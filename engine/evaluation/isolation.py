import getpass
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, cast

from engine.evaluation.conditions import NEUTRAL_EMAIL, NEUTRAL_NAME, run_git
from engine.parser.result import Problem

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping, Sequence

ALWAYS_TOOLS = ("Skill",)
CONTEXT_PROMPT = "/context all"
INSTRUCTION_FILES = ("CLAUDE.md", "CLAUDE.local.md", "AGENTS.md", ".claude/CLAUDE.md")
INSTRUCTION_FILES_MORE = (".claude/AGENTS.md",)
RULES_FOLDER = ".claude/rules"
GLOB_CHARACTERS = frozenset("*?[]{}()!+@")
KEPT_SKILL_SOURCES = frozenset({"Built-in", "Project"})
BUILT_IN_PLUGIN_PATH = "builtin"
DEFAULT_OUTPUT_STYLE = "default"
SECOND_COLUMN = 1
ISOLATION_CODES = (
    "memory-file",
    "instructions",
    "skill",
    "plugin",
    "mcp",
    "agent",
    "output-style",
    "tool",
    "auto-memory",
    "git-identity",
    "probe",
)
TABLE_ROW = re.compile(r"^\|(?P<cells>.+)\|[ \t]*$")
SECTION = re.compile(r"^### (?P<name>.+?)[ \t]*$")
SLUG_CHARACTER = re.compile(r"[^A-Za-z0-9]")


@dataclass(frozen=True, slots=True)
class RunFlags:
    claude: str
    model: str
    run_budget: float
    tools: tuple[str, ...]


def glob_literal(path: Path | str) -> str:
    return "".join(
        f"[{character}]" if character in GLOB_CHARACTERS else character for character in str(path)
    )


def instruction_excludes(run_folder: Path, home: Path) -> list[str]:
    folders = [*run_folder.resolve().parents]
    names = (*INSTRUCTION_FILES, *INSTRUCTION_FILES_MORE)
    patterns = [glob_literal(folder / name) for folder in folders for name in names]
    patterns += [f"{glob_literal(folder / RULES_FOLDER)}/**" for folder in folders]
    patterns += [
        glob_literal(home / ".claude" / "CLAUDE.md"),
        f"{glob_literal(home / '.claude/rules')}/**",
    ]
    return list(dict.fromkeys(patterns))


def run_settings(run_folder: Path, home: Path) -> str:
    settings = {
        "autoMemoryEnabled": False,
        "claudeMdExcludes": instruction_excludes(run_folder, home),
    }
    return json.dumps(settings, sort_keys=True)


