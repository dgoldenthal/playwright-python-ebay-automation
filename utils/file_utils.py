from pathlib import Path
from datetime import datetime
import re


def ensure_dir(path: str | Path) -> Path:
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def safe_filename(value: str) -> str:
    clean_value = re.sub(r"[^a-zA-Z0-9_.-]+", "_", value.strip())
    return clean_value.strip("_") or "artifact"


def timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")
