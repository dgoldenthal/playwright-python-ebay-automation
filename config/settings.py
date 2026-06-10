from dotenv import load_dotenv
load_dotenv()  # loads .env from the current working directory
from dataclasses import dataclass
import os
from pathlib import Path


@dataclass(frozen=True)
class TestSettings:
    base_url: str = "https://www.ebay.com.au"
    headless: bool = False
    slow_mo_ms: int = 0
    default_timeout_ms: int = 15000
    username: str | None = None
    password: str | None = None
    project_root: Path = Path(__file__).resolve().parents[1]


def _to_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def load_settings() -> TestSettings:
    """Load runtime configuration from environment variables or .env."""
    project_root = Path(__file__).resolve().parents[1]
    load_dotenv(project_root / ".env")

    return TestSettings(
        base_url=os.getenv("BASE_URL", "https://www.ebay.com.au").rstrip("/"),
        headless=_to_bool(os.getenv("HEADLESS"), False),
        slow_mo_ms=int(os.getenv("SLOW_MO_MS", "0")),
        default_timeout_ms=int(os.getenv("DEFAULT_TIMEOUT_MS", "15000")),
        username=os.getenv("EBAY_USERNAME") or None,
        password=os.getenv("EBAY_PASSWORD") or None,
        project_root=project_root,
    )
