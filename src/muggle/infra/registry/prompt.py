from importlib import resources
from importlib.resources.abc import Traversable

import jinja2

from muggle.core.exceptions import PromptNotFoundError
from muggle.shared.utils import parse_frontmatter


class PromptRegistry:
    prompts_dir: Traversable

    def __init__(self, prompts_dir: str = None):
        if prompts_dir:
            self.prompts_dir = resources.files(prompts_dir)
        else:
            # Default to internal package resources
            self.prompts_dir = resources.files("muggle.infra.prompts")

        self._cache = {}  # { (type, name): {metadata, template} }
        self._jinja_env = jinja2.Environment()

    def _get_prompt_path(self, prompt_type: str, prompt_name: str):
        # Works for both Path and importlib Traversable
        return self.prompts_dir / prompt_type / f"{prompt_name}.md"

    def _load_prompt(self, prompt_type: str, prompt_name: str) -> dict:
        cache_key = (prompt_type, prompt_name)
        if cache_key not in self._cache:
            path = self._get_prompt_path(prompt_type, prompt_name)
            if not path.is_file():
                raise PromptNotFoundError(prompt_name=prompt_name, prompt_type=prompt_type)

            content = path.read_text(encoding="utf-8")

            metadata, template_str = parse_frontmatter(content)
            self._cache[cache_key] = {
                "metadata": metadata,
                "template": self._jinja_env.from_string(template_str)
            }

        return self._cache[cache_key]

    def get_system_prompt(self, prompt_name: str, variables: dict = None) -> str:
        """Retrieve and render a system prompt."""
        prompt_data = self._load_prompt("system", prompt_name)
        return prompt_data["template"].render(**(variables or {}))

    def get_user_prompt(self, prompt_name: str, variables: dict = None) -> str:
        """Retrieve and render a user prompt."""
        prompt_data = self._load_prompt("user", prompt_name)
        return prompt_data["template"].render(**(variables or {}))
