import os
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

import chromadb
from sentence_transformers import SentenceTransformer
from app.core.config import settings

_client = None
_collection = None
_embedding_model = None

def load_vector_store():
    """يُستدعى مرة واحدة فقط عند إقلاع السيرفر (lifespan)."""
    global _client, _collection, _embedding_model
    _client = chromadb.PersistentClient(path=settings.vector_store_path)
    _collection = _client.get_collection(settings.collection_name)
    _embedding_model = SentenceTransformer(settings.embedding_model)

def retrieve(query: str, n_results: int = 5) -> list[dict]:
    if _collection is None:
        raise RuntimeError("Vector store not loaded. Call load_vector_store() first.")

    results = _collection.query(query_texts=[query], n_results=n_results)
    retrieved = [
        {"text": doc, "source": meta["source"]}
        for doc, meta in zip(results["documents"][0], results["metadatas"][0])
    ]

    # Fallback: تأكد من وجود مصدر الشكاوى للأسئلة المتعلقة بالشكاوى
    if "شكو" in query and not any("شكاوي" in r["source"] for r in retrieved):
        extra = _collection.query(query_texts=[query], n_results=10)
        for doc, meta in zip(extra["documents"][0], extra["metadatas"][0]):
            if "شكاوي" in meta["source"]:
                retrieved.append({"text": doc, "source": meta["source"]})
                break

    return retrieved