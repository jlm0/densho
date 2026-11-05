import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from rdflib import Graph
from rdflib.compare import to_canonical_graph

from knowledge_architecture.compiler.graph import normal_form
from knowledge_architecture.generated.metamodel import CompiledResult
from knowledge_architecture.graph.shapes import KA, NODE_NAMESPACE, rdf_graph
from knowledge_architecture.parser.result import Problem

if TYPE_CHECKING:
    from collections.abc import Mapping

    from knowledge_architecture.compiler.graph import CompiledGraph

OUTPUT_FOLDER = Path("build/compiled")
FORMAT_VERSION = 1
NOTICES = {
    CompiledResult.in_force: (
        "This result holds only the accepted directives and exceptions. "
        "It leaves out each proposal."
    ),
    CompiledResult.proposals: (
        "NOT IN FORCE. This result also holds the proposed directives and exceptions, "
        "which no reviewer has accepted. Use it only to review what acceptance would change."
    ),
}


@dataclass(frozen=True, slots=True)
class BuildOutput:
    result: CompiledResult
    files: Mapping[str, bytes]
    digests: Mapping[str, str]
    digest: str


def file_names(result: CompiledResult) -> tuple[str, str, str]:
    mark = "" if result == CompiledResult.in_force else ".proposals"
    return f"graph{mark}.json", f"graph{mark}.ttl", f"digests{mark}.json"


def _applied_entries(compiled: CompiledGraph) -> dict[str, list[dict[str, object]]]:
    return {
        node_id: [
            {
                "directive": entry.directive.id,
                "holder": entry.holder,
                "route": list(entry.route),
                "status": entry.directive.status,
            }
            for entry in entries
        ]
        for node_id, entries in compiled.applied.items()
    }


def _json_bytes(document: object) -> bytes:
    return (json.dumps(document, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def render_json(compiled: CompiledGraph) -> bytes:
    return _json_bytes(
        {
            "result": compiled.result,
            "notice": NOTICES[compiled.result],
            "format_version": FORMAT_VERSION,
            "left_out": compiled.left_out,
            "paths": compiled.paths,
            "applied": _applied_entries(compiled),
            "graph": normal_form(compiled.graph.model_dump(mode="json", exclude_none=True)),
        }
    )


def render_turtle(compiled: CompiledGraph) -> bytes:
    output = Graph()
    output.bind("ka", KA)
    output.bind("node", NODE_NAMESPACE)
    for triple in to_canonical_graph(rdf_graph(compiled.graph)):
        output.add(triple)
    header = f"# {compiled.result.value}: {NOTICES[compiled.result]}\n\n"
    return header.encode("utf-8") + output.serialize(format="turtle", encoding="utf-8")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def render_output(compiled: CompiledGraph) -> BuildOutput:
    json_name, turtle_name, digests_name = file_names(compiled.result)
    graph_files = {json_name: render_json(compiled), turtle_name: render_turtle(compiled)}
    hashes = {name: _sha256(data) for name, data in sorted(graph_files.items())}
    listing = "".join(f"{value}  {name}\n" for name, value in hashes.items())
    digest = f"sha256:{_sha256(listing.encode('utf-8'))}"
    digests = {name: f"sha256:{value}" for name, value in hashes.items()}
    manifest = _json_bytes({"result": compiled.result, "digest": digest, "files": digests})
    return BuildOutput(compiled.result, {**graph_files, digests_name: manifest}, digests, digest)


def _write_problem(folder: Path, error: OSError) -> Problem:
    return Problem(folder, 1, "write", f"The build cannot change this folder: {error.strerror!a}.")


def write_output(output: BuildOutput, folder: Path) -> list[Problem]:
    try:
        folder.mkdir(parents=True, exist_ok=True)
        for name, data in output.files.items():
            (folder / name).write_bytes(data)
    except OSError as error:
        return [_write_problem(folder, error)]
    return []


def remove_output(folder: Path) -> list[Problem]:
    try:
        for result in CompiledResult:
            for name in file_names(result):
                (folder / name).unlink(missing_ok=True)
    except OSError as error:
        return [_write_problem(folder, error)]
    return []
