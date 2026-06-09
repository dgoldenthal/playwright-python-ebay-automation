import json
from pathlib import Path
from typing import Any


def load_test_data(path: str | Path) -> dict[str, Any]:
    """Read JSON test data for data-driven scenarios."""
    file_path = Path(path)
    if not file_path.is_absolute():
        file_path = Path(__file__).resolve().parents[1] / file_path

    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)
