import json
import shutil
import subprocess
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING, cast

from engine.evaluation.check import check_tasks
from engine.evaluation.conditions import (
    CONDITIONS,
    WITH,
    WITHOUT,
    build_condition,
    canary_problems,
    commit_folder,
)
from engine.evaluation.grader import grade
from engine.evaluation.isolation import (
    CONTEXT_PROMPT,
    RunFlags,
    identity_problems,
    memory_problems,
    probe_problems,
    read_probe,
    run_arguments,
    run_environment,
)
from engine.evaluation.report import (
    ERROR,
    FAILED,
    PASSED,
    PROBED,
    EvalReport,
    RunRecord,
    write_report,
)
from engine.evaluation.tasks import FIXTURE_FOLDER, load_tasks, read_files
from engine.parser.result import Problem

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from engine.evaluation.conditions import Condition
    from engine.evaluation.tasks import Task

WORK_FOLDER = PurePosixPath("build/eval")
RUN_CODE = "eval-run"
LOGIN_CODE = "login"
LOGIN_ARGUMENTS = ("auth", "status")
DETAIL_LIMIT = 200
GRADER_SKIPPED = frozenset({".git", ".claude", "AGENTS.md"})
PROBE_TIMEOUT = 120.0


@dataclass(frozen=True, slots=True)
class EvalOptions:
    discipline: str
    tasks: tuple[str, ...] = ()
    runs: int = 1
    model: str = "sonnet"
    budget: float = 5.0
    run_budget: float = 0.5
    timeout: float = 900.0
    work: Path | None = None
    claude: str = "claude"
    home: Path = field(default_factory=Path.home)
    dry_run: bool = False


def default_work(repository: Path) -> Path:
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    return repository / WORK_FOLDER / stamp


def selected_tasks(tasks: Sequence[Task], names: Sequence[str]) -> tuple[list[Task], list[str]]:
    known = {task.id for task in tasks}
    missing = [name for name in names if name not in known]
    chosen = [task for task in tasks if task.canary or not names or task.id in names]
    return sorted(chosen, key=lambda task: (not task.canary, task.id)), missing


def _cost(data: Mapping[str, object], fallback: float) -> float:
    value = data.get("total_cost_usd")
    if isinstance(value, bool) or not isinstance(value, int | float) or value < 0:
        return fallback
    return float(value)


def _result_data(stdout: str) -> dict[str, object] | None:
    try:
        data = cast("object", json.loads(stdout))
    except ValueError:
        return None
    return cast("dict[str, object]", data) if isinstance(data, dict) else None


def _error_detail(data: Mapping[str, object] | None, returncode: int) -> str | None:
    if data is None:
        return f"claude gave no JSON result, exit {returncode}"
    if data.get("is_error") is not False or data.get("subtype") != "success":
        reply = data.get("result")
        text = f": {reply[:DETAIL_LIMIT]!a}" if isinstance(reply, str) else ""
        return f"claude ended with {data.get('subtype')!a}{text}"
    if not isinstance(data.get("result"), str):
        return "claude gave no reply text"
    return None


def run_files(folder: Path) -> tuple[dict[PurePosixPath, str], list[Problem]]:
    return read_files(folder, skipped=GRADER_SKIPPED)


def _numbers(record: RunRecord, data: Mapping[str, object]) -> None:
    duration = data.get("duration_ms")
    turns = data.get("num_turns")
    record.duration_ms = duration if isinstance(duration, int) else None
    record.turns = turns if isinstance(turns, int) else None
    usage = data.get("modelUsage")
    record.models = sorted(cast("dict[str, object]", usage)) if isinstance(usage, dict) else []


