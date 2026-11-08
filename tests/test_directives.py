from pathlib import Path
from typing import Any

import pytest

from engine.directives import (
    DIRECTIVE_CODES,
    AppliedDirective,
    check_directives,
    check_items,
    resolve_directives,
)
from engine.graph.references import references_of
from engine.parser import ParsedNode, parse_source

type Spec = dict[str, Any]

LADDER_RUNGS = 40
PAIRS = 20
LIST_FIELDS = (
    "broader",
    "uses",
    "applies",
    "related",
    "informs",
    "depends_on",
    "governs",
    "implements",
)


def rule(directive_id: str, scope: str = "subtree", **fields: object) -> Spec:
    return {"id": directive_id, "scope": scope, "status": "accepted", **fields}


def stop(directive_id: str, status: str = "accepted") -> Spec:
    return {
        "directive": directive_id,
        "reason": "This node is a throwaway prototype.",
        "status": status,
    }


def domain(node_id: str, **fields: object) -> Spec:
    return {"id": node_id, "kind": "densho:Domain", **fields}


def concept(node_id: str, *broader: str, **fields: object) -> Spec:
    return {"id": node_id, "kind": "densho:Concept", "broader": list(broader), **fields}


def skill(node_id: str, *uses: str, **fields: object) -> Spec:
    return {"id": node_id, "kind": "densho:Skill", "uses": list(uses), **fields}


def root(**fields: object) -> Spec:
    return {"id": "root", "kind": "densho:Root", **fields}


def directive_lines(entry: Spec) -> list[str]:
    text = entry.get("text", f"Do the {entry['id']} thing.")
    lines = [f"- {text} ^{entry['id']}", f"  - scope: {entry['scope']}", "  - basis: judgment"]
    lines += [f"  - status: {entry['status']}", "  - origin: template"]
    for key in ("also_attached_to", "refines", "conflicts_with"):
        lines += [f"  - {key}: {value}" for value in entry.get(key, [])]
    return lines


def front_matter(spec: Spec, others: list[str]) -> list[str]:
    lines = [f"id: {spec['id']}", f"kind: {spec['kind']}", f"title: {spec['id']}"]
    lines += [f"status: {spec.get('status', 'accepted')}", "origin: template"]
    if spec["kind"] == "densho:Root":
        lines.append("pointers:")
        for other in others:
            lines += ["  - kind: densho:TextPointer", f"    target: {other}"]
            lines.append("    trigger: You need it.")
        return lines
    lines.append("knowledge_type: domain")
    if spec["kind"] == "densho:Skill":
        lines += [
            "description: Use this skill for a review.",
            "invocation: agent",
            "skill_type: system",
        ]
    for key in LIST_FIELDS:
        if key in spec:
            lines += [f"{key}:", *[f"  - {value}" for value in spec[key]]]
    if spec.get("exceptions"):
        lines.append("exceptions:")
        for entry in spec["exceptions"]:
            lines += [f"  - directive: {entry['directive']}", f"    reason: {entry['reason']}"]
            lines.append(f"    status: {entry['status']}")
    return lines


def render(spec: Spec, others: list[str]) -> str:
    lines = ["---", *front_matter(spec, others), "---", ""]
    if spec["kind"] not in {"densho:Root", "densho:Skill"}:
        lines += ["## Definition", "", "A meaning.", ""]
    if spec.get("rules"):
        lines += ["## Directives", ""]
        for entry in spec["rules"]:
            lines += directive_lines(entry)
        lines.append("")
    return "\n".join(lines)


def file_of(spec: Spec) -> Path:
    if spec["kind"] == "densho:Root":
        return Path("knowledge/node.md")
    folder = "knowledge/skills" if spec["kind"] == "densho:Skill" else "knowledge/nodes"
    return Path(folder) / spec["id"] / "node.md"


def complete(specs: tuple[Spec, ...]) -> list[Spec]:
    has_root = any(spec["kind"] == "densho:Root" for spec in specs)
    return [*specs] if has_root else [root(), *specs]


def sources(specs: tuple[Spec, ...]) -> dict[str, tuple[Path, str]]:
    everything = complete(specs)
    others = [spec["id"] for spec in everything if spec["kind"] != "densho:Root"]
    return {spec["id"]: (file_of(spec), render(spec, others)) for spec in everything}


def parsed(*specs: Spec) -> list[ParsedNode]:
    items: list[ParsedNode] = []
    for path, text in sources(specs).values():
        result = parse_source(text, path)
        assert isinstance(result, ParsedNode), result
        items.append(result)
    return items


def applied_at(node_id: str, *specs: Spec) -> list[AppliedDirective]:
    return resolve_directives(parsed(*specs)).at(node_id)


def routes_at(node_id: str, *specs: Spec) -> dict[str, tuple[str, ...]]:
    return {entry.directive.id: entry.route for entry in applied_at(node_id, *specs)}


def problems_of(*specs: Spec) -> list[str]:
    return [str(problem) for problem in check_items(parsed(*specs))]


def codes_of(*specs: Spec) -> list[str]:
    return [problem.split(": ")[1] for problem in problems_of(*specs)]


def location(specs: tuple[Spec, ...], node_id: str, text: str) -> str:
    path, source = sources(specs)[node_id]
    numbers = [number for number, line in enumerate(source.split("\n"), 1) if text in line]
    return f"{path}:{numbers[-1]}"


def test_a_subtree_directive_reaches_each_node_under_it() -> None:
    specs = (
        domain("design", rules=[rule("a")]),
        concept("ui", "design"),
        concept("motion", "ui"),
    )
    assert routes_at("design", *specs) == {"a": ("design",)}
    assert routes_at("ui", *specs) == {"a": ("design", "ui")}
    assert routes_at("motion", *specs) == {"a": ("design", "ui", "motion")}


def test_a_directive_does_not_reach_a_parent_or_a_sibling() -> None:
    specs = (domain("design"), concept("ui", "design", rules=[rule("a")]), concept("ux", "design"))
    assert routes_at("design", *specs) == {}
    assert routes_at("ux", *specs) == {}
    assert routes_at("root", *specs) == {}


def test_a_node_directive_stays_on_the_attached_nodes() -> None:
    specs = (
        domain("design", rules=[rule("a", "node", also_attached_to=["ux"])]),
        concept("ui", "design"),
        concept("ux", "design"),
        concept("research", "ux"),
    )
    assert routes_at("design", *specs) == {"a": ("design",)}
    assert routes_at("ui", *specs) == {}
    assert routes_at("ux", *specs) == {"a": ("ux",)}
    assert routes_at("research", *specs) == {}


