"""Graph Search - Neo4j for relationship queries"""
from neo4j import GraphDatabase
from typing import List, Dict, Any
from app import config

_driver = None

def get_driver():
    """Connect to Neo4j"""
    global _driver
    if not _driver:
        try: _driver = GraphDatabase.driver(config.NEO4J_URI, auth=(config.NEO4J_USER, config.NEO4J_PASSWORD))
        except: return None
    return _driver

def run_query(cypher: str, params: dict = None) -> List[Dict]:
    """Execute Cypher query"""
    d = get_driver()
    if not d: return []
    try:
        with d.session() as s: return [r.data() for r in s.run(cypher, params or {})]
    except: return []

def add_entity(name: str, etype: str, props: dict = None) -> List[Dict]:
    """Add node to graph"""
    return run_query(f"MERGE (n:{etype} {{name:$n}}) SET n+=$p RETURN n", {"n": name, "p": props or {}})

def add_relationship(from_n: str, to_n: str, rel: str) -> List[Dict]:
    """Add edge between nodes"""
    return run_query(f"MATCH (a),(b) WHERE a.name=$f AND b.name=$t MERGE (a)-[:{rel}]->(b)", {"f": from_n, "t": to_n})

def find_related(name: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Find connected entities"""
    return run_query("MATCH (n)-[r]-(x) WHERE n.name=$n RETURN n.name as entity, type(r) as relationship, x.name as related_entity LIMIT $l", {"n": name, "l": limit})

def search_by_keyword(kw: str) -> List[Dict]:
    """Find entities by name"""
    return run_query("MATCH (n) WHERE toLower(n.name) CONTAINS toLower($k) RETURN n.name as name LIMIT 5", {"k": kw})

def get_context_for_query(keywords: List[str]) -> List[Dict[str, Any]]:
    """Get graph context for keywords (used by RAG)"""
    ctx = []
    for kw in keywords[:3]:
        for e in search_by_keyword(kw):
            ctx.extend(find_related(e['name'], 3))
    return ctx[:10]
