import json
from dataclasses import asdict, dataclass, field
from typing import TYPE_CHECKING

from engine.evaluation.conditions import WITH, WITHOUT
from engine.parser.result import Problem

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping
    from pathlib import Path


PASSED = "passed"
FAILED = "failed"
ERROR = "error"
NOT_RUN = "not-run"
PROBED = "probed"
SMALL_SAMPLE = "The sample is small. The counts are raw, and they show no significance."


@dataclass(slots=True)
class RunRecord:
    task: str
    canary: bool
    condition: str
    repeat: int
    directives: list[str]
    folder: str = ""
    status: str = NOT_RUN
    targets: dict[str, bool] = field(default_factory=dict[str, bool])
    cost: float = 0.0
    duration_ms: int | None = None
    turns: int | None = None
    models: list[str] = field(default_factory=list[str])
    detail: str = ""


@dataclass(slots=True)
class EvalReport:
    discipline: str
    model: str
    work: Path | None = None
    runs: list[RunRecord] = field(default_factory=list[RunRecord])
    problems: list[Problem] = field(default_factory=list[Problem])

    @property
    def cost(self) -> float:
        return sum(run.cost for run in self.runs)


@dataclass(slots=True)
class Counts:
    passes: int = 0
    runs: int = 0
    errors: int = 0

    def text(self) -> str:
        errors = (
            f", {self.errors} {'error' if self.errors == 1 else 'errors'}" if self.errors else ""
        )
        return f"{self.passes} of {self.runs} passed{errors}"


def directive_counts(runs: Iterable[RunRecord]) -> dict[str, dict[str, Counts]]:
    counts: dict[str, dict[str, Counts]] = {}
    for run in runs:
        if run.canary or run.condition not in {WITH, WITHOUT}:
            continue
        for directive in run.directives:
            entry = counts.setdefault(directive, {WITH: Counts(), WITHOUT: Counts()})[run.condition]
            if run.status == ERROR:
                entry.errors += 1
            elif run.status in {PASSED, FAILED}:
                entry.runs += 1
                entry.passes += run.targets.get(directive, False)
    return dict(sorted(counts.items()))


def is_candidate(counts: Mapping[str, Counts]) -> bool:
    found, absent = counts[WITH], counts[WITHOUT]
    if not found.runs or not absent.runs or found.errors or absent.errors:
        return False
    return found.passes * absent.runs <= absent.passes * found.runs


def signal_line(directive: str, counts: Mapping[str, Counts], date: str) -> str:
    found, absent = counts[WITH], counts[WITHOUT]
    return (
        f"- `{directive}`: {date}, eval. With the discipline in force, {found.passes} of "
        f"{found.runs} runs passed. Without it, {absent.passes} of {absent.runs} runs passed."
    )


def _tasks_of(runs: Iterable[RunRecord]) -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    for run in runs:
        if run.canary:
            continue
        for directive in run.directives:
            names = found.setdefault(directive, [])
            if run.task not in names:
                names.append(run.task)
    return found


def _cell(text: str) -> str:
    return " ".join(text.replace("|", "/").split())


def report_markdown(report: EvalReport, date: str) -> str:
    runs = report.runs
    counts = directive_counts(runs)
    tasks = _tasks_of(runs)
    done = [run for run in runs if run.status != NOT_RUN]
    errors = sum(run.status == ERROR for run in runs)
    lines = [
        f"# Eval of {report.discipline}",
        "",
        (
            f"- Model: `{report.model}`. Models in the results: "
            f"{', '.join(sorted({model for run in runs for model in run.models})) or 'none'}."
        ),
        f"- Runs: {len(done)}, with {errors} errors. Not run: {len(runs) - len(done)}.",
        f"- Cost: {report.cost:.4f} USD, from `total_cost_usd` of each run.",
        "",
        SMALL_SAMPLE,
        "",
        "## Directives",
        "",
        "| Directive | Tasks | With | Without |",
        "| --- | --- | --- | --- |",
    ]
    lines += [
        f"| `{directive}` | {', '.join(tasks.get(directive, []))} | "
        f"{entry[WITH].text()} | {entry[WITHOUT].text()} |"
        for directive, entry in counts.items()
    ]
    candidates = [directive for directive, entry in counts.items() if is_candidate(entry)]
    lines += ["", "## Deprecation candidates", ""]
    lines += [signal_line(directive, counts[directive], date) for directive in candidates] or [
        "No directive is a candidate."
    ]
    lines += [
        "",
        "## Runs",
        "",
        "| Task | Condition | Repeat | Status | Cost USD | Turns | Detail |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    lines += [
        f"| {run.task}{' (canary)' if run.canary else ''} | {run.condition} | {run.repeat} | "
        f"{run.status} | {run.cost:.4f} | {run.turns if run.turns is not None else ''} | "
        f"{_cell(run.detail)} |"
        for run in runs
    ]
    if report.problems:
        lines += ["", "## Problems", ""]
        lines += [f"- {_cell(str(problem))}" for problem in report.problems]
    return "\n".join(lines) + "\n"


def report_data(report: EvalReport) -> dict[str, object]:
    counts = directive_counts(report.runs)
    return {
        "discipline": report.discipline,
        "model": report.model,
        "cost_usd": report.cost,
        "note": SMALL_SAMPLE,
        "directives": {
            directive: {condition: asdict(value) for condition, value in entry.items()}
            for directive, entry in counts.items()
        },
        "candidates": [directive for directive, entry in counts.items() if is_candidate(entry)],
        "runs": [asdict(run) for run in report.runs],
        "problems": [str(problem) for problem in report.problems],
    }


def write_report(report: EvalReport, folder: Path, date: str) -> tuple[Path, Path]:
    data = folder / "report.json"
    text = folder / "report.md"
    data.write_text(json.dumps(report_data(report), indent=2, sort_keys=True) + "\n", "utf-8")
    text.write_text(report_markdown(report, date), "utf-8")
    return data, text