def run_tools(tools: Iterable[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys((*tools, *ALWAYS_TOOLS)))


def run_arguments(flags: RunFlags, run_folder: Path, home: Path, *, probe: bool) -> list[str]:
    output = ["stream-json", "--verbose"] if probe else ["json"]
    budget = 0.01 if probe else flags.run_budget
    return [
        flags.claude,
        "-p",
        "--output-format",
        *output,
        "--model",
        flags.model,
        "--tools",
        ",".join(run_tools(flags.tools)),
        "--permission-mode",
        "acceptEdits",
        "--permission-prompts",
        "none",
        "--setting-sources",
        "project",
        "--settings",
        run_settings(run_folder, home),
        "--strict-mcp-config",
        "--no-session-persistence",
        "--max-budget-usd",
        f"{budget:.2f}",
    ]


def run_environment(home: Path, git_config: Path) -> dict[str, str]:
    return {
        "HOME": str(home),
        "USER": getpass.getuser(),
        "PATH": os.environ.get("PATH", os.defpath),
        "LANG": "en_US.UTF-8",
        "TERM": "dumb",
        "CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1",
        "GIT_CONFIG_GLOBAL": str(git_config),
        "GIT_CONFIG_NOSYSTEM": "1",
    }


def memory_folder(run_folder: Path, home: Path) -> Path:
    slug = SLUG_CHARACTER.sub("-", str(run_folder.resolve()))
    return home / ".claude" / "projects" / slug / "memory"


@dataclass(frozen=True, slots=True)
class Probe:
    init: Mapping[str, object]
    context: str
    cost: float | None


def read_probe(output: str) -> Probe | None:
    init: dict[str, object] | None = None
    context: str | None = None
    cost: float | None = None
    for line in output.splitlines():
        try:
            event = cast("object", json.loads(line))
        except ValueError:
            continue
        if not isinstance(event, dict):
            continue
        data = cast("dict[str, object]", event)
        if data.get("type") == "system" and data.get("subtype") == "init":
            init = data
        elif data.get("type") == "result" and isinstance(data.get("result"), str):
            context = cast("str", data["result"])
            value = data.get("total_cost_usd")
            cost = (
                float(value)
                if isinstance(value, int | float) and not isinstance(value, bool)
                else None
            )
    if init is None or context is None:
        return None
    return Probe(init, context, cost)


def table_rows(context: str, section: str) -> list[list[str]] | None:
    rows: list[list[str]] = []
    inside = False
    found = False
    for line in context.splitlines():
        heading = SECTION.match(line)
        if heading:
            inside = heading["name"] == section
            found = found or inside
            continue
        row = TABLE_ROW.match(line) if inside else None
        if row:
            cells = [cell.strip() for cell in row["cells"].split("|")]
            if not all(set(cell) <= {"-", ":"} for cell in cells):
                rows.append(cells)
    return rows[1:] if found and rows else ([] if found else None)


def _strings(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [entry for entry in cast("list[object]", value) if isinstance(entry, str)]


def _mappings(value: object) -> list[dict[str, object]]:
    if not isinstance(value, list):
        return []
    return [
        cast("dict[str, object]", entry)
        for entry in cast("list[object]", value)
        if isinstance(entry, dict)
    ]


def _memory_problems(run_folder: Path, context: str) -> list[Problem]:
    problems: list[Problem] = []
    rows = table_rows(context, "Memory Files") or []
    paths = [Path(row[SECOND_COLUMN]) for row in rows if len(row) > SECOND_COLUMN]
    for path in paths:
        if not path.is_absolute() or not path.resolve().is_relative_to(run_folder.resolve()):
            message = f"The run loads a memory file outside the run folder: {path}."
            problems.append(Problem(run_folder, 1, "memory-file", message))
    if (run_folder / "AGENTS.md").resolve() not in {path.resolve() for path in paths}:
        message = "The run does not load the AGENTS.md of the run folder."
        problems.append(Problem(run_folder, 1, "instructions", message))
    return problems


def _project_skills(run_folder: Path) -> set[str]:
    folder = run_folder / ".claude" / "skills"
    if not folder.is_dir():
        return set()
    return {path.parent.name for path in folder.glob("*/SKILL.md") if path.is_file()}


def _skill_problems(run_folder: Path, context: str) -> list[Problem]:
    rows = table_rows(context, "Skills")
    if rows is None:
        return [
            Problem(
                run_folder, 1, "skill", "The probe lists no skills. Give the run the Skill tool."
            )
        ]
    problems: list[Problem] = []
    known = _project_skills(run_folder)
    for row in rows:
        if len(row) <= SECOND_COLUMN or row[SECOND_COLUMN] not in KEPT_SKILL_SOURCES:
            source = row[SECOND_COLUMN] if len(row) > SECOND_COLUMN else "no source"
            message = f"The run loads the skill {row[0]} from the source {source}."
            problems.append(Problem(run_folder, 1, "skill", message))
        elif row[SECOND_COLUMN] == "Project" and row[0] not in known:
            message = f"The run loads the project skill {row[0]}, and the run folder lacks it."
            problems.append(Problem(run_folder, 1, "skill", message))
    return problems


def _init_problems(
    run_folder: Path, init: Mapping[str, object], tools: Sequence[str]
) -> list[Problem]:
    problems: list[Problem] = []
    for plugin in _mappings(init.get("plugins")):
        if plugin.get("path") != BUILT_IN_PLUGIN_PATH:
            message = f"The run loads the plugin {plugin.get('name')!a}."
            problems.append(Problem(run_folder, 1, "plugin", message))
    servers = init.get("mcp_servers")
    if not isinstance(servers, list) or servers:
        problems.append(Problem(run_folder, 1, "mcp", "The run has MCP servers."))
    style = init.get("output_style")
    if style != DEFAULT_OUTPUT_STYLE:
        message = f"The run has the output style {style!a}, not {DEFAULT_OUTPUT_STYLE}."
        problems.append(Problem(run_folder, 1, "output-style", message))
    loaded = set(_strings(init.get("tools")))
    expected = set(run_tools(tools))
    for tool in sorted(loaded ^ expected):
        verb = "has" if tool in loaded else "lacks"
        message = f"The run {verb} the tool {tool}, and the task names {sorted(expected)}."
        problems.append(Problem(run_folder, 1, "tool", message))
    return problems


def _agent_problems(run_folder: Path, context: str) -> list[Problem]:
    rows = table_rows(context, "Custom Agents") or []
    return [
        Problem(run_folder, 1, "agent", f"The run loads the custom agent {row[0]}.") for row in rows
    ]


def memory_problems(run_folder: Path, home: Path) -> list[Problem]:
    folder = memory_folder(run_folder, home)
    if not folder.exists():
        return []
    message = f"Auto memory has a folder for the run folder: {folder}."
    return [Problem(run_folder, 1, "auto-memory", message)]


def identity_problems(run_folder: Path, git_config: Path) -> list[Problem]:
    problems: list[Problem] = []
    for key, expected in (("user.name", NEUTRAL_NAME), ("user.email", NEUTRAL_EMAIL)):
        done = run_git(run_folder, git_config, "config", "--get", key)
        if done.stdout.strip() != expected:
            message = f"git gives {key} a value other than {expected}."
            problems.append(Problem(run_folder, 1, "git-identity", message))
    done = run_git(run_folder, git_config, "log", "--format=%an%n%ae%n%cn%n%ce")
    if set(done.stdout.split()) != {NEUTRAL_NAME, NEUTRAL_EMAIL}:
        message = "The git history of the run folder holds an identity other than the neutral one."
        problems.append(Problem(run_folder, 1, "git-identity", message))
    return problems


def probe_problems(run_folder: Path, probe: Probe | None, tools: Sequence[str]) -> list[Problem]:
    if probe is None:
        return [Problem(run_folder, 1, "probe", "The probe gave no init event and no context.")]
    problems: list[Problem] = []
    if probe.cost != 0:
        message = f"The probe must cost 0 USD, and it reports {probe.cost}."
        problems.append(Problem(run_folder, 1, "probe", message))
    return [
        *problems,
        *_memory_problems(run_folder, probe.context),
        *_skill_problems(run_folder, probe.context),
        *_agent_problems(run_folder, probe.context),
        *_init_problems(run_folder, probe.init, tools),
    ]
