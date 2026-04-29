from flask import Flask

def register_blueprints(app: Flask):
    """Register all blueprints with the Flask application."""
    from muggle.blueprints.chat import chat_bp
    from muggle.blueprints.monitoring import monitor_bp
    
    app.register_blueprint(chat_bp)
    app.register_blueprint(monitor_bp)
