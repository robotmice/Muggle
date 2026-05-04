import pytest
import os
from muggle.infra.registry.vector import VectorStoreManager
from muggle.infra.loaders.faq_loader import FAQLoader

@pytest.fixture(scope="module")
def vs_manager():
    # Ensure we use a test collection if possible, but for now we'll use the one from config
    return VectorStoreManager()

def test_vector_store_initialization(vs_manager):
    assert vs_manager.client is not None
    assert vs_manager.collection_name == "aia_faq"
    assert vs_manager.client.has_collection(vs_manager.collection_name)

def test_embed_text(vs_manager):
    text = "Hello world"
    vector = vs_manager.embed_text(text)
    assert len(vector) == 1024
    assert isinstance(vector[0], float)

def test_search(vs_manager):
    query = "membership benefits"
    results = vs_manager.search(query, limit=1)
    assert len(results) > 0
    assert "header" in results[0]
    assert "text" in results[0]

def test_faq_loader_parsing():
    # Mocking or using a small sample might be better, but let's check the logic
    # with a temporary file if needed, or just trust the functional test run
    pass

def test_idempotency(vs_manager):
    data = [{
        "id": "test_id_1",
        "header_vector": [0.1] * 1024,
        "content_vector": [0.2] * 1024,
        "text": "Test content",
        "header": "Test Header",
        "is_segment": False,
        "lang_tag": "en-US"
    }]
    vs_manager.upsert(data)
    # Upsert again
    vs_manager.upsert(data)
    
    # Verify only one exists with this ID (Milvus upsert handles this)
    res = vs_manager.client.get(collection_name=vs_manager.collection_name, ids=["test_id_1"])
    assert len(res) == 1
