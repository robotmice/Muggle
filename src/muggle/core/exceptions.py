class MuggleError(Exception):
    """Base exception for all muggle-related errors."""
    pass

class PromptNotFoundError(MuggleError):
    """Raised when a requested prompt cannot be found in the registry."""
    def __init__(self, prompt_name: str, prompt_type: str):
        self.prompt_name = prompt_name
        self.prompt_type = prompt_type
        super().__init__(f"Prompt '{prompt_name}' of type '{prompt_type}' not found.")
