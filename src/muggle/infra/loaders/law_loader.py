import logging
import re
import hashlib
import argparse
from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
from muggle.infra.config import cfg
from muggle.infra.registry.vector import VectorStoreManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ARTICLE_PATTERN = re.compile(r'\*\*(第[一二三四五六七八九十百]+条)\*\*')


class LawLoader:
    SUPPORTED_LANGS = {"zh-CN", "en-US"}

    def __init__(self, vector_store: VectorStoreManager, lang_tag: str = "zh-CN"):
        if lang_tag not in self.SUPPORTED_LANGS:
            raise ValueError(f"Unsupported lang_tag '{lang_tag}'. Supported: {self.SUPPORTED_LANGS}")
        self.vs = vector_store
        self.lang_tag = lang_tag
        self.segment_splitter = RecursiveCharacterTextSplitter(
            chunk_size=300,
            chunk_overlap=20
        )

    def _generate_id(self, text: str) -> str:
        return hashlib.md5(text.encode("utf-8")).hexdigest()

    def load_from_file(self, file_path: str):
        logger.info(f"Loading law document from {file_path}")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            return

        # Remove source attribution line at the bottom
        content = re.sub(r'\n\*来源：[^*]+\*\s*$', '', content)

        # Remove trailing --- separators and whitespace
        content = re.sub(r'\n---\n*$', '', content)

        # Split into sections on ## headers
        chapter_blocks = re.split(r'\n(?=## )', content)

        records: List[Dict[str, Any]] = []

        for block in chapter_blocks:
            block = block.strip()
            if not block or not block.startswith('## '):
                continue

            # Extract chapter name (text after ## on the first line)
            first_line_end = block.find('\n')
            chapter_name = block[3:first_line_end].strip() if first_line_end != -1 else block[3:].strip()

            # Skip TOC and non-content sections
            if chapter_name == '目录':
                continue

            # Split chapter body into articles
            article_matches = list(ARTICLE_PATTERN.finditer(block))
            if not article_matches:
                continue

            for i, match in enumerate(article_matches):
                article_number = match.group(1)
                start = match.start()
                end = article_matches[i + 1].start() if i + 1 < len(article_matches) else len(block)
                article_body = block[start:end].strip()

                header = f"{chapter_name} — {article_number}"
                full_text = f"{header}\n{article_body}"

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

                if len(full_text) > 200:
                    chunks = self.segment_splitter.split_text(article_body)
                    for chunk in chunks:
                        segment_text = f"{header}\n{chunk}"
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
            self.vs.upsert(records)
            logger.info(f"Successfully upserted {len(records)} records into Milvus.")
        else:
            logger.warning("No records found to ingest.")


def run_loader():
    parser = argparse.ArgumentParser(description="Load Social Insurance Law markdown into Milvus.")
    parser.add_argument("--file", default="中华人民共和国社会保险法.md",
                        help="Path to the law markdown file.")
    parser.add_argument("--lang", default="zh-CN", choices=["zh-CN", "en-US"],
                        help="Language tag for the law content.")
    args = parser.parse_args()

    params = cfg.get_vector_store_params()
    vs_manager = VectorStoreManager(collection_name=params["law_collection_name"])
    loader = LawLoader(vs_manager, lang_tag=args.lang)
    loader.load_from_file(args.file)
