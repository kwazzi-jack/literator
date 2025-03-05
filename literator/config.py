import os
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from literator.utils import get_logger

logger = get_logger(__name__)


class APIConfig(BaseModel):
    """Configuration for API connections with validation"""

    api_key: str = Field(..., description="API key for authentication")
    api_url: str = Field(..., description="Base URL for the API")
    timeout: int = Field(30, gt=0, description="Request timeout in seconds")
    max_results_per_request: int = Field(
        100, gt=0, description="Maximum results per request"
    )
    retry_count: int = Field(
        3, gt=0, description="Number of retry attempts for failed requests"
    )
    retry_backoff: float = Field(
        1.5, gt=0.0, description="Exponential backoff factor for retries"
    )
    connect_timeout: int = Field(
        10, gt=0, description="Timeout for establishing connection in seconds"
    )
    user_agent: str = Field("Literator/1.0", description="User agent for API requests")
    rate_limit_pause: float = Field(
        1.0, ge=0, description="Seconds to pause between requests"
    )


class PathConfig(BaseModel):
    """Configuration for file paths"""

    project_root: Path
    vault_path: Path
    requests_dir: Path
    papers_dir: Path

    class Config:
        arbitrary_types_allowed = True


class DBConfig(BaseModel):
    """Configuration for database"""

    path: Path = Field(..., description="Path to the database file")
    exists: bool = Field(..., description="Database file existence")
    echo: bool = Field(False, description="Enable database echo")
    pool_size: int = Field(5, gt=0, description="Connection pool size")
    max_overflow: int = Field(10, ge=0, description="Maximum overflow connections")

    class Config:
        arbitrary_types_allowed = True


class Config:
    """Centralized configuration for the literator application"""

    def __init__(self):
        # Load environment variables
        logger.info("Initializing configuration")
        load_dotenv()
        self.env_vars: Dict[str, str] = dict(os.environ)

        # Initialize configurations
        self.initialize_paths()
        self.initialize_api_settings()
        self.initialize_db_settings()
        logger.info("Configuration initialization completed")

    def initialize_paths(self) -> None:
        """Set up and create necessary directories"""
        logger.debug("Setting up directory paths")
        project_root = Path(__file__).parent

        # Determine vault path from env or default
        if self.env_vars.get("VAULT_PATH") and len(self.env_vars["VAULT_PATH"]) > 0:
            vault_path = Path(self.env_vars["VAULT_PATH"])
            logger.info(f"Using custom vault path: {vault_path}")
        else:
            vault_path = project_root / "vault"
            logger.info(f"Using default vault path: {vault_path}")

        # Create necessary directories
        vault_path.mkdir(exist_ok=True)
        requests_dir = vault_path / "requests"
        requests_dir.mkdir(exist_ok=True)
        papers_dir = vault_path / "papers"
        papers_dir.mkdir(exist_ok=True)
        logger.debug("Required directories created")

        self.paths = PathConfig(
            project_root=project_root,
            vault_path=vault_path,
            requests_dir=requests_dir,
            papers_dir=papers_dir,
        )

    def initialize_api_settings(self) -> None:
        """Set up API-related configuration"""
        logger.debug("Initializing API settings")
        scopus_api_key = os.getenv("SCOPUS_API_KEY")
        if not scopus_api_key:
            logger.warning(
                "SCOPUS_API_KEY not found in environment variables or .env file"
            )
            raise ValueError("SCOPUS_API_KEY is required")

        scopus_api_url = os.getenv("SCOPUS_API_URL")
        if not scopus_api_url:
            logger.warning(
                "SCOPUS_API_URL not found in environment variables or .env file"
            )
            raise ValueError("SCOPUS_API_URL is required")

        request_timeout = int(self.env_vars.get("REQUEST_TIMEOUT", "30"))
        max_results_per_request = int(
            self.env_vars.get("MAX_RESULTS_PER_REQUEST", "100")
        )
        retry_count = int(self.env_vars.get("RETRY_COUNT", "3"))
        retry_backoff = float(self.env_vars.get("RETRY_BACKOFF", "1.5"))
        connect_timeout = int(self.env_vars.get("CONNECT_TIMEOUT", "10"))
        user_agent = self.env_vars.get("USER_AGENT", "Literator/1.0")
        rate_limit_pause = float(self.env_vars.get("RATE_LIMIT_PAUSE", "1.0"))
        logger.debug(f"{scopus_api_key=}, type={type(scopus_api_key)}")
        logger.debug(f"{scopus_api_url=}, type={type(scopus_api_url)}")
        logger.debug(f"{request_timeout=}, type={type(request_timeout)}")
        logger.debug(
            f"{max_results_per_request=}, type={type(max_results_per_request)}"
        )
        logger.debug(f"{retry_count=}, type={type(retry_count)}")
        logger.debug(f"{retry_backoff=}, type={type(retry_backoff)}")
        logger.debug(f"{connect_timeout=}, type={type(connect_timeout)}")
        logger.debug(f"{user_agent=}, type={type(user_agent)}")
        logger.debug(f"{rate_limit_pause=}, type={type(rate_limit_pause)}")

        self.scopus = APIConfig(
            api_key=scopus_api_key,
            api_url=scopus_api_url,
            timeout=request_timeout,
            max_results_per_request=max_results_per_request,
            retry_count=retry_count,
            retry_backoff=retry_backoff,
            connect_timeout=connect_timeout,
            user_agent=user_agent,
            rate_limit_pause=rate_limit_pause,
        )
        logger.debug("API settings initialized")

    def initialize_db_settings(self) -> None:
        """Set up database configuration"""
        logger.debug("Initializing database settings")
        db_path = self.paths.vault_path / "litreview.db"
        db_exists = db_path.exists()
        if db_exists:
            logger.info(f"Database file found at {db_path}")
        else:
            logger.info(f"Database file will be created at {db_path}")

        db_echo = os.getenv("DB_ECHO", "False").lower() in ("true", "1", "t")
        pool_size = int(os.getenv("DB_POOL_SIZE", "5"))
        max_overflow = int(os.getenv("DB_MAX_OVERFLOW", "10"))

        self.db = DBConfig(
            path=db_path,
            exists=db_exists,
            echo=db_echo,
            pool_size=pool_size,
            max_overflow=max_overflow,
        )
        logger.debug("Database settings initialized")

    def get_api_config(self) -> dict[str, Any]:
        """Return API configuration as a dictionary"""
        logger.debug("Retrieving API configuration")
        return {"scopus": self.scopus.model_dump()}

    def get_db_config(self) -> dict[str, Any]:
        """Return database configuration as a dictionary"""
        logger.debug("Retrieving database configuration")
        return self.db.model_dump()


# Create a singleton instance for easy import
config = Config()

# For backwards compatibility
get_api_config = config.get_api_config
get_db_config = config.get_db_config

# Export commonly used paths
PROJECT_ROOT = config.paths.project_root
VAULT_PATH = config.paths.vault_path
REQUESTS_DIR = config.paths.requests_dir
PAPERS_DIR = config.paths.papers_dir
DB_PATH = config.db.path
