from typing import Any

import pytest
from pydantic import BaseModel, ValidationError

from engine.generated.metamodel import (
    AlwaysPointer,
    Concept,
    Directive,
    DirectiveException,
    Discipline,
    Domain,
    KnowledgeGraph,
    PathPointer,
    PracticeArea,
    Root,
    Skill,
    SkillPointer,
    TextPointer,
)

Sample = dict[str, Any]

GOVERNED: Sample = {"id": "sample", "status": "accepted", "origin": "template"}
NODE: Sample = {**GOVERNED, "title": "Sample"}
TAXONOMY: Sample = {**NODE, "knowledge_type": "domain", "definition": "A sample node."}

TEXT_POINTER: Sample = {"kind": "ka:TextPointer", "target": "other", "trigger": "When X happens."}
PATH_POINTER: Sample = {**TEXT_POINTER, "kind": "ka:PathPointer", "paths": ["src/**"]}
ALWAYS_POINTER: Sample = {**TEXT_POINTER, "kind": "ka:AlwaysPointer"}
SKILL_POINTER: Sample = {**TEXT_POINTER, "kind": "ka:SkillPointer"}
DIRECTIVE: Sample = {**GOVERNED, "text": "Use X.", "scope": "node", "basis": "judgment"}

ROOT: Sample = {**NODE, "kind": "ka:Root", "pointers": [TEXT_POINTER]}
DOMAIN: Sample = {**TAXONOMY, "kind": "ka:Domain"}
DISCIPLINE: Sample = {**TAXONOMY, "kind": "ka:Discipline", "broader": ["other"]}
PRACTICE_AREA: Sample = {**TAXONOMY, "kind": "ka:PracticeArea", "broader": ["other"]}
CONCEPT: Sample = {**TAXONOMY, "kind": "ka:Concept", "broader": ["other"]}
SKILL: Sample = {
    **NODE,
    "kind": "ka:Skill",
    "knowledge_type": "domain",
    "description": "Use this skill for X.",
    "invocation": "agent",
    "uses": ["other"],
}

KNOWLEDGE_SAMPLES: list[tuple[type[BaseModel], Sample]] = [
    (Domain, DOMAIN),
    (Discipline, DISCIPLINE),
    (PracticeArea, PRACTICE_AREA),
    (Concept, CONCEPT),
    (Skill, SKILL),
]
NODE_SAMPLES = [(Root, ROOT), *KNOWLEDGE_SAMPLES]
POINTER_SAMPLES: list[tuple[type[BaseModel], Sample]] = [
    (AlwaysPointer, ALWAYS_POINTER),
    (PathPointer, PATH_POINTER),
    (SkillPointer, SKILL_POINTER),
    (TextPointer, TEXT_POINTER),
]
KIND_SAMPLES = [*NODE_SAMPLES, *POINTER_SAMPLES]
ALL_SAMPLES = [*KIND_SAMPLES, (Directive, DIRECTIVE)]
ID_SAMPLES: list[tuple[type[BaseModel], Sample]] = [(Domain, DOMAIN), (Directive, DIRECTIVE)]

BAD_SLUGS = [
    "",
    "Upper",
    "snake_case",
    "a.b",
    "a/b",
    "knowledge/nodes/a/node.md",
    "-a",
    "a-",
    "a--b",
    "1a",
    "newline-at-end\n",
]
BAD_LINES = [
    "",
    " ",
    " leading",
    "trailing ",
    "two\nlines",
    "newline at end\n",
    "carriage\rreturn",
    "tab\tinside",
    "vertical\vtab",
    "form\ffeed",
    "next\x85line",
    "line\u2028separator",
    "paragraph\u2029separator",
]


def errors_of(model: type[BaseModel], data: Sample) -> set[tuple[str, str]]:
    with pytest.raises(ValidationError) as caught:
        model.model_validate(data)
    return {(str(e["loc"][-1]), e["type"]) for e in caught.value.errors()}


def graph_of(*nodes: Sample) -> Sample:
    return {"root": ROOT, "nodes": list(nodes)}


def without(sample: Sample, field: str) -> Sample:
    return {key: value for key, value in sample.items() if key != field}


def sample_id(value: object) -> str | None:
    return value.__name__ if isinstance(value, type) else None


