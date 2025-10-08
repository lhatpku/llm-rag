import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

APP_CONFIG_FPATH = os.path.join(ROOT_DIR, "config", "app_config.yaml")
PROMPT_CONFIG_FPATH = os.path.join(ROOT_DIR, "config", "prompt_config.yaml")

OUTPUTS_DIR = os.path.join(ROOT_DIR, "outputs")

DATA_DIR = os.path.join(ROOT_DIR, "data")

DOCUMENT_DIR = os.path.join(ROOT_DIR, "documents")

