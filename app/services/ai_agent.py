"""AI Agent - Orchestrates RAG pipeline with autonomous decisions"""
import ollama
from typing import Dict, List, Tuple, Any
from app import config
from app.services.nlp_helper import preprocess_query
from app.services.vector_search import search_similar
from app.services.graph_search import get_context_for_query

def call_llm(prompt: str, context: str = "") -> str:
    """Call Ollama LLM"""
    try:
        msg = f"You are a helpful support assistant.\nContext: {context}\nQuery: {prompt}" if context else prompt
        return ollama.chat(model=config.OLLAMA_MODEL, messages=[{"role": "user", "content": msg}])['message']['content']
    except Exception as e: return f"AI error: {e}"

def decide_strategy(info: Dict) -> str:
    """Agent decides: vector, graph, hybrid, or direct"""
    if info['intent'] == 'complaint' or info['entities']: return 'hybrid'
    if info['intent'] == 'question': return 'vector'
    return 'direct' if len(info['keywords']) < 2 else 'vector'

def retrieve_context(query: str, info: Dict, strategy: str) -> Tuple[str, List[Dict]]:
    """Get relevant context from vector/graph stores"""
    ctx, src = [], []
    if strategy in ['vector', 'hybrid']:
        for d in search_similar(query, 3):
            ctx.append(d['content']); src.append({'type': 'vector', 'id': d['id']})
    if strategy in ['graph', 'hybrid']:
        for i in get_context_for_query(info['keywords']):
            ctx.append(f"{i['entity']} → {i['related_entity']}"); src.append({'type': 'graph'})
    return "\n".join(ctx), src

def should_escalate(info: Dict) -> bool:
    """Check if needs human attention"""
    if info['sentiment'] == 'negative' and info['intent'] == 'complaint': return True
    return any(w in info['original'].lower() for w in ['urgent','manager','lawyer'])

def process_query(query: str) -> Dict[str, Any]:
    """Main pipeline: NLP → Strategy → Retrieve → LLM → Response"""
    info = preprocess_query(query)
    strategy = decide_strategy(info)
    context, sources = retrieve_context(query, info, strategy)
    return {
        'answer': call_llm(query, context), 'sources': sources,
        'metadata': {'intent': info['intent'], 'sentiment': info['sentiment'],
                     'entities_found': len(info['entities']), 'strategy_used': strategy,
                     'escalate_to_human': should_escalate(info)}
    }
