import os

# ROOT_DIR is now one level up from utils/ (which was app/)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

APP_CONFIG_FPATH = os.path.join(ROOT_DIR, "config", "app_config.yaml")
PROMPT_CONFIG_FPATH = os.path.join(ROOT_DIR, "config", "prompt_config.yaml")

OUTPUTS_DIR = os.path.join(ROOT_DIR, "outputs")

DATA_DIR = os.path.join(ROOT_DIR, "data")

DOCUMENT_DIR = os.path.join(ROOT_DIR, "documents")

# Evaluation paths
EVALUATION_DIR = os.path.join(ROOT_DIR, "evaluation")
EVALUATION_CASES_PATH = os.path.join(EVALUATION_DIR, "rag_evaluation_cases.json")
EVALUATION_RESULTS_DIR = os.path.join(OUTPUTS_DIR, "evaluation_results")

