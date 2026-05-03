import logging
from muggle.infra.registry.vector import VectorStoreManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_search():
    vs = VectorStoreManager()
    
    query = "How much are the AIA membership dues?"
    
    logger.info(f"Searching for: '{query}'")
    
    logger.info("--- Searching against 'header_vector' ---")
    header_results = vs.search(query, vector_field="header_vector", limit=3)
    for i, res in enumerate(header_results):
        logger.info(f"{i+1}. [Header: {res['header']}] (Segment: {res['is_segment']})")
        
    logger.info("--- Searching against 'content_vector' ---")
    content_results = vs.search(query, vector_field="content_vector", limit=3)
    for i, res in enumerate(content_results):
        logger.info(f"{i+1}. [Header: {res['header']}] (Segment: {res['is_segment']})")

if __name__ == "__main__":
    verify_search()
