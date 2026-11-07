import re
from typing import TYPE_CHECKING

from engine.layout import KNOWLEDGE_FOLDER
from engine.parser.result import Problem

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

CREDENTIAL_CODE = "secret"
EMAIL_CODE = "email"
CREDENTIAL_FORMS = {
    "aws": r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b",
    "github": r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})",
    "api": r"\bsk-[A-Za-z0-9_-]{20,}",
    "slack": r"\bxox[abprs]-[A-Za-z0-9-]{4,}",
    "google": r"\bAIza[0-9A-Za-z_-]{35}",
    "stripe": r"\b[rs]k_live_[0-9A-Za-z]{16,}",
    "private": r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    "jwt": r"\beyJ[A-Za-z0-9_-]{8,}\.eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}",
    "login": r"\b[a-z][a-z0-9+.-]*://[^\s/:@]+:[^\s/@]+@",
    "assigned": (
        r"(?i:\b(?:password|passwd|secret|token|api[_-]?key)[a-z_-]*"
        r"[ \t]*[:=][ \t]*['\"]?[^\s'\"`]{8,})"
    ),
}
CREDENTIAL = re.compile("|".join(f"(?:{form})" for form in CREDENTIAL_FORMS.values()))
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}")
CREDENTIAL_MESSAGE = (
    "This line holds what reads as secret material. Remove it, and revoke the secret if it is real."
)
EMAIL_MESSAGE = "This line holds an email address. Remove it."


def _text_files(folder: Path) -> Iterator[tuple[Path, str]]:
    for path in sorted(folder.rglob("*")):
        if path.is_symlink() or not path.is_file():
            continue
        try:
            yield path, path.read_text(encoding="utf-8")
        except OSError, UnicodeDecodeError:
            continue


def exposure_problems(repository: Path) -> list[Problem]:
    problems: list[Problem] = []
    for path, text in _text_files(repository / KNOWLEDGE_FOLDER):
        for line, content in enumerate(text.splitlines(), 1):
            if CREDENTIAL.search(content):
                problems.append(Problem(path, line, CREDENTIAL_CODE, CREDENTIAL_MESSAGE))
            if EMAIL.search(content):
                problems.append(Problem(path, line, EMAIL_CODE, EMAIL_MESSAGE))
    return problems