def test_also_attached_to_starts_a_new_route() -> None:
    specs = (
        domain("design", rules=[rule("a", also_attached_to=["other"])]),
        domain("other"),
        concept("deep", "other"),
    )
    assert routes_at("deep", *specs) == {"a": ("other", "deep")}
    entry = applied_at("deep", *specs)[0]
    assert entry.holder == "design"
    assert entry.directive.id == "a"


def test_a_root_subtree_directive_reaches_each_node() -> None:
    specs = (
        root(rules=[rule("a")]),
        domain("design"),
        concept("ui", "design"),
        skill("review", "ui"),
    )
    assert routes_at("root", *specs) == {"a": ("root",)}
    assert routes_at("design", *specs) == {"a": ("root", "design")}
    assert routes_at("ui", *specs) == {"a": ("root", "design", "ui")}
    assert routes_at("review", *specs) == {"a": ("root", "review")}


def test_a_root_node_directive_stays_on_the_root() -> None:
    specs = (root(rules=[rule("a", "node")]), domain("design"), skill("review", "design"))
    assert routes_at("root", *specs) == {"a": ("root",)}
    assert routes_at("design", *specs) == {}
    assert routes_at("review", *specs) == {}


def test_attaching_to_the_root_covers_the_whole_graph() -> None:
    specs = (
        domain("design", rules=[rule("a", also_attached_to=["root"])]),
        domain("other"),
        concept("deep", "other"),
    )
    assert routes_at("deep", *specs) == {"a": ("root", "other", "deep")}


@pytest.mark.parametrize("field", ["related", "informs", "depends_on", "governs", "implements"])
def test_other_edges_carry_no_directive(field: str) -> None:
    specs = (
        domain("design", rules=[rule("a")]),
        domain("other", **{field: ["design"]}),
        domain("third", rules=[rule("b")], **{field: ["other"]}),
    )
    assert routes_at("other", *specs) == {}
    assert routes_at("design", *specs) == {"a": ("design",)}


def test_two_routes_give_one_result_with_the_shortest_route() -> None:
    specs = (
        domain("design", rules=[rule("a")]),
        concept("left", "design"),
        concept("right", "design"),
        concept("join", "right", "left"),
        concept("short", "design"),
        concept("both", "join", "short"),
    )
    assert routes_at("join", *specs) == {"a": ("design", "left", "join")}
    assert routes_at("both", *specs) == {"a": ("design", "short", "both")}
    assert len(applied_at("both", *specs)) == 1


def test_a_tie_between_two_attached_nodes_has_a_fixed_route() -> None:
    specs = (
        domain("zeta", rules=[rule("a", also_attached_to=["alpha"])]),
        domain("alpha"),
        concept("join", "zeta", "alpha"),
    )
    assert routes_at("join", *specs) == {"a": ("alpha", "join")}


def test_a_ladder_of_diamonds_does_not_list_each_route() -> None:
    specs = [domain("n0", rules=[rule("a")])]
    for rung in range(LADDER_RUNGS):
        specs += [
            concept(f"a{rung}", f"n{rung}"),
            concept(f"b{rung}", f"n{rung}"),
            concept(f"n{rung + 1}", f"a{rung}", f"b{rung}"),
        ]
    route = routes_at(f"n{LADDER_RUNGS}", *specs)["a"]
    assert len(route) == 2 * LADDER_RUNGS + 1
    assert route[:3] == ("n0", "a0", "n1")


def test_two_directives_come_in_order_of_route_then_id() -> None:
    specs = (
        root(rules=[rule("z-broad")]),
        domain("design", rules=[rule("b"), rule("a")]),
        concept("ui", "design", rules=[rule("own")]),
    )
    assert [entry.directive.id for entry in applied_at("ui", *specs)] == [
        "z-broad",
        "a",
        "b",
        "own",
    ]


def test_an_unknown_node_has_no_directives() -> None:
    assert applied_at("missing", domain("design", rules=[rule("a")])) == []


def test_a_deprecated_directive_applies_nowhere() -> None:
    specs = (
        domain("design", rules=[rule("a", status="deprecated", also_attached_to=["other"])]),
        domain("other"),
        concept("ui", "design"),
    )
    assert routes_at("design", *specs) == {}
    assert routes_at("other", *specs) == {}
    assert routes_at("ui", *specs) == {}
    assert problems_of(*specs) == []


def test_a_proposed_directive_is_not_in_force() -> None:
    specs = (domain("design", rules=[rule("a", status="proposed")]), concept("ui", "design"))
    assert routes_at("design", *specs) == {}
    assert routes_at("ui", *specs) == {}
    assert problems_of(*specs) == []


def test_a_proposed_directive_applies_when_the_caller_asks_for_proposals() -> None:
    specs = (domain("design", rules=[rule("a", status="proposed")]), concept("ui", "design"))
    entry = resolve_directives(parsed(*specs), proposals=True).at("ui")[0]
    assert entry.directive.status == "proposed"
    assert entry.route == ("design", "ui")


def test_a_deprecated_directive_stays_out_of_the_proposals() -> None:
    specs = (domain("design", rules=[rule("a", status="deprecated")]),)
    assert resolve_directives(parsed(*specs), proposals=True).at("design") == []


def test_a_proposed_exception_does_not_stop_the_directive() -> None:
    specs = (
        domain("design", rules=[rule("a")]),
        concept("ui", "design", exceptions=[stop("a", "proposed")]),
    )
    assert routes_at("ui", *specs) == {"a": ("design", "ui")}
    assert problems_of(*specs) == []


def test_a_proposed_exception_stops_the_directive_when_the_caller_asks_for_proposals() -> None:
    specs = (
        domain("design", rules=[rule("a")]),
        concept("ui", "design", exceptions=[stop("a", "proposed")]),
    )
    assert resolve_directives(parsed(*specs), proposals=True).at("ui") == []


def test_a_deprecated_exception_stops_nothing_and_passes() -> None:
    specs = (
        domain("design", rules=[rule("a")]),
        concept("ui", "design", exceptions=[stop("a", "deprecated")]),
    )
    assert routes_at("ui", *specs) == {"a": ("design", "ui")}
    assert resolve_directives(parsed(*specs), proposals=True).at("ui") != []
    assert problems_of(*specs) == []


def test_a_deprecated_exception_with_no_route_passes() -> None:
    specs = (
        domain("design"),
        domain("other", rules=[rule("a")]),
        concept("ui", "design", exceptions=[stop("a", "deprecated")]),
    )
    assert problems_of(*specs) == []


