import os
from flask import Flask, send_from_directory
from muggle.config import cfg
from muggle.ai import ChatProcessor
from muggle.registry import ModelRegistry
from muggle.blueprints import register_blueprints

def create_app():
    app = Flask(__name__, static_folder='static')
    
    # 1. Setup Components
    setup_components(app)
    
    # 2. Register Blueprints
    register_blueprints(app)
    
    # 3. Static routes
    @app.route('/')
    def index():
        return send_from_directory(app.static_folder, 'index.html')
        
    return app

def setup_components(app):
    """Initialize and attach core components to the Flask app."""
    # Initialize Registry
    registry = ModelRegistry()
    
    # Register models from config
    # Note: In a real app, this might iterate over multiple model definitions
    ai_params = cfg.get_ai_params()
    registry.register(
        "default", 
        provider=ai_params["provider"], 
        model_id=ai_params["model"],
        temperature=ai_params["temperature"]
    )
    
    # Initialize Processor
    processor = ChatProcessor(registry=registry, model_alias="default")
    
    # Warm up (Graceful Startup)
    try:
        processor.warm_up()
    except Exception as e:
        app.logger.error(f"Failed to warm up ChatProcessor: {e}")
    
    # Attach to app for blueprint access
    app.processor = processor
    app.registry = registry

def run():
    """CLI entrypoint to run the Flask application."""
    app = create_app()
    server_params = cfg.get_server_params()
    app.run(
        host=server_params["host"],
        port=server_params["port"],
        debug=server_params["debug"]
    )

if __name__ == '__main__':
    run()
