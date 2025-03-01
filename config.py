import os
from pathlib import Path
from typing import Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# File paths
PROJECT_ROOT = Path(__file__).parent
VAULT_PATH = Path("/net/sinatra/vault2-tina/welman/phd/litreview/")

# Ensure the results directory exists
RESULTS_DIR = PROJECT_ROOT / "results"
RESULTS_DIR.mkdir(exist_ok=True)

# API keys
SCOPUS_API_KEY = os.getenv("SCOPUS_API_KEY")
if not SCOPUS_API_KEY:
    print("Warning: SCOPUS_API_KEY not found in environment variables or .env file")

# API settings
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
MAX_RESULTS_PER_REQUEST = int(os.getenv("MAX_RESULTS_PER_REQUEST", "100"))


# Get API configuration as a dictionary
def get_api_config() -> dict[str, Any]:
    return {
        "scopus": {
            "api_key": SCOPUS_API_KEY,
            "timeout": REQUEST_TIMEOUT,
            "max_results_per_request": MAX_RESULTS_PER_REQUEST,
        }
    }