def test_a_deprecated_exception_counts_as_a_repeat() -> None:
    specs = (
        domain("design", rules=[rule("a")]),
        concept("ui", "design", exceptions=[stop("a", "deprecated"), stop("a")]),
    )
    assert codes_of(*specs) == ["exception-repeated"]


def test_a_proposed_exception_with_no_route_fails() -> None:
    specs = (
        domain("design"),
        domain("other", rules=[rule("a")]),
        concept("ui", "design", exceptions=[stop("a", "proposed")]),
    )
    assert codes_of(*specs) == ["exception-unused"]


def test_an_exception_for_a_proposed_directive_passes() -> None:
    specs = (
        domain("design", rules=[rule("a", status="proposed")]),
        concept("ui", "design", exceptions=[stop("a", "proposed")]),
    )
    assert problems_of(*specs) == []


def test_a_proposal_that_conflicts_fails_before_a_review() -> None:
    specs = (
        domain("design", rules=[rule("a"), rule("b", status="proposed", conflicts_with=["a"])]),
    )
    assert codes_of(*specs) == ["conflict"]


def test_a_proposal_with_a_proposed_exception_settles_the_conflict_for_review() -> None:
    specs = (
        domain("design", rules=[rule("a")]),
        concept(
            "ui",
            "design",
            exceptions=[stop("a", "proposed")],
            rules=[rule("b", status="proposed", conflicts_with=["a"])],
        ),
    )
    assert problems_of(*specs) == []


def test_accepting_a_rule_before_its_exception_fails_as_a_conflict() -> None:
    specs = (
        domain("design", rules=[rule("a")]),
        concept(
            "ui",
            "design",
            exceptions=[stop("a", "proposed")],
            rules=[rule("b", conflicts_with=["a"])],
        ),
    )
    assert codes_of(*specs) == ["conflict"]


def test_a_proposed_exception_on_one_route_reports_the_route_conflict() -> None:
    specs = (
        domain("design", rules=[rule("a")]),
        concept("ui", "design", exceptions=[stop("a", "proposed")]),
        concept("ux", "design"),
        concept("join", "ui", "ux"),
    )
    assert codes_of(*specs) == ["route-conflict"]


def test_an_accepted_rule_cannot_refine_a_proposed_rule() -> None:
    specs = (domain("design", rules=[rule("a", status="proposed"), rule("b", refines=["a"])]),)
    assert codes_of(*specs) == ["refines-outside"]


def test_a_proposed_rule_can_refine_an_accepted_rule() -> None:
    specs = (domain("design", rules=[rule("a"), rule("b", status="proposed", refines=["a"])]),)
    assert problems_of(*specs) == []


def test_a_proposed_rule_can_refine_a_proposed_rule() -> None:
    specs = (
        domain(
            "design",
            rules=[rule("a", status="proposed"), rule("b", status="proposed", refines=["a"])],
        ),
    )
    assert problems_of(*specs) == []


def test_a_proposed_refinement_outside_the_broader_rule_fails() -> None:
    specs = (
        domain("design"),
        concept("ui", "design", rules=[rule("a")]),
        concept("ux", "design", rules=[rule("b", status="proposed", refines=["a"])]),
    )
    assert codes_of(*specs) == ["refines-outside"]


def test_what_applies_at_a_skill() -> None:
    specs = (
        root(rules=[rule("everywhere"), rule("root-only", "node")]),
        domain(
            "design",
            rules=[rule("broad"), rule("design-only", "node")],
        ),
        concept(
            "ui",
            "design",
            rules=[rule("used-subtree"), rule("used-node", "node")],
        ),
        concept("below", "ui", rules=[rule("below-subtree"), rule("below-node", "node")]),
        domain("other", rules=[rule("named", "node"), rule("unnamed", "node")]),
        skill(
            "review",
            "ui",
            applies=["named"],
            rules=[rule("own", "node")],
        ),
    )
    assert routes_at("review", *specs) == {
        "everywhere": ("root", "review"),
        "broad": ("design", "ui", "review"),
        "used-subtree": ("ui", "review"),
        "used-node": ("ui", "review"),
        "named": ("review",),
        "own": ("review",),
    }


def test_a_skill_can_attach_with_also_attached_to() -> None:
    specs = (
        domain("design"),
        domain("other", rules=[rule("a", "node", also_attached_to=["review"])]),
        skill("review", "design"),
    )
    assert routes_at("review", *specs) == {"a": ("review",)}


def test_nothing_is_under_a_skill() -> None:
    specs = (domain("design"), skill("review", "design", rules=[rule("a")]))
    assert routes_at("design", *specs) == {}
    assert routes_at("root", *specs) == {}


def test_an_exception_stops_a_directive_at_a_node_and_below() -> None:
    specs = (
        domain("design", rules=[rule("a")]),
        concept("ui", "design", exceptions=[stop("a")]),
        concept("motion", "ui"),
        concept("ux", "design"),
    )
    assert routes_at("ui", *specs) == {}
    assert routes_at("motion", *specs) == {}
    assert routes_at("ux", *specs) == {"a": ("design", "ux")}
    assert problems_of(*specs) == []


def test_a_domain_can_step_out_of_a_root_directive() -> None:
    specs = (
        root(rules=[rule("a")]),
        domain("design", exceptions=[stop("a")]),
        concept("ui", "design"),
        domain("other"),
    )
    assert routes_at("ui", *specs) == {}
    assert routes_at("other", *specs) == {"a": ("root", "other")}
    assert problems_of(*specs) == []


def test_a_skill_can_step_out_of_a_directive() -> None:
    specs = (root(rules=[rule("a")]), domain("design"), skill("review", exceptions=[stop("a")]))
    assert routes_at("review", *specs) == {}
    assert problems_of(*specs) == []


def test_a_skill_exception_stops_a_directive_from_a_used_node() -> None:
    specs = (
        domain("design", rules=[rule("a", "node"), rule("b")]),
        skill("review", "design", exceptions=[stop("a"), stop("b")]),
    )
    assert routes_at("review", *specs) == {}
    assert routes_at("design", *specs).keys() == {"a", "b"}
    assert problems_of(*specs) == []


def test_a_used_node_that_steps_out_carries_nothing_to_a_skill() -> None:
    specs = (
        domain("design", rules=[rule("a")]),
        concept("ui", "design", exceptions=[stop("a")]),
        skill("review", "ui"),
    )
    assert routes_at("review", *specs) == {}
    assert problems_of(*specs) == []


