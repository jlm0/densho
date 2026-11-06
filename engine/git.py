import os
import shutil
import subprocess
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Collection
    from pathlib import Path

IGNORED_EXIT = 0


def git_environment() -> dict[str, str]:
    variables = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    return {**variables, "LC_ALL": "C"}


def ignored_paths(folder: Path, paths: Collection[Path]) -> frozenset[Path]:
    program = shutil.which("git")
    if program is None or not paths:
        return frozenset()
    resolved = {path: str(path.resolve()) for path in paths}
    request = b"".join(os.fsencode(name) + b"\0" for name in resolved.values())
    try:
        checked = subprocess.run(  # noqa: S603
            [program, "-C", str(folder), "check-ignore", "-z", "--stdin"],
            input=request,
            capture_output=True,
            check=False,
            env=git_environment(),
        )
    except OSError:
        return frozenset()
    if checked.returncode != IGNORED_EXIT:
        return frozenset()
    named = {os.fsdecode(name) for name in checked.stdout.split(b"\0") if name}
    return frozenset(path for path, name in resolved.items() if name in named)