@dataclass(slots=True)
class _Batch:
    repository: Path
    options: EvalOptions
    work: Path
    git_config: Path
    conditions: dict[str, Condition]
    report: EvalReport

    def run_folder(self, task: Task, condition: str, repeat: int) -> Path | list[Problem]:
        folder = self.work / "runs" / task.id / f"{condition}-{repeat}"
        folder.mkdir(parents=True)
        for path, data in self.conditions[condition].files.items():
            target = folder / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        fixture = task.folder / FIXTURE_FOLDER
        if fixture.is_dir():
            shutil.copytree(fixture, folder, symlinks=True, dirs_exist_ok=True)
        problems = commit_folder(folder, self.git_config, f"{task.id} {condition} {repeat}")
        return problems or folder

    def flags(self, task: Task) -> RunFlags:
        options = self.options
        return RunFlags(options.claude, options.model, options.run_budget, task.tools)

    def claude(
        self, task: Task, folder: Path, prompt: str, *, probe: bool
    ) -> subprocess.CompletedProcess[str]:
        home = self.options.home
        return subprocess.run(  # noqa: S603
            run_arguments(self.flags(task), folder, home, probe=probe),
            input=prompt,
            capture_output=True,
            text=True,
            cwd=folder,
            env=run_environment(home, self.git_config),
            timeout=PROBE_TIMEOUT if probe else self.options.timeout,
            check=False,
        )

    def login(self) -> list[Problem]:
        try:
            done = subprocess.run(  # noqa: S603
                [self.options.claude, *LOGIN_ARGUMENTS],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=self.work,
                env=run_environment(self.options.home, self.git_config),
                timeout=PROBE_TIMEOUT,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            return [Problem(self.work, 1, LOGIN_CODE, f"The login check did not finish: {error}.")]
        if done.returncode != 0:
            message = "claude is not logged in with the run environment. Run claude auth status."
            return [Problem(self.work, 1, LOGIN_CODE, message)]
        return []

    def isolation(self, task: Task, folder: Path) -> list[Problem]:
        problems = identity_problems(folder, self.git_config)
        try:
            done = self.claude(task, folder, CONTEXT_PROMPT, probe=True)
        except (OSError, subprocess.TimeoutExpired) as error:
            return [*problems, Problem(folder, 1, "probe", f"The probe did not finish: {error}.")]
        (folder.parent / f"{folder.name}.probe.jsonl").write_text(done.stdout, encoding="utf-8")
        found = probe_problems(folder, read_probe(done.stdout), task.tools)
        return [*problems, *found, *memory_problems(folder, self.options.home)]

    def agent(self, task: Task, folder: Path, record: RunRecord) -> None:
        try:
            done = self.claude(task, folder, task.prompt, probe=False)
        except subprocess.TimeoutExpired:
            record.status = ERROR
            record.cost = self.options.run_budget
            record.detail = f"the run passed {self.options.timeout:.0f} seconds"
            return
        except OSError as error:
            record.status = ERROR
            record.detail = f"claude did not start: {error}"
            return
        (folder.parent / f"{folder.name}.result.json").write_text(done.stdout, encoding="utf-8")
        data = _result_data(done.stdout)
        record.cost = _cost(data or {}, self.options.run_budget)
        if data is not None:
            _numbers(record, data)
        error = _error_detail(data, done.returncode)
        if error is not None:
            record.status = ERROR
            record.detail = error
            return
        files, problems = run_files(folder)
        reply = cast("str", (data or {})["result"])
        results = grade(task, files, reply)
        record.targets = {result.directive: result.passed for result in results}
        record.status = PASSED if all(record.targets.values()) else FAILED
        failures = [failure for result in results for failure in result.failures]
        record.detail = "; ".join([*failures, *(problem.message for problem in problems)])

    def run(self, task: Task, condition: str, repeat: int) -> bool:
        options = self.options
        directives = [target.directive for target in task.targets]
        record = RunRecord(task.id, task.canary, condition, repeat, directives)
        self.report.runs.append(record)
        if not options.dry_run and self.report.cost + options.run_budget > options.budget:
            record.detail = "the batch budget does not cover another run"
            return True
        folder = self.run_folder(task, condition, repeat)
        if isinstance(folder, list):
            self.report.problems.extend(folder)
            return False
        record.folder = folder.relative_to(self.work).as_posix()
        problems = self.isolation(task, folder)
        if problems:
            self.report.problems.extend(problems)
            record.detail = "the isolation probe failed"
            return False
        if options.dry_run:
            record.status = PROBED
            return True
        self.agent(task, folder, record)
        problems = memory_problems(folder, options.home)
        self.report.problems.extend(problems)
        return not problems


def _canary_problems(report: EvalReport) -> list[Problem]:
    canaries = {run.condition: run for run in report.runs if run.canary}
    expected = {WITH: PASSED, WITHOUT: FAILED}
    problems: list[Problem] = []
    for condition, status in expected.items():
        run = canaries.get(condition)
        if run is not None and run.status not in {status, PROBED}:
            message = f"The canary {run.task} must end {status} in {condition}, not {run.status}."
            problems.append(Problem(Path(run.folder), 1, "eval-canary", message))
    return problems


def _conditions(batch: _Batch, tasks: Sequence[Task]) -> list[Problem]:
    options = batch.options
    for name in CONDITIONS:
        try:
            built = build_condition(
                batch.repository, batch.work, options.discipline, name, batch.git_config
            )
        except ValueError as error:
            return [Problem(batch.work, 1, RUN_CODE, str(error))]
        if isinstance(built, list):
            return built
        batch.conditions[name] = built
    targets = [target.directive for task in tasks for target in task.targets]
    canary = [target.directive for task in tasks if task.canary for target in task.targets]
    return canary_problems(batch.conditions[WITH], batch.conditions[WITHOUT], targets, canary)


def _prepared(repository: Path, options: EvalOptions) -> tuple[list[Task], list[Problem]]:
    _, problems = check_tasks(repository)
    if problems:
        return [], problems
    tasks, problems = load_tasks(repository, options.discipline)
    chosen, missing = selected_tasks(tasks, options.tasks)
    problems += [
        Problem(repository, 1, RUN_CODE, f"{options.discipline} has no task {name}.")
        for name in missing
    ]
    if not any(task.canary for task in chosen):
        message = f"{options.discipline} has no canary task in knowledge/evals/."
        problems.append(Problem(repository, 1, RUN_CODE, message))
    if options.runs < 1 or options.run_budget <= 0 or options.budget < options.run_budget:
        message = "Set 1 or more runs, and a batch budget of at least one run budget."
        problems.append(Problem(repository, 1, RUN_CODE, message))
    return chosen, problems


def run_eval(repository: Path, options: EvalOptions) -> EvalReport:
    report = EvalReport(options.discipline, options.model)
    tasks, report.problems = _prepared(repository, options)
    if report.problems:
        return report
    work = (options.work or default_work(repository)).resolve()
    if work.exists() and (not work.is_dir() or any(work.iterdir())):
        message = "The work folder must be new or empty."
        report.problems.append(Problem(work, 1, RUN_CODE, message))
        return report
    work.mkdir(parents=True, exist_ok=True)
    report.work = work
    git_config = work / "gitconfig"
    git_config.write_text("", encoding="utf-8")
    batch = _Batch(repository, options, work, git_config, {}, report)
    report.problems = batch.login() or _conditions(batch, tasks)
    if not report.problems:
        _run_tasks(batch, tasks)
    write_report(report, work, datetime.now(UTC).date().isoformat())
    return report


def _run_tasks(batch: _Batch, tasks: Sequence[Task]) -> None:
    report = batch.report
    for task in tasks:
        for repeat in range(1, (1 if task.canary else batch.options.runs) + 1):
            for condition in CONDITIONS:
                if not batch.run(task, condition, repeat):
                    return
        if task.canary:
            report.problems.extend(_canary_problems(report))
            if report.problems:
                return