def test_an_attachment_under_an_exception_restarts_the_directive() -> None:
    specs = (
        domain("design", rules=[rule("a", also_attached_to=["motion"])]),
        concept("ui", "design", exceptions=[stop("a")]),
        concept("motion", "ui"),
        concept("easing", "motion"),
    )
    assert routes_at("ui", *specs) == {}
    assert routes_at("motion", *specs) == {"a": ("motion",)}
    assert routes_at("easing", *specs) == {"a": ("motion", "easing")}
    assert problems_of(*specs) == []


@pytest.mark.parametrize(
    "extra",
    [
        pytest.param(domain("other", rules=[rule("a")]), id="another branch"),
        pytest.param(concept("sibling", "design", rules=[rule("a")]), id="a sibling"),
        pytest.param(domain("other", rules=[rule("a", "node")]), id="node scope elsewhere"),
    ],
)
def test_an_exception_with_no_route_fails(extra: Spec) -> None:
    specs = (domain("design"), concept("ui", "design", exceptions=[stop("a")]), extra)
    assert problems_of(*specs) == [
        (
            f"{location(specs, 'ui', 'directive: a')}: exception-unused: This exception stops "
            "nothing, because no route brings a to this node. Remove it."
        )
    ]


def test_an_exception_for_a_node_directive_on_a_parent_fails() -> None:
    specs = (
        domain("design", rules=[rule("a", "node")]),
        concept("ui", "design", exceptions=[stop("a")]),
    )
    assert codes_of(*specs) == ["exception-unused"]


def test_an_exception_for_a_deprecated_directive_fails() -> None:
    specs = (
        domain("design", rules=[rule("a", status="deprecated")]),
        concept("ui", "design", exceptions=[stop("a")]),
    )
    assert codes_of(*specs) == ["exception-unused"]


def test_an_exception_under_another_exception_fails() -> None:
    specs = (
        domain("design", rules=[rule("a")]),
        concept("ui", "design", exceptions=[stop("a")]),
        concept("motion", "ui", exceptions=[stop("a")]),
    )
    assert problems_of(*specs) == [
        (
            f"{location(specs, 'motion', 'directive: a')}: exception-unused: This exception stops "
            "nothing, because no route brings a to this node. Remove it."
        )
    ]


@pytest.mark.parametrize(
    "specs",
    [
        pytest.param(
            (domain("design", rules=[rule("a")], exceptions=[stop("a")]),),
            id="the holder",
        ),
        pytest.param(
            (
                domain("design", rules=[rule("a", also_attached_to=["ui"])]),
                concept("ui", "design", exceptions=[stop("a")]),
            ),
            id="an attached node",
        ),
        pytest.param(
            (
                domain("design", rules=[rule("a", "node")]),
                skill("ui", "design", applies=["a"], exceptions=[stop("a")]),
            ),
            id="a skill that applies it",
        ),
    ],
)
def test_a_node_cannot_attach_a_directive_and_step_out_of_it(specs: tuple[Spec, ...]) -> None:
    node_id = "design" if len(specs) == 1 else "ui"
    assert problems_of(*specs) == [
        (
            f"{location(specs, node_id, 'directive: a')}: exception-attached: This node attaches a "
            "and also steps out of it. Remove the exception or the attachment."
        )
    ]


def test_an_attachment_still_applies_when_the_node_steps_out() -> None:
    specs = (domain("design", rules=[rule("a")], exceptions=[stop("a")]), concept("ui", "design"))
    assert routes_at("design", *specs) == {"a": ("design",)}
    assert routes_at("ui", *specs) == {"a": ("design", "ui")}


def test_two_exceptions_for_one_directive_fail() -> None:
    specs = (
        domain("design", rules=[rule("a")]),
        concept("ui", "design", exceptions=[stop("a"), stop("a")]),
    )
    assert problems_of(*specs) == [
        (
            f"{location(specs, 'ui', 'directive: a')}: exception-repeated: This node already has "
            "an exception for a."
        )
    ]


def test_the_exception_problem_points_at_its_own_entry() -> None:
    specs = (
        domain("design", rules=[rule("a")]),
        concept("ui", "design", exceptions=[stop("a"), stop("missing-route")]),
        domain("other", rules=[rule("missing-route")]),
    )
    assert [problem.split(": ")[0] for problem in problems_of(*specs)] == [
        location(specs, "ui", "directive: missing-route")
    ]


def test_an_exception_on_one_route_leaves_the_other_route() -> None:
    specs = (
        domain("design", rules=[rule("a")]),
        concept("left", "design", exceptions=[stop("a")]),
        concept("right", "design"),
        concept("join", "left", "right"),
        concept("below", "join"),
    )
    assert routes_at("join", *specs) == {"a": ("design", "right", "join")}
    assert problems_of(*specs) == [
        (
            f"{location(specs, 'join', 'id: join')}: route-conflict: a still reaches this node, "
            "but its route through left stops. Add an exception here, or attach the directive to "
            "this node."
        )
    ]


def test_an_exception_at_the_join_settles_a_route_conflict() -> None:
    specs = (
        domain("design", rules=[rule("a")]),
        concept("left", "design", exceptions=[stop("a")]),
        concept("right", "design"),
        concept("join", "left", "right", exceptions=[stop("a")]),
        concept("below", "join"),
    )
    assert routes_at("join", *specs) == {}
    assert routes_at("below", *specs) == {}
    assert problems_of(*specs) == []


def test_an_attachment_at_the_join_settles_a_route_conflict() -> None:
    specs = (
        domain("design", rules=[rule("a", also_attached_to=["join"])]),
        concept("left", "design", exceptions=[stop("a")]),
        concept("right", "design"),
        concept("join", "left", "right"),
    )
    assert routes_at("join", *specs) == {"a": ("join",)}
    assert problems_of(*specs) == []


def test_a_route_below_a_stopped_node_also_counts() -> None:
    specs = (
        domain("design", rules=[rule("a")]),
        concept("left", "design", exceptions=[stop("a")]),
        concept("left-child", "left"),
        concept("right", "design"),
        concept("join", "left-child", "right"),
    )
    assert problems_of(*specs) == [
        (
            f"{location(specs, 'join', 'id: join')}: route-conflict: a still reaches this node, "
            "but its route through left-child stops. Add an exception here, or attach the "
            "directive to this node."
        )
    ]


def test_two_stopped_routes_give_one_route_conflict() -> None:
    specs = (
        domain("design", rules=[rule("a")]),
        concept("first", "design", exceptions=[stop("a")]),
        concept("second", "design", exceptions=[stop("a")]),
        concept("right", "design"),
        concept("join", "first", "second", "right"),
    )
    problems = problems_of(*specs)
    assert len(problems) == 1
    assert "its route through first stops" in problems[0]


