"""
Configuration - Environment variables for all services
Demonstrates: Environment-based configuration, 12-factor app principles
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Flask Configuration
SECRET_KEY: str = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Redis (for Celery task queue)
REDIS_URL: str = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Neo4j (Knowledge Graph)
NEO4J_URI: str = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
NEO4J_USER: str = os.getenv('NEO4J_USER', 'neo4j')
NEO4J_PASSWORD: str = os.getenv('NEO4J_PASSWORD', 'password123')

# Ollama LLM (runs natively on host, not in Docker for better performance)
OLLAMA_HOST: str = os.getenv('OLLAMA_HOST', 'http://host.docker.internal:11434')
OLLAMA_MODEL: str = os.getenv('OLLAMA_MODEL', 'llama3.2')

# Note: ChromaDB uses local PersistentClient at /app/chroma_data
# This avoids HTTP client tenant issues and provides persistence