@pytest.mark.parametrize(("model", "sample"), ALL_SAMPLES, ids=sample_id)
def test_valid_sample_round_trips(model: type[BaseModel], sample: Sample) -> None:
    assert model.model_validate(sample).model_dump(exclude_none=True) == sample


@pytest.mark.parametrize(("model", "sample"), KNOWLEDGE_SAMPLES, ids=sample_id)
def test_graph_selects_node_class_from_kind(model: type[BaseModel], sample: Sample) -> None:
    graph = KnowledgeGraph.model_validate(graph_of(sample))
    assert type(graph.nodes[0]) is model


@pytest.mark.parametrize(("model", "sample"), POINTER_SAMPLES, ids=sample_id)
def test_node_selects_pointer_class_from_kind(model: type[BaseModel], sample: Sample) -> None:
    root = Root.model_validate({**ROOT, "pointers": [sample]})
    assert type(root.pointers[0]) is model


@pytest.mark.parametrize(("model", "sample"), NODE_SAMPLES, ids=sample_id)
@pytest.mark.parametrize("field", ["id", "kind", "status", "origin", "title"])
def test_node_requires_field(model: type[BaseModel], sample: Sample, field: str) -> None:
    assert (field, "missing") in errors_of(model, without(sample, field))


@pytest.mark.parametrize(("model", "sample"), POINTER_SAMPLES, ids=sample_id)
@pytest.mark.parametrize("field", ["kind", "target", "trigger"])
def test_pointer_requires_field(model: type[BaseModel], sample: Sample, field: str) -> None:
    assert (field, "missing") in errors_of(model, without(sample, field))


@pytest.mark.parametrize("field", ["id", "status", "origin", "text", "scope"])
def test_directive_requires_field(field: str) -> None:
    assert (field, "missing") in errors_of(Directive, without(DIRECTIVE, field))


@pytest.mark.parametrize(
    ("model", "sample", "field"),
    [
        (Domain, DOMAIN, "definition"),
        (Domain, DOMAIN, "knowledge_type"),
        (Discipline, DISCIPLINE, "broader"),
        (PracticeArea, PRACTICE_AREA, "broader"),
        (Concept, CONCEPT, "broader"),
        (Concept, CONCEPT, "definition"),
        (Concept, CONCEPT, "knowledge_type"),
        (Skill, SKILL, "description"),
        (Skill, SKILL, "knowledge_type"),
        (Root, ROOT, "pointers"),
        (PathPointer, PATH_POINTER, "paths"),
    ],
)
def test_kind_requires_field(model: type[BaseModel], sample: Sample, field: str) -> None:
    assert (field, "missing") in errors_of(model, without(sample, field))


@pytest.mark.parametrize(
    ("model", "sample", "field"),
    [
        (Root, ROOT, "pointers"),
        (Discipline, DISCIPLINE, "broader"),
        (PracticeArea, PRACTICE_AREA, "broader"),
        (Concept, CONCEPT, "broader"),
        (PathPointer, PATH_POINTER, "paths"),
    ],
)
def test_required_list_is_not_empty(model: type[BaseModel], sample: Sample, field: str) -> None:
    assert (field, "too_short") in errors_of(model, {**sample, field: []})


def test_graph_requires_a_knowledge_node() -> None:
    assert ("nodes", "too_short") in errors_of(KnowledgeGraph, graph_of())


def test_graph_requires_a_root() -> None:
    assert ("root", "missing") in errors_of(KnowledgeGraph, {"nodes": [DOMAIN]})


def test_graph_rejects_second_root() -> None:
    errors = errors_of(KnowledgeGraph, graph_of(ROOT))
    assert ("kind", "literal_error") in errors


def test_graph_rejects_knowledge_node_as_root() -> None:
    errors = errors_of(KnowledgeGraph, {"root": DOMAIN, "nodes": [DOMAIN]})
    assert ("kind", "literal_error") in errors


def test_skill_can_name_only_directives() -> None:
    data = {**without(SKILL, "uses"), "applies": ["a-directive"]}
    assert Skill.model_validate(data).model_dump(exclude_none=True) == data


