"""NLP Helper - Intent, Sentiment, Entity extraction"""
import re
from typing import List, Dict, Any

STOP_WORDS = {'a','an','the','is','are','was','were','be','have','has','had','do','does','did','will',
'would','could','should','to','of','in','for','on','with','at','by','from','and','but','if','or',
'this','that','i','me','my','we','you','your','they','them','what','which','who','please','help','want'}

# Regex patterns for entity extraction
ENTITY_PATTERNS = {
    'EMAIL': r'\b[\w.+-]+@[\w.-]+\.\w+\b',
    'PHONE': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
    'ORDER_ID': r'#?\d{5,10}\b',
    'MONEY': r'\$\d+(?:\.\d{2})?',
}

def extract_keywords(text: str) -> List[str]:
    """Get important words from text"""
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    return list(set(w for w in words if w not in STOP_WORDS))[:10]

def extract_entities(text: str) -> List[Dict[str, str]]:
    """Find emails, phones, order IDs, money amounts"""
    entities = []
    for etype, pattern in ENTITY_PATTERNS.items():
        for match in re.findall(pattern, text, re.I):
            entities.append({'type': etype, 'value': match})
    return entities

def get_sentiment(text: str) -> str:
    """Simple positive/negative/neutral detection"""
    t = text.lower()
    neg = ['angry','upset','frustrated','terrible','broken','failed','hate','refund','complaint','awful','bad']
    pos = ['great','love','excellent','amazing','perfect','thank','happy','good','best','awesome','helpful']
    n, p = sum(w in t for w in neg), sum(w in t for w in pos)
    return "negative" if n > p else ("positive" if p > n else "neutral")

def classify_intent(text: str) -> str:
    """Detect: question, request, complaint, or general"""
    t = text.lower()
    if '?' in text or any(w in t for w in ['how','what','when','where','why']): return "question"
    if any(w in t for w in ['refund','return','cancel','replace']): return "request"
    if any(w in t for w in ['problem','issue','broken','not working']): return "complaint"
    return "general"

def preprocess_query(text: str) -> Dict[str, Any]:
    """Full NLP pipeline - returns all extracted features"""
    return {
        "original": text, "keywords": extract_keywords(text),
        "entities": extract_entities(text), "intent": classify_intent(text),
        "sentiment": get_sentiment(text)
    }
