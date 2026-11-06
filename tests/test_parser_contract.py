# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingTypeStubs=false, reportOptionalMemberAccess=false
from pathlib import Path
from typing import TYPE_CHECKING, get_args

import pytest
from linkml_runtime.utils.schemaview import SchemaView

from engine.parser.node import MARKDOWN_FIELDS, NODE_CLASSES, POINTER_CLASSES

if TYPE_CHECKING:
    from pydantic import BaseModel

SCHEMA = Path(__file__).resolve().parents[1] / "knowledge/governance/schema/metamodel.yaml"
VIEW = SchemaView(str(SCHEMA))


def concrete_descendants(name: str) -> set[str]:
    return {
        descendant
        for descendant in VIEW.class_descendants(name)
        if not VIEW.get_class(descendant).abstract
    }


def test_parser_handles_each_concrete_node_class() -> None:
    assert {model.__name__ for model in NODE_CLASSES} == concrete_descendants("Node")


def test_parser_handles_each_concrete_pointer_class() -> None:
    assert {model.__name__ for model in POINTER_CLASSES} == concrete_descendants("Pointer")


@pytest.mark.parametrize("model", [*NODE_CLASSES, *POINTER_CLASSES])
def test_the_curie_of_each_class_is_a_valid_kind(model: type[BaseModel]) -> None:
    assert f"ka:{model.__name__}" in get_args(model.model_fields["kind"].annotation)


def test_markdown_fields_are_schema_slots() -> None:
    node_slots = {slot.name for slot in VIEW.class_induced_slots("TaxonomyNode")}
    assert set(MARKDOWN_FIELDS) <= node_slots
