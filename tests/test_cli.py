from typing import TYPE_CHECKING

from typer.testing import CliRunner

from knowledge_architecture.cli import app

if TYPE_CHECKING:
    from pathlib import Path

    import pytest

RUNNER = CliRunner()
NODE = """---
id: sample
kind: ka:Domain
title: Sample
status: accepted
origin: template
knowledge_type: domain
---

## Definition

A sample.
"""
ROOT = """---
id: root
kind: ka:Root
title: Root
status: accepted
origin: template
pointers:
  - kind: ka:TextPointer
    target: sample
    trigger: You need the sample.
---
"""


def write_node(folder: Path, text: str = NODE) -> Path:
    folder.mkdir(parents=True)
    path = folder / "node.md"
    path.write_text(text, encoding="utf-8")
    return path


def test_parse_needs_a_folder() -> None:
    result = RUNNER.invoke(app, ["parse"])
    assert result.exit_code > 1
    assert "Usage" in result.output


def test_parse_passes_on_valid_nodes(tmp_path: Path) -> None:
    write_node(tmp_path / "a")
    result = RUNNER.invoke(app, ["parse", str(tmp_path)])
    assert result.exit_code == 0
    assert result.output == "1 nodes parsed, 0 problems\n"


def test_parse_fails_and_prints_each_location(tmp_path: Path) -> None:
    path = write_node(tmp_path / "a", NODE.replace("status: accepted", "status: ok"))
    result = RUNNER.invoke(app, ["parse", str(tmp_path)])
    assert result.exit_code == 1
    assert f"{path}:5: schema: status: " in result.output
    assert result.output.endswith("0 nodes parsed, 1 problems\n")


def test_parse_fails_on_a_missing_folder(tmp_path: Path) -> None:
    assert RUNNER.invoke(app, ["parse", str(tmp_path / "missing")]).exit_code == 1


def test_graph_passes_on_an_empty_tree(tmp_path: Path) -> None:
    (tmp_path / "knowledge").mkdir()
    (tmp_path / "skills").mkdir()
    result = RUNNER.invoke(app, ["graph", str(tmp_path)])
    assert result.exit_code == 0
    assert result.output == "0 nodes checked, 0 problems\n"


def test_graph_passes_on_a_valid_tree(tmp_path: Path) -> None:
    write_node(tmp_path / "knowledge", ROOT)
    write_node(tmp_path / "knowledge/sample")
    (tmp_path / "skills").mkdir()
    result = RUNNER.invoke(app, ["graph", str(tmp_path)])
    assert result.exit_code == 0, result.output
    assert result.output == "2 nodes checked, 0 problems\n"


def test_graph_fails_and_prints_each_location(tmp_path: Path) -> None:
    write_node(tmp_path / "knowledge", ROOT.replace("target: sample", "target: missing"))
    write_node(tmp_path / "knowledge/sample")
    (tmp_path / "skills").mkdir()
    result = RUNNER.invoke(app, ["graph", str(tmp_path)])
    assert result.exit_code == 1
    path = tmp_path / "knowledge/node.md"
    assert (
        f"{path}:9: reference: target names 'missing', and no node or directive has this ID.\n"
        in result.output
    )
    assert result.output.endswith("2 nodes checked, 1 problems\n")


def test_graph_reads_the_current_folder_by_default(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    write_node(tmp_path / "knowledge/sample")
    (tmp_path / "skills").mkdir()
    result = RUNNER.invoke(app, ["graph"])
    assert result.exit_code == 1
    assert result.output.startswith("knowledge/node.md:1: root: ")