def test_each_directive_gets_its_own_route_conflict() -> None:
    specs = (
        domain("design", rules=[rule("a"), rule("b")]),
        concept("left", "design", exceptions=[stop("a"), stop("b")]),
        concept("right", "design"),
        concept("join", "left", "right"),
    )
    assert codes_of(*specs) == ["route-conflict", "route-conflict"]


def test_a_skill_with_a_stopped_used_node_and_a_live_route_conflicts() -> None:
    specs = (
        root(rules=[rule("a")]),
        domain("design", exceptions=[stop("a")]),
        skill("review", "design"),
    )
    assert routes_at("review", *specs) == {"a": ("root", "review")}
    assert problems_of(*specs) == [
        (
            f"{location(specs, 'review', 'id: review')}: route-conflict: a still reaches this "
            "node, but its route through design stops. Add an exception here, or attach the "
            "directive to this node."
        )
    ]


def test_applies_settles_a_route_conflict_at_a_skill() -> None:
    specs = (
        root(rules=[rule("a")]),
        domain("design", exceptions=[stop("a")]),
        skill("review", "design", applies=["a"]),
    )
    assert routes_at("review", *specs) == {"a": ("review",)}
    assert problems_of(*specs) == []


def test_a_skill_exception_settles_a_route_conflict() -> None:
    specs = (
        root(rules=[rule("a")]),
        domain("design", exceptions=[stop("a")]),
        skill("review", "design", exceptions=[stop("a")]),
    )
    assert routes_at("review", *specs) == {}
    assert problems_of(*specs) == []


def test_a_skill_with_two_used_nodes_can_conflict() -> None:
    specs = (
        domain("design", rules=[rule("a")]),
        concept("left", "design", exceptions=[stop("a")]),
        concept("right", "design"),
        skill("review", "left", "right"),
    )
    assert codes_of(*specs) == ["route-conflict"]


def test_declared_conflicts_fail_where_both_apply() -> None:
    specs = (
        domain("design", rules=[rule("a", conflicts_with=["b"])]),
        concept("ui", "design", rules=[rule("b")]),
    )
    assert problems_of(*specs) == [
        (
            f"{location(specs, 'design', 'conflicts_with: b')}: conflict: This directive conflicts "
            "with b, and both apply at ui. Add an exception, or change the attachments."
        )
    ]


def test_a_declared_conflict_reads_from_either_side() -> None:
    specs = (
        domain("design", rules=[rule("a")]),
        concept("ui", "design", rules=[rule("b", conflicts_with=["a"])]),
    )
    assert codes_of(*specs) == ["conflict"]


def test_a_declared_conflict_points_at_its_own_entry() -> None:
    specs = (
        domain("design", rules=[rule("a", conflicts_with=["c", "b"])]),
        domain("other", rules=[rule("c")]),
        concept("ui", "design", rules=[rule("b")]),
    )
    assert problems_of(*specs)[0].startswith(location(specs, "design", "conflicts_with: b"))


def test_a_declared_conflict_names_the_first_node_and_the_count() -> None:
    specs = (
        domain("design", rules=[rule("a", conflicts_with=["b"]), rule("b")]),
        concept("ui", "design"),
        concept("ux", "design"),
    )
    assert "both apply at design and 2 more." in problems_of(*specs)[0]


def test_a_declared_conflict_passes_when_the_reaches_do_not_meet() -> None:
    specs = (
        domain("design", rules=[rule("a", conflicts_with=["b"])]),
        domain("other", rules=[rule("b")]),
    )
    assert problems_of(*specs) == []


def test_an_exception_settles_a_declared_conflict() -> None:
    specs = (
        domain("design", rules=[rule("a", conflicts_with=["b"])]),
        concept("ui", "design", rules=[rule("b")], exceptions=[stop("a")]),
    )
    assert problems_of(*specs) == []


def test_a_skill_can_meet_a_declared_conflict_across_branches() -> None:
    specs = (
        domain("design", rules=[rule("a", conflicts_with=["b"])]),
        domain("other", rules=[rule("b")]),
        skill("review", "design", "other"),
    )
    assert "both apply at review." in problems_of(*specs)[0]


def test_a_deprecated_directive_cannot_conflict() -> None:
    specs = (
        domain("design", rules=[rule("a", conflicts_with=["b"])]),
        concept("ui", "design", rules=[rule("b", status="deprecated")]),
    )
    assert problems_of(*specs) == []


def test_a_directive_cannot_conflict_with_itself() -> None:
    assert codes_of(domain("design", rules=[rule("a", conflicts_with=["a"])])) == ["conflict"]


@pytest.mark.parametrize(
    ("positive", "negative"),
    [
        ("Use a mock.", "Do not use a mock."),
        ("Use a `mock`.", "Do not use a `mock`."),
        ("Use a **mock**.", "Do not use a mock."),
        ("Use a  mock.", "do not use a mock."),
        ("If a test fails, stop the release.", "If a test fails, do not stop the release."),
        ("In `tests/`, use a mock.", "In `tests/`, do not use a mock."),
    ],
)
def test_a_rule_and_its_opposite_fail_where_both_apply(positive: str, negative: str) -> None:
    specs = (
        domain("design", rules=[rule("a", text=positive)]),
        concept("ui", "design", rules=[rule("b", text=negative)]),
    )
    assert problems_of(*specs) == [
        (
            f"{location(specs, 'ui', '^b')}: opposite: This directive is the opposite of a, and "
            "both apply at ui."
        )
    ]


def test_each_opposite_pair_is_reported() -> None:
    specs = (
        domain(
            "design",
            rules=[
                rule("a", text="Use a mock."),
                rule("b", text="Use a **mock**."),
                rule("c", text="Do not use a mock."),
            ],
        ),
    )
    assert codes_of(*specs) == ["opposite", "opposite"]


@pytest.mark.parametrize(
    ("first", "second"),
    [
        ("Use a mock.", "Do not use a fixture."),
        ("Use a mock.", "Avoid a mock."),
        ("If you do not know, ask.", "If you know, ask."),
        ("Use a mock.", "Use a mock now."),
    ],
)
def test_other_text_is_not_an_opposite(first: str, second: str) -> None:
    specs = (domain("design", rules=[rule("a", text=first), rule("b", text=second)]),)
    assert problems_of(*specs) == []


