import yaml
import re

def parse_frontmatter(content: str) -> tuple[dict, str]:
    """
    Parses YAML frontmatter from a string.
    Returns a tuple of (metadata_dict, remaining_content).
    """
    frontmatter_pattern = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)
    match = frontmatter_pattern.match(content)
    
    if match:
        yaml_content = match.group(1)
        remaining_content = content[match.end():]
        try:
            metadata = yaml.safe_load(yaml_content) or {}
            return metadata, remaining_content
        except yaml.YAMLError:
            return {}, content
    
    return {}, content
