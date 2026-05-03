from pathlib import Path

from flask import Flask, send_from_directory

from muggle.blueprints import register_blueprints
from muggle.core.processor import ChatProcessor
from muggle.infra.config import cfg
from muggle.infra.registry import ModelRegistry, PromptRegistry
from muggle.shared.constants import STR_LLM_DEFAULT


def create_app():
    static_folder = Path(__file__).parent / "static"
    app = Flask(__name__, static_folder=str(static_folder))

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
    # Initialize Registries
    model_registry = ModelRegistry()
    
    prompt_params = cfg.get_prompts_params()
    prompt_path = Path(prompt_params["path"])
    if not prompt_path.exists():
        prompt_path = None
        
    prompt_registry = PromptRegistry(prompts_dir=prompt_path)
    
    # Register models from config
    llm_params = cfg.get_llm_params()
    model_registry.register(
        STR_LLM_DEFAULT,
        provider=llm_params["provider"],
        model_id=llm_params["model"],
        temperature=llm_params["temperature"],
        streaming=False
    )

    # Initialize Processor
    processor = ChatProcessor(
        registry=model_registry,
        prompt_registry=prompt_registry,
        model_alias=STR_LLM_DEFAULT
    )

    # Warm up (Graceful Startup)
    try:
        processor.warm_up()
    except Exception as e:
        app.logger.error(f"Failed to warm up ChatProcessor: {e}")

    # Attach to app for blueprint access
    app.processor = processor
    app.model_registry = model_registry
    app.prompt_registry = prompt_registry


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