def test_opposites_pass_when_the_reaches_do_not_meet() -> None:
    specs = (
        domain("design", rules=[rule("a", text="Use a mock.")]),
        domain("other", rules=[rule("b", text="Do not use a mock.")]),
    )
    assert problems_of(*specs) == []


def test_an_exception_settles_an_opposite() -> None:
    specs = (
        domain("design", rules=[rule("a", text="Use a mock.")]),
        concept(
            "ui",
            "design",
            rules=[rule("b", text="Do not use a mock.")],
            exceptions=[stop("a")],
        ),
    )
    assert problems_of(*specs) == []


def test_an_opposite_at_a_skill_fails() -> None:
    specs = (
        domain("design", rules=[rule("a", text="Use a mock.")]),
        domain("other", rules=[rule("b", text="Do not use a mock.")]),
        skill("review", "design", "other"),
    )
    assert "both apply at review." in problems_of(*specs)[0]


def test_a_narrower_directive_can_refine_a_broader_one() -> None:
    specs = (
        domain("design", rules=[rule("a")]),
        concept("ui", "design", rules=[rule("b", refines=["a"])]),
        concept("motion", "ui"),
    )
    assert problems_of(*specs) == []
    assert routes_at("motion", *specs).keys() == {"a", "b"}


def test_a_directive_can_refine_one_with_the_same_reach() -> None:
    specs = (domain("design", rules=[rule("a", "node"), rule("b", "node", refines=["a"])]),)
    assert problems_of(*specs) == []


def test_a_skill_directive_can_refine_a_directive_of_a_used_node() -> None:
    specs = (
        domain("design", rules=[rule("a", "node")]),
        skill("review", "design", rules=[rule("b", refines=["a"])]),
    )
    assert problems_of(*specs) == []


def test_a_broader_directive_cannot_refine_a_narrower_one() -> None:
    specs = (
        domain("design", rules=[rule("a", refines=["b"])]),
        concept("ui", "design", rules=[rule("b")]),
    )
    assert problems_of(*specs) == [
        (
            f"{location(specs, 'design', 'refines: b')}: refines-outside: This directive refines "
            "b, but b does not apply at design, where this directive applies."
        )
    ]


def test_a_directive_cannot_refine_one_on_a_sibling() -> None:
    specs = (
        domain("design"),
        concept("ui", "design", rules=[rule("a")]),
        concept("ux", "design", rules=[rule("b", refines=["a"])]),
    )
    assert codes_of(*specs) == ["refines-outside"]


def test_refines_needs_the_broader_rule_below_too() -> None:
    specs = (
        domain("design", rules=[rule("a", "node")]),
        concept("ui", "design", rules=[rule("b", refines=["a"])]),
    )
    assert codes_of(*specs) == ["refines-outside"]


def test_a_stopped_broader_directive_breaks_a_refinement() -> None:
    specs = (
        domain("design", rules=[rule("a"), rule("b", refines=["a"])]),
        concept("ui", "design", exceptions=[stop("a")]),
    )
    assert problems_of(*specs) == [
        (
            f"{location(specs, 'design', 'refines: a')}: refines-outside: This directive refines "
            "a, but a does not apply at ui, where this directive applies."
        )
    ]


def test_stopping_both_directives_settles_a_refinement() -> None:
    specs = (
        domain("design", rules=[rule("a"), rule("b", refines=["a"])]),
        concept("ui", "design", exceptions=[stop("a"), stop("b")]),
    )
    assert problems_of(*specs) == []


def test_refining_a_deprecated_directive_fails() -> None:
    specs = (domain("design", rules=[rule("a", status="deprecated"), rule("b", refines=["a"])]),)
    assert codes_of(*specs) == ["refines-outside"]


def test_a_deprecated_directive_can_name_a_refinement() -> None:
    specs = (domain("design", rules=[rule("a"), rule("b", status="deprecated", refines=["a"])]),)
    assert problems_of(*specs) == []


def test_the_refinement_problem_points_at_its_own_entry() -> None:
    specs = (
        domain("design", rules=[rule("a", refines=["c", "b"]), rule("c")]),
        concept("ui", "design", rules=[rule("b")]),
    )
    assert problems_of(*specs)[0].startswith(location(specs, "design", "refines: b"))


def test_refines_and_conflicts_with_on_one_pair_always_fail() -> None:
    specs = (domain("design", rules=[rule("a"), rule("b", refines=["a"], conflicts_with=["a"])]),)
    assert codes_of(*specs) == ["conflict"]


def test_a_directive_cannot_refine_itself() -> None:
    specs = (domain("design", rules=[rule("a", refines=["a"])]),)
    assert problems_of(*specs) == [
        (
            f"{location(specs, 'design', 'refines: a')}: refines-cycle: The refines edges close a "
            "cycle through a."
        )
    ]


def test_a_chain_of_refines_cannot_close() -> None:
    specs = (
        domain(
            "design",
            rules=[
                rule("a", refines=["other", "b"]),
                rule("b", refines=["c"]),
                rule("c", refines=["a"]),
                rule("other"),
                rule("unrelated", refines=["a"]),
            ],
        ),
    )
    assert problems_of(*specs) == [
        (
            f"{location(specs, 'design', 'refines: b')}: refines-cycle: The refines edges close a "
            "cycle through a, b, c."
        )
    ]


def test_a_skill_cannot_apply_a_deprecated_directive() -> None:
    specs = (
        domain("design", rules=[rule("a", status="deprecated"), rule("c")]),
        skill("review", "design", applies=["c", "a"]),
    )
    item = next(item for item in parsed(*specs) if item.node.id == "review")
    assert problems_of(*specs) == [
        (
            f"{item.path}:{item.line_of(('applies', 1))}: applies-deprecated: This skill applies "
            "a, which is deprecated. Remove it from applies."
        )
    ]


def test_problems_have_a_stable_order() -> None:
    specs = [
        domain(
            f"node{number:02}",
            rules=[rule(f"a{number:02}", conflicts_with=[f"b{number:02}"]), rule(f"b{number:02}")],
        )
        for number in range(PAIRS)
    ]
    problems = check_items(parsed(*specs))
    assert len(problems) == PAIRS
    assert problems == sorted(problems)


def test_a_tree_with_no_directives_passes() -> None:
    assert problems_of(domain("design"), skill("review", "design")) == []


def test_no_items_pass() -> None:
    assert check_items([]) == []
    assert resolve_directives([]).at("root") == []


