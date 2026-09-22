"""API Routes - Flask endpoints"""
from flask import Blueprint, request, jsonify, render_template
from app.services.ai_agent import process_query
from app.services.vector_search import search_similar
from app.tasks.jobs import ingest_document_task

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home(): return render_template('chat.html')

@main_bp.route('/health')
def health(): return jsonify({'status': 'healthy'}), 200

@main_bp.route('/ask', methods=['POST'])
def ask():
    """Main endpoint - Ask a question"""
    q = request.get_json().get('question', '')
    if not q: return jsonify({'error': 'No question'}), 400
    return jsonify(process_query(q)), 200

@main_bp.route('/ingest', methods=['POST'])
def ingest():
    """Add document to knowledge base"""
    data = request.get_json()
    if not data.get('content'): return jsonify({'error': 'No content'}), 400
    task = ingest_document_task.delay(data['content'], data.get('metadata', {}))
    return jsonify({'status': 'processing', 'task_id': task.id}), 202

@main_bp.route('/search', methods=['POST'])
def search():
    """Direct vector search"""
    data = request.get_json()
    return jsonify({'results': search_similar(data.get('query', ''), data.get('limit', 3))}), 200
