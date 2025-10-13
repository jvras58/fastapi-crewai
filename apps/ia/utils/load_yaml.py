import yaml


def load_agent_prompt(yaml_path: str) -> dict:
    """Carrega o prompt do agente a partir de um arquivo YAML."""
    with open(yaml_path, encoding='utf-8') as f:
        return yaml.safe_load(f)