MUST_FAIL: dict[str, tuple[Spec, ...]] = {
    "exception-unused": (domain("design", exceptions=[stop("a")]), domain("b", rules=[rule("a")])),
    "exception-attached": (domain("design", rules=[rule("a")], exceptions=[stop("a")]),),
    "exception-repeated": (
        domain("design", rules=[rule("a")]),
        concept("ui", "design", exceptions=[stop("a"), stop("a")]),
    ),
    "route-conflict": (
        domain("design", rules=[rule("a")]),
        concept("left", "design", exceptions=[stop("a")]),
        concept("right", "design"),
        concept("join", "left", "right"),
    ),
    "conflict": (domain("design", rules=[rule("a", conflicts_with=["b"]), rule("b")]),),
    "opposite": (
        domain(
            "design",
            rules=[rule("a", text="Use a mock."), rule("b", text="Do not use a mock.")],
        ),
    ),
    "refines-outside": (
        domain("design", rules=[rule("a", refines=["b"])]),
        concept("ui", "design", rules=[rule("b")]),
    ),
    "refines-cycle": (domain("design", rules=[rule("a", refines=["a"])]),),
    "applies-deprecated": (
        domain("design", rules=[rule("a", status="deprecated")]),
        skill("review", "design", applies=["a"]),
    ),
}


def test_each_code_has_a_must_fail_input() -> None:
    assert set(MUST_FAIL) == set(DIRECTIVE_CODES)


@pytest.mark.parametrize("code", DIRECTIVE_CODES)
def test_the_must_fail_input_gives_only_its_code(code: str) -> None:
    assert codes_of(*MUST_FAIL[code]) == [code]


@pytest.mark.parametrize("code", DIRECTIVE_CODES)
def test_each_code_comes_through_the_graph_checks(tmp_path: Path, code: str) -> None:
    write_repository(tmp_path, *MUST_FAIL[code])
    assert repository_codes(tmp_path) == [code]


def write_repository(repository: Path, *specs: Spec) -> None:
    (repository / "knowledge").mkdir(exist_ok=True)
    for path, text in sources(specs).values():
        target = repository / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")


def repository_codes(repository: Path) -> list[str]:
    return [problem.code for problem in check_directives(repository)[1]]


def test_an_empty_tree_passes(tmp_path: Path) -> None:
    write_repository(tmp_path)
    (tmp_path / "knowledge/node.md").unlink()
    assert check_directives(tmp_path) == (0, [])


def test_a_sound_tree_passes_and_counts_each_directive(tmp_path: Path) -> None:
    write_repository(
        tmp_path,
        domain("design", rules=[rule("a"), rule("b", "node")]),
        concept("ui", "design", rules=[rule("c", refines=["a"])]),
        skill("review", "ui", applies=["b"]),
    )
    assert check_directives(tmp_path) == (3, [])


def test_a_directive_problem_prints_with_its_location(tmp_path: Path) -> None:
    specs = (
        domain("design", rules=[rule("a")]),
        concept("ui", "design", exceptions=[stop("a")]),
        concept("ux", "design"),
        concept("join", "ui", "ux"),
    )
    write_repository(tmp_path, *specs)
    count, problems = check_directives(tmp_path)
    assert count == 1
    assert [problem.code for problem in problems] == ["route-conflict"]
    assert problems[0].path == tmp_path / "knowledge/nodes/join/node.md"


def test_a_parse_problem_stops_the_directive_checks(tmp_path: Path) -> None:
    write_repository(
        tmp_path,
        domain("design", rules=[rule("a", refines=["a"])]),
    )
    path = tmp_path / "knowledge/nodes/design/node.md"
    path.write_text(path.read_text(encoding="utf-8").replace("status: accepted", "status: ok"))
    count, problems = check_directives(tmp_path)
    assert count == 0
    assert {problem.code for problem in problems} == {"schema"}


@pytest.mark.parametrize(
    ("spec", "text"),
    [
        (domain("design", rules=[rule("a", refines=["missing"])]), "refines: missing"),
        (
            domain("design", rules=[rule("a", conflicts_with=["missing"])]),
            "conflicts_with: missing",
        ),
        (domain("design", exceptions=[stop("missing")]), "directive: missing"),
    ],
    ids=["refines", "conflicts_with", "exception"],
)
def test_a_dangling_reference_stops_the_directive_checks(
    tmp_path: Path, spec: Spec, text: str
) -> None:
    specs = (spec,)
    write_repository(tmp_path, *specs)
    count, problems = check_directives(tmp_path)
    assert count == 0
    assert [problem.code for problem in problems] == ["reference"]
    assert (
        f"{tmp_path / location(specs, 'design', text)}" == f"{problems[0].path}:{problems[0].line}"
    )
    assert "'missing'" in problems[0].message


@pytest.mark.parametrize(
    ("spec", "text", "field"),
    [
        (domain("design", rules=[rule("a", refines=["other"])]), "refines: other", "refines"),
        (
            domain("design", rules=[rule("a", conflicts_with=["other"])]),
            "conflicts_with: other",
            "conflicts_with",
        ),
        (domain("design", exceptions=[stop("other")]), "directive: other", "directive"),
    ],
    ids=["refines", "conflicts_with", "exception"],
)
def test_a_reference_to_a_node_is_a_type_problem(
    tmp_path: Path, spec: Spec, text: str, field: str
) -> None:
    specs = (spec, domain("other"))
    write_repository(tmp_path, *specs)
    count, problems = check_directives(tmp_path)
    assert count == 0
    assert [str(problem).split(tmp_path.as_posix() + "/")[1] for problem in problems] == [
        (
            f"{location(specs, 'design', text)}: type: {field} cannot name other, which has kind "
            "densho:Domain."
        )
    ]


def test_the_type_problem_finds_the_right_exception(tmp_path: Path) -> None:
    specs = (
        domain("design", exceptions=[stop("a"), stop("other")]),
        domain("other", rules=[rule("a")]),
    )
    write_repository(tmp_path, *specs)
    assert (
        str(check_directives(tmp_path)[1][0])
        .split(tmp_path.as_posix() + "/")[1]
        .startswith(f"{location(specs, 'design', 'directive: other')}: type: ")
    )


def test_a_graph_problem_stops_the_directive_checks(tmp_path: Path) -> None:
    write_repository(
        tmp_path,
        domain("design", rules=[rule("a", conflicts_with=["a"])]),
        concept("ui", "ui"),
    )
    assert "conflict" not in repository_codes(tmp_path)
    assert "cycle" in repository_codes(tmp_path)


