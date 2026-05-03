from flask import Blueprint, jsonify, current_app

monitor_bp = Blueprint('monitoring', __name__)

@monitor_bp.route('/health', methods=['GET'])
def health():
    processor = getattr(current_app, 'processor', None)
    
    if not processor:
        return jsonify({
            "status": "unhealthy",
            "errors": ["Processor not found in application context"]
        }), 503
        
    if not processor.is_initialized():
        return jsonify({
            "status": "unhealthy",
            "errors": [processor.last_error or "Processor is not initialized"]
        }), 503
        
    return jsonify({"status": "healthy"}), 200
