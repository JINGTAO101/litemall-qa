from pathlib import Path
import yaml

_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config"/"local.yaml"

def load_config():
    with _CONFIG_PATH.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)