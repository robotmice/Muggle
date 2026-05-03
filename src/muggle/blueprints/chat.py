import uuid
from flask import Blueprint, request, jsonify, current_app

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat', methods=['POST'])
def chat():
    data = request.json
    if not data or 'message' not in data:
        return jsonify({"error": "Missing 'message' field in request"}), 400
    
    user_message = data['message']
    thread_id = data.get('thread_id') or str(uuid.uuid4())
    
    # Retrieve the processor from current_app
    processor = getattr(current_app, 'processor', None)
    if not processor:
        return jsonify({"error": "LLM Processor not initialized"}), 500
        
    response_text = processor.get_response(user_message, thread_id=thread_id)
    
    return jsonify({
        "response": response_text,
        "thread_id": thread_id
    })