@pytest.mark.parametrize(
    ("model", "sample", "field", "value"),
    [
        (Concept, CONCEPT, "unknown_edge", ["other"]),
        (Domain, DOMAIN, "broader", ["other"]),
        (Root, ROOT, "broader", ["other"]),
        (Root, ROOT, "knowledge_type", "domain"),
        (Root, ROOT, "related", ["other"]),
        (Root, ROOT, "governs", ["other"]),
        (Skill, SKILL, "governs", ["other"]),
        (Concept, CONCEPT, "uses", ["other"]),
        (Skill, SKILL, "broader", ["other"]),
        (Directive, DIRECTIVE, "broader", ["other"]),
        (TextPointer, TEXT_POINTER, "paths", ["src/**"]),
        (AlwaysPointer, ALWAYS_POINTER, "paths", ["src/**"]),
        (SkillPointer, SKILL_POINTER, "paths", ["src/**"]),
    ],
)
def test_field_is_not_allowed(
    model: type[BaseModel],
    sample: Sample,
    field: str,
    value: object,
) -> None:
    assert (field, "extra_forbidden") in errors_of(model, {**sample, field: value})


@pytest.mark.parametrize(
    ("model", "sample", "field"),
    [
        (Concept, CONCEPT, "status"),
        (Concept, CONCEPT, "origin"),
        (Concept, CONCEPT, "knowledge_type"),
        (Skill, SKILL, "knowledge_type"),
        (Directive, DIRECTIVE, "status"),
        (Directive, DIRECTIVE, "origin"),
        (Directive, DIRECTIVE, "scope"),
    ],
)
def test_vocabulary_rejects_unknown_value(
    model: type[BaseModel],
    sample: Sample,
    field: str,
) -> None:
    assert (field, "enum") in errors_of(model, {**sample, field: "unknown"})


@pytest.mark.parametrize(
    ("model", "sample", "field", "value"),
    [
        (Concept, CONCEPT, "status", "proposed"),
        (Concept, CONCEPT, "status", "accepted"),
        (Concept, CONCEPT, "status", "deprecated"),
        (Concept, CONCEPT, "origin", "template"),
        (Concept, CONCEPT, "origin", "project"),
        (Concept, CONCEPT, "knowledge_type", "domain"),
        (Concept, CONCEPT, "knowledge_type", "workspace"),
        (Directive, DIRECTIVE, "scope", "node"),
        (Directive, DIRECTIVE, "scope", "subtree"),
    ],
)
def test_vocabulary_accepts_value(
    model: type[BaseModel],
    sample: Sample,
    field: str,
    value: str,
) -> None:
    assert model.model_validate({**sample, field: value}).model_dump()[field] == value


@pytest.mark.parametrize(("model", "sample"), KIND_SAMPLES, ids=sample_id)
def test_kind_must_match_class(model: type[BaseModel], sample: Sample) -> None:
    assert ("kind", "literal_error") in errors_of(model, {**sample, "kind": "Unknown"})


@pytest.mark.parametrize(
    "node",
    [
        {**DOMAIN, "kind": "ka:Unknown"},
        {**DOMAIN, "kind": "Domain"},
        {**NODE, "kind": "ka:Node"},
        {**NODE, "kind": "ka:KnowledgeNode", "knowledge_type": "domain"},
        {**TAXONOMY, "kind": "ka:TaxonomyNode"},
        {**TAXONOMY, "kind": "skos:Concept"},
    ],
    ids=lambda node: node["kind"],
)
def test_graph_rejects_kind_without_concrete_class(node: Sample) -> None:
    errors = errors_of(KnowledgeGraph, graph_of(node))
    assert ("kind", "literal_error") in errors
    assert ("kind", "missing") not in errors


def test_graph_rejects_node_without_kind() -> None:
    assert ("kind", "missing") in errors_of(KnowledgeGraph, graph_of(without(DOMAIN, "kind")))


@pytest.mark.parametrize("kind", ["ka:Unknown", "TextPointer", "ka:Pointer"])
def test_node_rejects_pointer_kind_without_concrete_class(kind: str) -> None:
    pointer = {**TEXT_POINTER, "kind": kind}
    assert ("kind", "literal_error") in errors_of(Root, {**ROOT, "pointers": [pointer]})


@pytest.mark.parametrize("slug", ["a", "a1", "information-hierarchy", "a-2-b"])
def test_id_accepts_slug(slug: str) -> None:
    assert Domain.model_validate({**DOMAIN, "id": slug}).id == slug


