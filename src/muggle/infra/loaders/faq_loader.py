import logging
import hashlib
import argparse
from typing import List, Dict, Any
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from muggle.infra.registry.vector import VectorStoreManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FAQLoader:
    SUPPORTED_LANGS = {"zh-CN", "en-US"}

    def __init__(self, vector_store: VectorStoreManager, lang_tag: str = "zh-CN"):
        if lang_tag not in self.SUPPORTED_LANGS:
            raise ValueError(f"Unsupported lang_tag '{lang_tag}'. Supported: {self.SUPPORTED_LANGS}")
        self.vs = vector_store
        self.lang_tag = lang_tag
        # Headers to split on: H3 represents the question
        self.header_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[("###", "header")]
        )
        # Segments splitter: used if total length > 200
        self.segment_splitter = RecursiveCharacterTextSplitter(
            chunk_size=300, 
            chunk_overlap=20
        )

    def _generate_id(self, text: str) -> str:
        """Generate a deterministic ID based on the text content."""
        return hashlib.md5(text.encode("utf-8")).hexdigest()

    def load_from_file(self, file_path: str):
        """Parse markdown and ingest sections into Milvus."""
        logger.info(f"Loading FAQ from {file_path}")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            return
        
        sections = self.header_splitter.split_text(content)
        records = []
        
        for section in sections:
            header = section.metadata.get("header", "").strip()
            if not header:
                continue
            
            body = section.page_content.strip()
            full_text = f"{header}\n{body}"
            
            # 1. Always store full section
            # Pre-calculate embeddings (potentially slow, but reliable for this scale)
            header_vector = self.vs.embed_text(header)
            content_vector = self.vs.embed_text(full_text)
            
            records.append({
                "id": self._generate_id(full_text),
                "header_vector": header_vector,
                "content_vector": content_vector,
                "text": full_text,
                "header": header,
                "is_segment": False,
                "lang_tag": self.lang_tag,
            })
            
            # 2. If > 200 chars, store segments
            if len(full_text) > 200:
                chunks = self.segment_splitter.split_text(body)
                for chunk in chunks:
                    segment_text = f"{header}\n{chunk}"
                    # Avoid duplicate if splitting didn't actually change anything
                    if segment_text == full_text:
                        continue
                        
                    seg_content_vector = self.vs.embed_text(segment_text)
                    records.append({
                        "id": self._generate_id(segment_text),
                        "header_vector": header_vector,
                        "content_vector": seg_content_vector,
                        "text": segment_text,
                        "header": header,
                        "is_segment": True,
                        "lang_tag": self.lang_tag,
                    })
        
        if records:
            # Upsert for idempotency
            self.vs.upsert(records)
            logger.info(f"Successfully upserted {len(records)} records into Milvus.")
        else:
            logger.warning("No records found to ingest.")

def run_loader():
    parser = argparse.ArgumentParser(description="Load FAQ markdown into Milvus.")
    parser.add_argument("--file", default="aia_faq.md", help="Path to the FAQ markdown file.")
    parser.add_argument("--lang", default="zh-CN", choices=["zh-CN", "en-US"],
                        help="Language tag for the FAQ content.")
    args = parser.parse_args()

    vs_manager = VectorStoreManager()
    loader = FAQLoader(vs_manager, lang_tag=args.lang)
    loader.load_from_file(args.file)

if __name__ == "__main__":
    run_loader()
