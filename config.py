import os
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
ENV_VARS: Dict[str, str] = os.environ

# File paths
PROJECT_ROOT = Path(__file__).parent
if ENV_VARS["VAULT_PATH"]:
    VAULT_PATH = Path(ENV_VARS["VAULT_PATH"])
else:
    VAULT_PATH = PROJECT_ROOT / "vault"
VAULT_PATH.mkdir(exist_ok=True)

# Ensure the data directories exists
REQUESTS_DIR = VAULT_PATH / "requests"
REQUESTS_DIR.mkdir(exist_ok=True)
PAPERS_DIR = VAULT_PATH / "papers"
PAPERS_DIR.mkdir(exist_ok=True)

# API keys
SCOPUS_API_KEY = os.getenv("SCOPUS_API_KEY")
if not SCOPUS_API_KEY:
    print("Warning: SCOPUS_API_KEY not found in environment variables or .env file")

# API settings
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
MAX_RESULTS_PER_REQUEST = int(os.getenv("MAX_RESULTS_PER_REQUEST", "100"))

# Database settings
DB_PATH = VAULT_PATH / "litreview.db"
DB_EXISTS = DB_PATH.exists()


# Get API configuration as a dictionary
def get_api_config() -> dict[str, Any]:
    return {
        "scopus": {
            "api_key": SCOPUS_API_KEY,
            "timeout": REQUEST_TIMEOUT,
            "max_results_per_request": MAX_RESULTS_PER_REQUEST,
        }
    }