@pytest.mark.parametrize("slug", BAD_SLUGS)
@pytest.mark.parametrize(("model", "sample"), ID_SAMPLES, ids=sample_id)
def test_id_rejects_non_slug(model: type[BaseModel], sample: Sample, slug: str) -> None:
    assert ("id", "value_error") in errors_of(model, {**sample, "id": slug})


@pytest.mark.parametrize("value", BAD_LINES)
@pytest.mark.parametrize(
    ("model", "sample", "field"),
    [
        (Domain, DOMAIN, "title"),
        (Directive, DIRECTIVE, "text"),
        (TextPointer, TEXT_POINTER, "trigger"),
        (Skill, SKILL, "description"),
    ],
)
def test_single_line_field_rejects_value(
    model: type[BaseModel],
    sample: Sample,
    field: str,
    value: str,
) -> None:
    assert (field, "value_error") in errors_of(model, {**sample, field: value})


@pytest.mark.parametrize("value", BAD_LINES)
@pytest.mark.parametrize(
    ("model", "sample", "field"),
    [(PathPointer, PATH_POINTER, "paths"), (Domain, DOMAIN, "sources")],
)
def test_single_line_list_rejects_value(
    model: type[BaseModel],
    sample: Sample,
    field: str,
    value: str,
) -> None:
    assert (field, "value_error") in errors_of(model, {**sample, field: [value]})


@pytest.mark.parametrize("value", ["", " ", "\n"])
@pytest.mark.parametrize("field", ["definition", "body"])
def test_prose_field_rejects_blank(field: str, value: str) -> None:
    assert (field, "value_error") in errors_of(Domain, {**DOMAIN, field: value})


@pytest.mark.parametrize("field", ["definition", "body"])
def test_prose_field_accepts_several_lines(field: str) -> None:
    text = "First line.\nSecond line."
    assert Domain.model_validate({**DOMAIN, field: text}).model_dump()[field] == text


@pytest.mark.parametrize(("model", "sample"), NODE_SAMPLES, ids=sample_id)
def test_each_kind_holds_prose(model: type[BaseModel], sample: Sample) -> None:
    data = {**sample, "body": "Supporting prose."}
    assert model.model_validate(data).model_dump(exclude_none=True) == data


@pytest.mark.parametrize(("model", "sample"), NODE_SAMPLES, ids=sample_id)
def test_directive_attaches_to_each_kind(model: type[BaseModel], sample: Sample) -> None:
    data = {**sample, "directives": [{**DIRECTIVE, "also_attached_to": ["other"]}]}
    assert model.model_validate(data).model_dump(exclude_none=True) == data


EXCEPTION: Sample = {
    "directive": "other",
    "reason": "This node holds a prototype.",
    "status": "proposed",
}


@pytest.mark.parametrize("field", ["directive", "reason", "status"])
def test_exception_requires_field(field: str) -> None:
    assert (field, "missing") in errors_of(DirectiveException, without(EXCEPTION, field))


def test_exception_rejects_an_unknown_field() -> None:
    assert ("extra", "extra_forbidden") in errors_of(DirectiveException, {**EXCEPTION, "extra": 1})


@pytest.mark.parametrize("reason", ["", " a", "a ", "a\nb", "a\n", "a\tb"])
def test_exception_reason_is_one_line(reason: str) -> None:
    assert errors_of(DirectiveException, {**EXCEPTION, "reason": reason})


@pytest.mark.parametrize(("model", "sample"), KNOWLEDGE_SAMPLES, ids=sample_id)
def test_knowledge_node_accepts_exceptions(model: type[BaseModel], sample: Sample) -> None:
    node = model.model_validate({**sample, "exceptions": [EXCEPTION]})
    assert getattr(node, "exceptions") == [DirectiveException(**EXCEPTION)]  # noqa: B009


def test_root_rejects_exceptions() -> None:
    assert ("exceptions", "extra_forbidden") in errors_of(Root, {**ROOT, "exceptions": [EXCEPTION]})


@pytest.mark.parametrize("field", ["refines", "conflicts_with", "also_attached_to"])
def test_directive_accepts_a_list_of_references(field: str) -> None:
    directive = Directive.model_validate({**DIRECTIVE, field: ["other"]})
    assert getattr(directive, field) == ["other"]
    assert errors_of(Directive, {**DIRECTIVE, field: "other"})
