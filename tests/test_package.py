import tomllib
from pathlib import Path

import knowledge_architecture

PYPROJECT = Path(__file__).resolve().parents[1] / "pyproject.toml"


def test_installed_version_matches_pyproject() -> None:
    project = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))["project"]
    assert knowledge_architecture.__version__ == project["version"]