def test_references_of_reads_each_new_field() -> None:
    specs = (
        domain("design", rules=[rule("a", refines=["b"], conflicts_with=["c"])]),
        domain(
            "other",
            rules=[rule("b"), rule("c")],
            exceptions=[stop("a")],
        ),
    )
    found = {
        (reference.field, reference.target, reference.field_path)
        for item in parsed(*specs)
        for reference in references_of(item)
    }
    assert ("refines", "b", ("directives", 0, "refines", 0)) in found
    assert ("conflicts_with", "c", ("directives", 0, "conflicts_with", 0)) in found
    assert ("directive", "a", ("exceptions", 0, "directive")) in found


def test_a_dangling_exception_reports_its_own_line(tmp_path: Path) -> None:
    specs = (
        domain("design", rules=[rule("a")]),
        concept("ui", "design", exceptions=[stop("a"), stop("missing")]),
    )
    write_repository(tmp_path, *specs)
    problem = check_directives(tmp_path)[1][0]
    assert f"{problem.path}:{problem.line}" == str(
        tmp_path / location(specs, "ui", "directive: missing")
    )


@pytest.mark.parametrize(
    "front",
    [
        "exceptions: a\n",
        "exceptions:\n  - a\n",
        (
            "exceptions:\n  - directive: a\n    reason: A reason.\n"
            "    status: accepted\n    extra: 1\n"
        ),
        "exceptions:\n  - directive: a\n    reason: 12\n    status: accepted\n",
        "exceptions:\n  - directive: [a]\n    reason: A reason.\n    status: accepted\n",
        'exceptions:\n  - directive: a\n    reason: "Two\\nlines."\n    status: accepted\n',
        "exceptions:\n  - directive: a\n    reason: A reason.\n    status: maybe\n",
    ],
    ids=["a string", "a string entry", "an extra key", "a number", "a list", "two lines", "status"],
)
def test_a_bad_exception_is_a_schema_problem(front: str) -> None:
    source = sources((domain("design"),))["design"][1]
    result = parse_source(source.replace("---\n\n", f"{front}---\n\n", 1), Path("node.md"))
    assert isinstance(result, list)
    assert {problem.code for problem in result} == {"schema"}


def test_a_root_cannot_hold_an_exception() -> None:
    source = sources((root(), domain("design")))["root"][1]
    text = (
        source.removesuffix("---\n")
        + "exceptions:\n  - directive: a\n    reason: No.\n    status: accepted\n---\n"
    )
    result = parse_source(text, Path("knowledge/node.md"))
    assert isinstance(result, list)
    assert [problem.code for problem in result] == ["schema"]
    assert "exceptions" in result[0].message


@pytest.mark.parametrize(
    ("entry", "missing"),
    [
        ("directive: a\n    reason: A reason.", "status"),
        ("directive: a\n    status: accepted", "reason"),
        ("reason: A reason.\n    status: accepted", "directive"),
    ],
)
def test_an_exception_needs_each_field(entry: str, missing: str) -> None:
    source = sources((domain("design"),))["design"][1]
    text = source.replace("---\n\n", f"exceptions:\n  - {entry}\n---\n\n", 1)
    result = parse_source(text, Path("knowledge/nodes/design/node.md"))
    assert isinstance(result, list)
    assert [problem.code for problem in result] == ["schema"]
    assert f"exceptions[0].{missing}" in result[0].message
    assert (
        result[0].line == text.split("\n").index(f"  - {entry.split(chr(10), maxsplit=1)[0]}") + 1
    )


@pytest.mark.parametrize("key", ["refines", "conflicts_with"])
def test_a_directive_reads_repeated_values(key: str) -> None:
    fields: Spec = {key: ["b", "c"]}
    item = parsed(domain("design", rules=[rule("a", **fields)]))[1]
    directive = (item.node.directives or [])[0]
    assert getattr(directive, key) == ["b", "c"]


@pytest.mark.parametrize("proposals", [False, True])
def test_a_directive_does_not_reach_a_rejected_node_or_its_children(proposals: bool) -> None:  # noqa: FBT001
    specs = (
        domain("design", rules=[rule("a", status="proposed" if proposals else "accepted")]),
        concept("ui", "design"),
        concept("old", "design", status="rejected"),
        concept("deep", "old"),
    )
    resolution = resolve_directives(parsed(*specs), proposals=proposals)
    assert [entry.route for entry in resolution.at("ui")] == [("design", "ui")]
    assert resolution.at("old") == []
    assert resolution.at("deep") == []


def test_a_directive_of_a_rejected_node_applies_nowhere() -> None:
    specs = (
        domain("old", status="rejected", rules=[rule("a", also_attached_to=["other"])]),
        domain("other"),
        concept("ui", "old"),
    )
    for proposals in (False, True):
        resolution = resolve_directives(parsed(*specs), proposals=proposals)
        assert [resolution.at(node_id) for node_id in ("old", "other", "ui")] == [[], [], []]


def test_a_rejected_skill_applies_nothing() -> None:
    specs = (
        domain("design", rules=[rule("a", "node")]),
        skill("review", "design", applies=["a"], status="rejected"),
    )
    assert routes_at("review", *specs) == {}
    assert routes_at("design", *specs) == {"a": ("design",)}


def test_a_rejected_node_does_not_attach_a_directive() -> None:
    specs = (
        domain("design", rules=[rule("a", "node", also_attached_to=["old"])]),
        domain("old", status="rejected"),
    )
    assert routes_at("old", *specs) == {}


def test_a_rejected_exception_does_not_stop_the_directive() -> None:
    specs = (
        domain("design", rules=[rule("a")]),
        concept("ui", "design", exceptions=[stop("a", "rejected")]),
    )
    assert routes_at("ui", *specs) == {"a": ("design", "ui")}
    assert resolve_directives(parsed(*specs), proposals=True).at("ui") != []
    assert problems_of(*specs) == []


def test_a_rejected_exception_with_no_route_passes() -> None:
    specs = (
        domain("design"),
        domain("other", rules=[rule("a")]),
        concept("ui", "design", exceptions=[stop("a", "rejected")]),
    )
    assert problems_of(*specs) == []


def test_an_exception_in_a_rejected_node_is_not_checked() -> None:
    specs = (
        domain("design"),
        domain("other", rules=[rule("a")]),
        concept("old", "design", status="rejected", exceptions=[stop("a", "proposed")]),
    )
    assert problems_of(*specs) == []


def test_a_rejected_node_does_not_stop_a_directive_for_a_live_node() -> None:
    specs = (
        domain("design", rules=[rule("a")]),
        concept("old", "design", status="rejected", exceptions=[stop("a")]),
        concept("ui", "design"),
    )
    assert routes_at("ui", *specs) == {"a": ("design", "ui")}
