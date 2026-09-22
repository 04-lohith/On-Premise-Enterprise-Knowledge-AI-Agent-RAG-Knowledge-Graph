"""Celery Tasks - Background jobs"""
from celery import Celery
from app import config

celery_app = Celery('support', broker=config.REDIS_URL, backend=config.REDIS_URL)
celery_app.conf.update(task_serializer='json', accept_content=['json'], broker_connection_retry_on_startup=True)

@celery_app.task
def ingest_document_task(content: str, metadata: dict = None):
    """Add document to vector store + knowledge graph"""
    from app.services.vector_search import add_document
    from app.services.nlp_helper import extract_keywords
    from app.services.graph_search import add_entity, add_relationship
    
    doc_id = add_document(content, metadata=metadata)
    for kw in extract_keywords(content):
        add_entity(kw, 'Concept')
        if doc_id: add_relationship(doc_id, kw, 'MENTIONS')
    return {'status': 'success', 'doc_id': doc_id}
