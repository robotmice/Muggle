import unittest
import os
import shutil
from pathlib import Path
from muggle.utils import parse_frontmatter
from muggle.registry import PromptRegistry

class TestPromptRegistry(unittest.TestCase):
    def setUp(self):
        # Create a temporary prompts directory
        self.test_dir = Path("tests/temp_prompts")
        self.test_dir.mkdir(parents=True, exist_ok=True)
        (self.test_dir / "system").mkdir(exist_ok=True)
        (self.test_dir / "user").mkdir(exist_ok=True)

    def tearDown(self):
        # Cleanup temporary directory
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_parse_frontmatter(self):
        content = "---\ntype: system\nname: test\n---\nHello {{name}}"
        metadata, template = parse_frontmatter(content)
        self.assertEqual(metadata["type"], "system")
        self.assertEqual(metadata["name"], "test")
        self.assertEqual(template, "Hello {{name}}")

    def test_parse_no_frontmatter(self):
        content = "Hello world"
        metadata, template = parse_frontmatter(content)
        self.assertEqual(metadata, {})
        self.assertEqual(template, "Hello world")

    def test_registry_discovery(self):
        # Create a test prompt
        prompt_path = self.test_dir / "system" / "hello.md"
        with open(prompt_path, "w") as f:
            f.write("Hello {{name}}")
        
        registry = PromptRegistry(str(self.test_dir))
        result = registry.get_system_prompt("hello", variables={"name": "World"})
        self.assertEqual(result, "Hello World")

    def test_registry_missing_prompt(self):
        registry = PromptRegistry(str(self.test_dir))
        with self.assertRaises(FileNotFoundError):
            registry.get_system_prompt("nonexistent")

    def test_jinja_logic(self):
        prompt_path = self.test_dir / "user" / "logic.md"
        with open(prompt_path, "w") as f:
            f.write("{% if True %}TRUE{% endif %}")
        
        registry = PromptRegistry(str(self.test_dir))
        result = registry.get_user_prompt("logic")
        self.assertEqual(result, "TRUE")

    def test_crispe_example_loads(self):
        # We need to point to the actual prompts dir for this or mock it
        # Let's mock it for the unit test
        (self.test_dir / "system" / "example.md").write_text("# CAPACITY\n{{ task_description }}")
        registry = PromptRegistry(str(self.test_dir))
        result = registry.get_system_prompt("example", variables={"task_description": "Test Task"})
        self.assertIn("Test Task", result)

if __name__ == '__main__':
    unittest.main()
