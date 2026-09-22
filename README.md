# 🧠 On-Premise Enterprise Knowledge AI Agent

> A fully **on-premise**, production-ready AI agent that answers questions about your organization's private knowledge base — powered by RAG (Retrieval-Augmented Generation), a Neo4j Knowledge Graph, ChromaDB vector search, and a locally-hosted LLM via Ollama.

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-lightgrey?logo=flask)](https://flask.palletsprojects.com/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-0.4.18-orange)](https://www.trychroma.com/)
[![Neo4j](https://img.shields.io/badge/Neo4j-5.x-blue?logo=neo4j)](https://neo4j.com/)
[![Ollama](https://img.shields.io/badge/Ollama-LLaMA3.2-green)](https://ollama.com/)
[![Celery](https://img.shields.io/badge/Celery-5.3-brightgreen?logo=celery)](https://docs.celeryq.dev/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

---

## 📌 What Is This?

This project is a **self-hosted, privacy-first AI knowledge agent** built for enterprises that cannot send their internal data to external cloud services like ChatGPT or Google Gemini.

It is pre-loaded with knowledge about **AI Intime** — an enterprise knowledge management product by **Vegam Solutions Inc.** — and demonstrates how organizations can deploy an intelligent Q&A assistant that:

- Understands natural language questions
- Searches their **private document repository** using semantic (vector) search
- Traverses a **knowledge graph** to understand entity relationships
- Generates accurate, context-grounded answers using a **local LLM running on your own hardware**
- Escalates sensitive or urgent queries to human agents

**No data ever leaves your infrastructure.**

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🔍 **Semantic Vector Search** | ChromaDB stores document embeddings and retrieves results by meaning, not just keywords |
| 🔗 **Knowledge Graph** | Neo4j models entities (products, features, contacts) and their relationships for context-rich answers |
| 🤖 **Agentic AI Pipeline** | The AI Agent autonomously decides whether to use vector search, graph search, or both based on query type |
| 🧠 **NLP Pre-processing** | Every query is analyzed for intent, sentiment, named entities (emails, phone numbers, order IDs), and keywords before retrieval |
| 💬 **Local LLM via Ollama** | All language generation runs on-premise using LLaMA 3.2 (or any Ollama-compatible model) — no API keys required |
| ⚡ **Async Document Ingestion** | Celery + Redis process document uploads in the background; new documents are simultaneously indexed in the vector store and the knowledge graph |
| 🚨 **Escalation Detection** | Queries with negative sentiment, complaints, or urgent keywords are automatically flagged for human review |
| 🐳 **One-Command Deployment** | The entire stack (Flask, Redis, ChromaDB, Neo4j) runs with a single `docker-compose up` |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER / Browser                           │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP
                             ▼
┌────────────────────────────────────────────────────────────────┐
│                     Flask Web App (Port 5000)                  │
│                                                                │
│  GET  /          → Serve chat UI (chat.html + app.js)          │
│  POST /ask       → Process question through AI pipeline        │
│  POST /ingest    → Queue document for background ingestion     │
│  POST /search    → Direct vector similarity search             │
│  GET  /health    → Service health check                        │
└────────────────────────────┬───────────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────────┐
│                        AI Agent                                │
│                     (app/services/ai_agent.py)                 │
│                                                                │
│  1. NLP Pre-process  ──►  Extract keywords, intent, sentiment, │
│     (nlp_helper.py)        named entities                      │
│                                                                │
│  2. Strategy Decision ──►  vector | graph | hybrid | direct    │
│                                                                │
│  3. Context Retrieval ──►  ChromaDB (semantic docs)            │
│                        └►  Neo4j (entity relationships)        │
│                                                                │
│  4. LLM Generation   ──►  Ollama (LLaMA 3.2 on-premise)        │
│                                                                │
│  5. Response + Metadata (intent, sentiment, escalation flag)   │
└────────────────────────────────────────────────────────────────┘
                             │
              ┌──────────────┴──────────────┐
              ▼                             ▼
┌─────────────────────┐       ┌─────────────────────────┐
│  ChromaDB           │       │  Neo4j Knowledge Graph  │
│  (Vector Store)     │       │  (Graph Database)       │
│  Port 8001          │       │  Port 7474 / 7687       │
│                     │       │                         │
│  - Stores document  │       │  - Entities: Products,  │
│    embeddings       │       │    Features, Contacts   │
│  - Semantic search  │       │  - Relationships between│
│  - Persistent local │       │    entities (Cypher)    │
│    storage          │       │                         │
└─────────────────────┘       └─────────────────────────┘

              ┌───────────────────────────────────────┐
              │         Celery Background Worker       │
              │                                        │
              │  POST /ingest → Celery Task:           │
              │    1. add_document() → ChromaDB        │
              │    2. extract_keywords() → NLP         │
              │    3. add_entity() + add_relationship()│
              │       → Neo4j                          │
              └──────────────┬────────────────────────┘
                             │ Broker
                             ▼
                    ┌──────────────────┐
                    │  Redis (Port 6379)│
                    │  Task Queue &    │
                    │  Result Backend  │
                    └──────────────────┘

              ┌───────────────────────────────────────┐
              │         Ollama (runs on HOST machine) │
              │         Port 11434                    │
              │                                       │
              │  - Model: llama3.2 (default)          │
              │  - Accessed via host.docker.internal  │
              │  - Runs natively for GPU performance  │
              └───────────────────────────────────────┘
```

---

## 🧬 How the AI Agent Works — Step by Step

When a user submits a question through the chat interface, the following pipeline executes:

### Step 1 — NLP Pre-processing (`nlp_helper.py`)
The raw query is analyzed to extract:
- **Keywords** — stop words removed; top 10 meaningful words extracted
- **Named Entities** — emails, phone numbers, order IDs (`#12345`), monetary amounts (`$99.99`) via regex
- **Intent Classification** — `question` / `request` / `complaint` / `general`
- **Sentiment Detection** — `positive` / `negative` / `neutral` based on keyword matching

### Step 2 — Strategy Decision (`ai_agent.py → decide_strategy()`)
The agent picks the most appropriate retrieval strategy:

| Condition | Strategy |
|---|---|
| Intent is `complaint` OR named entities found | `hybrid` (vector + graph) |
| Intent is `question` | `vector` |
| Fewer than 2 keywords | `direct` (LLM only, no retrieval) |
| Otherwise | `vector` |

### Step 3 — Context Retrieval
- **Vector Search** (`vector_search.py`): Queries ChromaDB for the top-3 semantically similar documents using `chromadb.PersistentClient`.
- **Graph Search** (`graph_search.py`): Searches Neo4j for entities matching the query keywords, then traverses relationships to pull in connected context (e.g., `AI Intime → HAS_FEATURE → Audit Trail`).

### Step 4 — LLM Response Generation
All retrieved context is concatenated and sent to **Ollama** as a prompt. The LLM generates a grounded, natural-language answer. If context is empty (direct strategy), the LLM responds from its base knowledge.

### Step 5 — Response Metadata & Escalation
The API response includes:
```json
{
  "answer": "AI Intime is an enterprise knowledge platform...",
  "sources": [{ "type": "vector", "id": "aiintime_doc_1" }],
  "metadata": {
    "intent": "question",
    "sentiment": "neutral",
    "entities_found": 0,
    "strategy_used": "vector",
    "escalate_to_human": false
  }
}
```
If `escalate_to_human` is `true`, the chat UI displays a prominent warning banner.

---

## 📁 Project Structure

```
On-Premise-Enterprise-Knowledge-AI-Agent/
│
├── app/                            # Core Flask application
│   ├── __init__.py
│   ├── app.py                      # App factory: creates Flask app, registers blueprints
│   ├── config.py                   # All configuration loaded from environment variables
│   │
│   ├── routes/
│   │   └── main.py                 # All REST API endpoints (/ask, /ingest, /search, /health)
│   │
│   ├── services/
│   │   ├── ai_agent.py             # 🧠 Core AI pipeline: NLP → Strategy → Retrieval → LLM
│   │   ├── vector_search.py        # 📚 ChromaDB wrapper: add, search, count documents
│   │   ├── graph_search.py         # 🔗 Neo4j wrapper: add entities, relationships, search
│   │   └── nlp_helper.py           # 📝 Intent, sentiment, entity extraction, keyword parsing
│   │
│   └── tasks/
│       └── jobs.py                 # ⚡ Celery task: async document ingestion into vector + graph
│
├── templates/
│   └── chat.html                   # Minimal Jinja2 HTML shell; JS/CSS loaded from /static
│
├── static/
│   ├── app.js                      # Frontend chat logic: send messages, render responses, XSS-safe
│   └── style.css                   # Chat UI styling
│
├── scripts/
│   └── setup.py                    # One-time database seeder: loads AI Intime docs into ChromaDB
│                                   # and builds the Neo4j knowledge graph
│
├── data/
│   └── sample_docs/                # (Optional) Place additional documents here for ingestion
│
├── Dockerfile                      # Python 3.11-slim image for the Flask app and Celery worker
├── docker-compose.yml              # Orchestrates: web, celery, redis, chromadb, neo4j
├── requirements.txt                # All Python dependencies with pinned versions
├── .env.example                    # Template for environment variables — copy to .env
└── .gitignore
```

---

## 🚀 Getting Started

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (includes Docker Compose)
- [Ollama](https://ollama.com/download) installed and running **natively on your host machine** (not inside Docker, for GPU access and better performance)
- Git

> **Why Ollama runs on the host, not in Docker?**
> Running Ollama natively gives it direct access to your GPU (NVIDIA/Apple Silicon). The Flask app connects to it via `host.docker.internal:11434`, which Docker resolves to your local machine automatically.

---

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/On-Premise-Enterprise-Knowledge-AI-Agent.git
cd On-Premise-Enterprise-Knowledge-AI-Agent
```

### 2. Configure Environment Variables

```bash
# Copy the example file
cp .env.example .env   # macOS / Linux
copy .env.example .env # Windows
```

Edit `.env` and update any values as needed (see [Configuration](#-configuration) below).

### 3. Pull the LLM Model (First Time Only)

Make sure Ollama is running, then pull the model:

```bash
ollama pull llama3.2
```

> You can substitute any Ollama-compatible model (e.g., `mistral`, `gemma2`, `phi3`). Update `OLLAMA_MODEL` in your `.env` accordingly.

### 4. Start All Services

```bash
docker-compose up -d
```

This starts:
| Container | Service | Port |
|---|---|---|
| `web` | Flask API | `5000` |
| `celery` | Background worker | — |
| `redis` | Task broker + result backend | `6379` |
| `chromadb` | Vector database | `8001` |
| `neo4j` | Graph database | `7474`, `7687` |

Wait ~30 seconds for all services to become healthy.

### 5. Seed the Knowledge Base

Run the one-time setup script to populate ChromaDB and Neo4j with the AI Intime knowledge documents:

```bash
docker-compose exec web python scripts/setup.py
```

This will:
- Load **16 curated AI Intime support documents** into ChromaDB (product overview, features, security, pricing, FAQs, etc.)
- Create **21 entities** in the Neo4j knowledge graph (Products, Features, Locations, Services, Contacts)
- Create **18 named relationships** (`HAS_FEATURE`, `DEVELOPED_BY`, `SUPPORTS`, `OFFERS`, `CONTACT_VIA`, etc.)

### 6. Open the App

Navigate to: **[http://localhost:5000](http://localhost:5000)**

You should see the chat interface. Try asking:
- *"What is AI Intime?"*
- *"How does AI Intime handle data security?"*
- *"How long does implementation take?"*
- *"What makes AI Intime different from ChatGPT?"*

---

## 🔌 API Reference

All endpoints accept and return JSON.

### `GET /`
Returns the chat web interface (HTML).

---

### `POST /ask`
Submit a natural language question to the AI agent.

**Request:**
```bash
curl -X POST http://localhost:5000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What deployment options does AI Intime support?"}'
```

**Response:**
```json
{
  "answer": "AI Intime supports both on-premise and cloud deployment...",
  "sources": [
    { "type": "vector", "id": "aiintime_doc_10" },
    { "type": "graph" }
  ],
  "metadata": {
    "intent": "question",
    "sentiment": "neutral",
    "entities_found": 0,
    "strategy_used": "hybrid",
    "escalate_to_human": false
  }
}
```

---

### `POST /ingest`
Add a new document to the knowledge base. Processed asynchronously via Celery — the document is indexed into both ChromaDB and Neo4j.

**Request:**
```bash
curl -X POST http://localhost:5000/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "content": "AI Intime now supports Microsoft SharePoint integration for seamless document sync.",
    "metadata": { "category": "features", "topic": "integrations", "source": "release-notes" }
  }'
```

**Response (202 Accepted):**
```json
{
  "status": "processing",
  "task_id": "b3f2a1c4-7e8d-4f9a-..."
}
```

---

### `POST /search`
Perform a direct semantic similarity search against the vector store (bypasses the AI agent).

**Request:**
```bash
curl -X POST http://localhost:5000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "enterprise data privacy", "limit": 5}'
```

**Response:**
```json
{
  "results": [
    {
      "id": "aiintime_doc_9",
      "content": "AI Intime is designed for enterprise security...",
      "metadata": { "category": "security", "topic": "privacy" }
    }
  ]
}
```

---

### `GET /health`
Service liveness check.

```bash
curl http://localhost:5000/health
# {"status": "healthy"}
```

---

## 📊 Service Admin UIs

| Service | URL | Purpose |
|---|---|---|
| **Chat App** | http://localhost:5000 | Main AI chat interface |
| **Neo4j Browser** | http://localhost:7474 | Visualize and query the knowledge graph |
| **ChromaDB API** | http://localhost:8001 | Inspect vector collections |

**Neo4j Default Credentials:** `neo4j` / `password123` (set via `NEO4J_AUTH` in `docker-compose.yml`)

To explore the knowledge graph in Neo4j Browser:
```cypher
// See all entities and relationships
MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 50

// Find everything related to AI Intime
MATCH (n {name: "AI Intime"})-[r]->(m) RETURN n, r, m
```

---

## 🔧 Configuration

All settings are loaded from the `.env` file via `python-dotenv`. Here are all available variables:

```env
# ── Flask ──────────────────────────────────────────────────────
FLASK_APP=app.app
FLASK_ENV=development          # Use 'production' for live deployments
SECRET_KEY=your-secret-key-change-this

# ── Redis (Celery Broker) ───────────────────────────────────────
REDIS_URL=redis://redis:6379/0

# ── Neo4j (Knowledge Graph) ─────────────────────────────────────
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password123     # Change this in production!

# ── Ollama (Local LLM) ──────────────────────────────────────────
# host.docker.internal routes from inside Docker to your host machine
OLLAMA_HOST=http://host.docker.internal:11434
OLLAMA_MODEL=llama3.2          # Any installed Ollama model works here

# ── ChromaDB ────────────────────────────────────────────────────
# Uses PersistentClient at /app/chroma_data inside the container
# No host/port config needed — data is persisted via Docker volume
```

---

## 🛠️ Development (Without Docker)

If you prefer to run the stack outside of Docker:

### 1. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows

pip install -r requirements.txt
```

### 2. Start supporting services

You must have Redis, Neo4j, and Ollama running locally. Update `.env` to point to `localhost` instead of Docker service names:

```env
REDIS_URL=redis://localhost:6379/0
NEO4J_URI=bolt://localhost:7687
OLLAMA_HOST=http://localhost:11434
```

### 3. Run the Flask development server

```bash
flask run
```

### 4. Run the Celery worker (separate terminal)

```bash
celery -A app.tasks.jobs worker --loglevel=info
```

### 5. Seed the database

```bash
python scripts/setup.py
```

---

## 📦 Dependencies

| Package | Version | Purpose |
|---|---|---|
| `flask` | 3.0.0 | Web framework |
| `flask-cors` | 4.0.0 | Cross-origin request support |
| `celery` | 5.3.4 | Distributed task queue |
| `redis` | 5.0.1 | Celery broker and result backend |
| `chromadb` | 0.4.18 | Vector database for semantic search |
| `neo4j` | 5.14.1 | Graph database driver |
| `ollama` | 0.1.6 | Python client for local Ollama LLM |
| `python-dotenv` | 1.0.0 | Load `.env` configuration |
| `requests` | 2.31.0 | HTTP client utilities |
| `numpy` | <2.0 | Required for ChromaDB compatibility |

---

## 🔒 Security Notes

- **Data Privacy**: All data stays within your own infrastructure. No external API calls are made for inference — Ollama runs entirely on your machine.
- **Secret Key**: Change `SECRET_KEY` in `.env` before any production deployment.
- **Neo4j Password**: The default `password123` is for development only. Set a strong password via `NEO4J_AUTH` in `docker-compose.yml` and `NEO4J_PASSWORD` in `.env`.
- **XSS Protection**: The frontend (`app.js`) sanitizes all user and AI-generated content before injecting it into the DOM.
- **CORS**: Enabled globally via `flask-cors`. Restrict origins in production if the API is exposed externally.

---

## 🧩 Extending the System

### Adding New Knowledge Documents
Use the `/ingest` API endpoint or add entries to the `aiintime_docs` list in `scripts/setup.py` and re-run the setup.

### Changing the LLM Model
Update `OLLAMA_MODEL` in `.env` to any model you have pulled via `ollama pull <model-name>`.

### Adding New Entity Types to the Knowledge Graph
Edit the `entities` and `relationships` lists in `scripts/setup.py`. Entities use any label string (e.g., `"Product"`, `"Feature"`, `"Contact"`), and relationships use Cypher-style verbs (e.g., `"HAS_FEATURE"`, `"CONTACT_VIA"`).

### Customizing Intent / Sentiment Detection
Extend the keyword lists in `app/services/nlp_helper.py`. For production use, consider replacing the regex-based NLP with a lightweight model like `spaCy` or `transformers`.

---

## 🙋 FAQ

**Q: Do I need a GPU?**
Ollama runs on CPU as well, but response times will be slower. For production, a GPU (NVIDIA with CUDA, or Apple Silicon) is strongly recommended.

**Q: Can I use a different LLM?**
Yes. Any model available on [Ollama's model library](https://ollama.com/library) (Mistral, Gemma 2, Phi-3, etc.) works. Just `ollama pull <model>` and update `OLLAMA_MODEL` in `.env`.

**Q: How do I add my company's documents?**
Send `POST /ingest` requests with your document content and metadata. For bulk ingestion, write a script that loops through your files and calls the API.

**Q: Where is ChromaDB data stored?**
Inside the container at `/app/chroma_data`, persisted by the `chroma_data` Docker volume. It survives container restarts unless you run `docker-compose down -v`.

**Q: Why isn't Ollama in `docker-compose.yml`?**
Ollama is deliberately excluded from Docker to allow it to access your host's GPU directly. GPU passthrough inside Docker requires additional configuration and often performs worse than native execution.

---

## 📝 License

This project is licensed under the **MIT License** — free to use, modify, and distribute.

---

<div align="center">
  <sub>Built with ❤️ to demonstrate on-premise RAG and Agentic AI for enterprise knowledge management.</sub><br/>
  <sub>Powered by <a href="https://ollama.com">Ollama</a> · <a href="https://www.trychroma.com/">ChromaDB</a> · <a href="https://neo4j.com/">Neo4j</a> · <a href="https://flask.palletsprojects.com/">Flask</a></sub>
</div>
