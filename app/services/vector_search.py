"""Vector Search - ChromaDB for semantic similarity"""
import chromadb, os
from typing import List, Dict, Optional, Any

CHROMA_PATH = "/app/chroma_data"
os.makedirs(CHROMA_PATH, exist_ok=True)
_client, _collection = None, None

def get_collection():
    """Get or create ChromaDB collection"""
    global _client, _collection
    if not _collection:
        try: _client = chromadb.PersistentClient(path=CHROMA_PATH)
        except: _client = chromadb.Client()
        _collection = _client.get_or_create_collection(name="support_docs")
    return _collection

def add_document(content: str, doc_id: str = None, metadata: dict = None) -> Optional[str]:
    """Add document to vector store (auto-generates embeddings)"""
    c = get_collection()
    doc_id = doc_id or f"doc_{c.count()}"
    try: c.add(ids=[doc_id], documents=[content], metadatas=[metadata or {}]); return doc_id
    except: return None

def search_similar(query: str, limit: int = 3) -> List[Dict[str, Any]]:
    """Find semantically similar documents"""
    c = get_collection()
    if not c or c.count() == 0: return []
    try:
        r = c.query(query_texts=[query], n_results=min(limit, c.count()))
        return [{'content': r['documents'][0][i], 'metadata': r['metadatas'][0][i], 'id': r['ids'][0][i]}
                for i in range(len(r['documents'][0]))] if r['documents'] else []
    except: return []

def get_document_count() -> int:
    """Total documents stored"""
    c = get_collection()
    return c.count() if c else 0
