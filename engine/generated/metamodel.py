from __future__ import annotations

import re
import sys
from datetime import (
    date,
    datetime,
    time
)
from decimal import Decimal
from enum import Enum
from typing import (
    Any,
    ClassVar,
    Literal,
    Optional,
    Union
)

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    SerializationInfo,
    SerializerFunctionWrapHandler,
    field_validator,
    model_serializer
)


metamodel_version = "1.12.0"
version = "0.1.0"


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        serialize_by_alias = True,
        validate_by_name = True,
        validate_assignment = True,
        validate_default = True,
        extra = "forbid",
        arbitrary_types_allowed = True,
        use_enum_values = True,
        strict = False,
    )





class LinkMLMeta(RootModel):
    root: dict[str, Any] = {}
    model_config = ConfigDict(frozen=True)

    def __getattr__(self, key:str):
        return getattr(self.root, key)

    def __getitem__(self, key:str):
        return self.root[key]

    def __setitem__(self, key:str, value):
        self.root[key] = value

    def __contains__(self, key:str) -> bool:
        return key in self.root


linkml_meta = None

class CompiledResult(str, Enum):
    """
    The kinds of compiled graph.
    """
    in_force = "in_force"
    """
    The graph holds only the accepted directives and exceptions.
    """
    proposals = "proposals"
    """
    The graph also holds the proposed directives and exceptions, which are not in force.
    """


class KnowledgeType(str, Enum):
    """
    The kinds of knowledge.
    """
    domain = "domain"
    """
    Universal knowledge.
    """
    workspace = "workspace"
    """
    Knowledge that is specific to one project.
    """


class Origin(str, Enum):
    """
    The sources of an entity.
    """
    template = "template"
    """
    The template supplied the entity.
    """
    project = "project"
    """
    The project added the entity.
    """


class Status(str, Enum):
    """
    The lifecycle states.
    """
    proposed = "proposed"
    """
    An author recommends the entity. No reviewer approved it. A proposed directive or exception is not in force.
    """
    accepted = "accepted"
    """
    A reviewer approved the entity. An accepted directive or exception is in force.
    """
    deprecated = "deprecated"
    """
    The entity stays for reference. Do not apply it to new work.
    """
    rejected = "rejected"
    """
    A person rejected the proposal. A rejected entity is not in force, and no generated file holds it.
    """


class Invocation(str, Enum):
    """
    The actors that can start a skill.
    """
    agent = "agent"
    """
    The agent can start the skill by itself.
    """
    person = "person"
    """
    Only a person starts the skill. The agent does not start it by itself.
    """


class SkillType(str, Enum):
    """
    The kinds of skill.
    """
    flow = "flow"
    """
    The skill runs the steps of a discipline in their order. Each step has a step file.
    """
    lens = "lens"
    """
    The skill reviews work from one angle, or runs other lens skills.
    """
    system = "system"
    """
    The skill runs an operation of Densho on the graph.
    """


class Basis(str, Enum):
    """
    The kinds of source that support a directive.
    """
    standard = "standard"
    """
    A published standard or a versioned specification.
    """
    research = "research"
    """
    An empirical study or a model from research.
    """
    practitioner = "practitioner"
    """
    A method of a named author or company.
    """
    judgment = "judgment"
    """
    No source supports the directive.
    """


class DirectiveScope(str, Enum):
    """
    The nodes that a directive applies to.
    """
    node = "node"
    """
    The directive applies only to the nodes that it attaches to and to each skill that uses one of them.
    """
    subtree = "subtree"
    """
    The directive applies to the attached nodes and to each node under them. Each node is under the root. A skill is under each node that it uses.
    """



class KnowledgeGraph(ConfiguredBaseModel):
    """
    The root and the knowledge nodes of one repository. A graph has exactly one root.
    """
    root: Root = Field(default=..., description="""The top node of the graph.""")
    nodes: list[Union[Skill,Domain,Discipline,PracticeArea,Concept]] = Field(default=..., description="""The knowledge nodes of the graph.""", min_length=1)
    result: Optional[CompiledResult] = Field(default=None, description="""The directives that a compiled graph holds. A source graph has no value.""")


class GovernedEntity(ConfiguredBaseModel):
    """
    An addressable entity that governance tracks.
    """
    id: str = Field(default=..., description="""The stable identifier. The identifier does not change when a file moves.""")
    status: Status = Field(default=..., description="""The lifecycle state.""")
    origin: Origin = Field(default=..., description="""The source of the entity in this repository.""")
    sources: Optional[list[str]] = Field(default=None, description="""The URLs, repository paths, or citations that support the entity.""")
    rejection_reason: Optional[str] = Field(default=None, description="""The reason that a person rejected the entity.""")

    @field_validator('id')
    def pattern_id(cls, v):
        pattern=re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*(?!\n)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid id format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('sources')
    def pattern_sources(cls, v):
        pattern=re.compile(r"^\S(?: *\S)*(?!\n)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid sources format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid sources format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('rejection_reason')
    def pattern_rejection_reason(cls, v):
        pattern=re.compile(r"^\S(?: *\S)*(?!\n)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid rejection_reason format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid rejection_reason format: {v}"
            raise ValueError(err_msg)
        return v


class Node(GovernedEntity):
    """
    One file in the graph. A node holds its knowledge, its directives, and its pointers.
    """
    kind: Literal["https://github.com/jlm0/densho/schema/Node","densho:Node"] = Field(default=..., description="""The class of the entity. The value is the class CURIE, for example densho:Concept.""")
    title: str = Field(default=..., description="""The preferred name of the node.""")
    pointers: Optional[list[Union[AlwaysPointer,PathPointer,SkillPointer,TextPointer]]] = Field(default=None, description="""The routes from this node to other nodes.""")
    directives: Optional[list[Directive]] = Field(default=None, description="""The directives that live in this file.""")
    body: Optional[str] = Field(default=None, description="""The supporting prose of the node.""")
    id: str = Field(default=..., description="""The stable identifier. The identifier does not change when a file moves.""")
    status: Status = Field(default=..., description="""The lifecycle state.""")
    origin: Origin = Field(default=..., description="""The source of the entity in this repository.""")
    sources: Optional[list[str]] = Field(default=None, description="""The URLs, repository paths, or citations that support the entity.""")
    rejection_reason: Optional[str] = Field(default=None, description="""The reason that a person rejected the entity.""")

    @field_validator('title')
    def pattern_title(cls, v):
        pattern=re.compile(r"^\S(?: *\S)*(?!\n)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid title format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid title format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('body')
    def pattern_body(cls, v):
        pattern=re.compile(r"\S")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid body format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid body format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('id')
    def pattern_id(cls, v):
        pattern=re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*(?!\n)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid id format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('sources')
    def pattern_sources(cls, v):
        pattern=re.compile(r"^\S(?: *\S)*(?!\n)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid sources format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid sources format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('rejection_reason')
    def pattern_rejection_reason(cls, v):
        pattern=re.compile(r"^\S(?: *\S)*(?!\n)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid rejection_reason format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid rejection_reason format: {v}"
            raise ValueError(err_msg)
        return v


class Root(Node):
    """
    The top node of the graph. Agents load the root first.
    """
    kind: Literal["https://github.com/jlm0/densho/schema/Root","densho:Root"] = Field(default=..., description="""The class of the entity. The value is the class CURIE, for example densho:Concept.""")
    title: str = Field(default=..., description="""The preferred name of the node.""")
    pointers: list[Union[AlwaysPointer,PathPointer,SkillPointer,TextPointer]] = Field(default=..., description="""The routes from this node to other nodes.""", min_length=1)
    directives: Optional[list[Directive]] = Field(default=None, description="""The directives that live in this file.""")
    body: Optional[str] = Field(default=None, description="""The supporting prose of the node.""")
    id: str = Field(default=..., description="""The stable identifier. The identifier does not change when a file moves.""")
    status: Status = Field(default=..., description="""The lifecycle state.""")
    origin: Origin = Field(default=..., description="""The source of the entity in this repository.""")
    sources: Optional[list[str]] = Field(default=None, description="""The URLs, repository paths, or citations that support the entity.""")
    rejection_reason: Optional[str] = Field(default=None, description="""The reason that a person rejected the entity.""")

    @field_validator('title')
    def pattern_title(cls, v):
        pattern=re.compile(r"^\S(?: *\S)*(?!\n)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid title format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid title format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('body')
    def pattern_body(cls, v):
        pattern=re.compile(r"\S")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid body format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid body format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('id')
    def pattern_id(cls, v):
        pattern=re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*(?!\n)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid id format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('sources')
    def pattern_sources(cls, v):
        pattern=re.compile(r"^\S(?: *\S)*(?!\n)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid sources format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid sources format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('rejection_reason')
    def pattern_rejection_reason(cls, v):
        pattern=re.compile(r"^\S(?: *\S)*(?!\n)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid rejection_reason format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid rejection_reason format: {v}"
            raise ValueError(err_msg)
        return v


class KnowledgeNode(Node):
    """
    A node that holds domain knowledge or workspace knowledge.
    """
    knowledge_type: KnowledgeType = Field(default=..., description="""The kind of knowledge in the node.""")
    exceptions: Optional[list[DirectiveException]] = Field(default=None, description="""The inherited directives that stop at this node.""")
    kind: Literal["https://github.com/jlm0/densho/schema/KnowledgeNode","densho:KnowledgeNode"] = Field(default=..., description="""The class of the entity. The value is the class CURIE, for example densho:Concept.""")
    title: str = Field(default=..., description="""The preferred name of the node.""")
    pointers: Optional[list[Union[AlwaysPointer,PathPointer,SkillPointer,TextPointer]]] = Field(default=None, description="""The routes from this node to other nodes.""")
    directives: Optional[list[Directive]] = Field(default=None, description="""The directives that live in this file.""")
    body: Optional[str] = Field(default=None, description="""The supporting prose of the node.""")
    id: str = Field(default=..., description="""The stable identifier. The identifier does not change when a file moves.""")
    status: Status = Field(default=..., description="""The lifecycle state.""")
    origin: Origin = Field(default=..., description="""The source of the entity in this repository.""")
    sources: Optional[list[str]] = Field(default=None, description="""The URLs, repository paths, or citations that support the entity.""")
    rejection_reason: Optional[str] = Field(default=None, description="""The reason that a person rejected the entity.""")

    @field_validator('title')
    def pattern_title(cls, v):
        pattern=re.compile(r"^\S(?: *\S)*(?!\n)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid title format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid title format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('body')
    def pattern_body(cls, v):
        pattern=re.compile(r"\S")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid body format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid body format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('id')
    def pattern_id(cls, v):
        pattern=re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*(?!\n)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid id format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('sources')
    def pattern_sources(cls, v):
        pattern=re.compile(r"^\S(?: *\S)*(?!\n)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid sources format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid sources format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('rejection_reason')
    def pattern_rejection_reason(cls, v):
        pattern=re.compile(r"^\S(?: *\S)*(?!\n)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid rejection_reason format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid rejection_reason format: {v}"
            raise ValueError(err_msg)
        return v


class TaxonomyNode(KnowledgeNode):
    """
    A node in the classification from domain to concept.
    """
    definition: str = Field(default=..., description="""The meaning of the node.""")
    related: Optional[list[str]] = Field(default=None, description="""The nodes with an association to this node. This edge is symmetric.""")
    informs: Optional[list[str]] = Field(default=None, description="""The nodes that take the output of this node as an input. This edge is the flow from one step to the next.""")
    depends_on: Optional[list[str]] = Field(default=None, description="""The nodes that this node cannot exist without. A handoff from one step to the next uses informs.""")
    governs: Optional[list[str]] = Field(default=None, description="""The nodes that this node sets rules for. A governance node can name itself.""")
    implements: Optional[list[str]] = Field(default=None, description="""The domain nodes that this workspace node gives project values for.""")
    knowledge_type: KnowledgeType = Field(default=..., description="""The kind of knowledge in the node.""")
    exceptions: Optional[list[DirectiveException]] = Field(default=None, description="""The inherited directives that stop at this node.""")
    kind: Literal["https://github.com/jlm0/densho/schema/TaxonomyNode","http://www.w3.org/2004/02/skos/core#Concept","densho:TaxonomyNode","skos:Concept"] = Field(default=..., description="""The class of the entity. The value is the class CURIE, for example densho:Concept.""")
    title: str = Field(default=..., description="""The preferred name of the node.""")
    pointers: Optional[list[Union[AlwaysPointer,PathPointer,SkillPointer,TextPointer]]] = Field(default=None, description="""The routes from this node to other nodes.""")
    directives: Optional[list[Directive]] = Field(default=None, description="""The directives that live in this file.""")
    body: Optional[str] = Field(default=None, description="""The supporting prose of the node.""")
    id: str = Field(default=..., description="""The stable identifier. The identifier does not change when a file moves.""")
    status: Status = Field(default=..., description="""The lifecycle state.""")
    origin: Origin = Field(default=..., description="""The source of the entity in this repository.""")
    sources: Optional[list[str]] = Field(default=None, description="""The URLs, repository paths, or citations that support the entity.""")
    rejection_reason: Optional[str] = Field(default=None, description="""The reason that a person rejected the entity.""")

    @field_validator('definition')
    def pattern_definition(cls, v):
        pattern=re.compile(r"\S")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid definition format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid definition format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('title')
    def pattern_title(cls, v):
        pattern=re.compile(r"^\S(?: *\S)*(?!\n)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid title format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid title format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('body')
    def pattern_body(cls, v):
        pattern=re.compile(r"\S")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid body format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid body format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('id')
    def pattern_id(cls, v):
        pattern=re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*(?!\n)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid id format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('sources')
    def pattern_sources(cls, v):
        pattern=re.compile(r"^\S(?: *\S)*(?!\n)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid sources format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid sources format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('rejection_reason')
    def pattern_rejection_reason(cls, v):
        pattern=re.compile(r"^\S(?: *\S)*(?!\n)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid rejection_reason format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid rejection_reason format: {v}"
            raise ValueError(err_msg)
        return v


class Domain(TaxonomyNode):
    """
    The top level of the taxonomy. A domain has no broader node.
    """
    definition: str = Field(default=..., description="""The meaning of the node.""")
    related: Optional[list[str]] = Field(default=None, description="""The nodes with an association to this node. This edge is symmetric.""")
    informs: Optional[list[str]] = Field(default=None, description="""The nodes that take the output of this node as an input. This edge is the flow from one step to the next.""")
    depends_on: Optional[list[str]] = Field(default=None, description="""The nodes that this node cannot exist without. A handoff from one step to the next uses informs.""")
    governs: Optional[list[str]] = Field(default=None, description="""The nodes that this node sets rules for. A governance node can name itself.""")
    implements: Optional[list[str]] = Field(default=None, description="""The domain nodes that this workspace node gives project values for.""")
    knowledge_type: KnowledgeType = Field(default=..., description="""The kind of knowledge in the node.""")
    exceptions: Optional[list[DirectiveException]] = Field(default=None, description="""The inherited directives that stop at this node.""")
    kind: Literal["https://github.com/jlm0/densho/schema/Domain","densho:Domain"] = Field(default=..., description="""The class of the entity. The value is the class CURIE, for example densho:Concept.""")
    title: str = Field(default=..., description="""The preferred name of the node.""")
    pointers: Optional[list[Union[AlwaysPointer,PathPointer,SkillPointer,TextPointer]]] = Field(default=None, description="""The routes from this node to other nodes.""")
    directives: Optional[list[Directive]] = Field(default=None, description="""The directives that live in this file.""")
    body: Optional[str] = Field(default=None, description="""The supporting prose of the node.""")
    id: str = Field(default=..., description="""The stable identifier. The identifier does not change when a file moves.""")
    status: Status = Field(default=..., description="""The lifecycle state.""")
    origin: Origin = Field(default=..., description="""The source of the entity in this repository.""")
    sources: Optional[list[str]] = Field(default=None, description="""The URLs, repository paths, or citations that support the entity.""")
    rejection_reason: Optional[str] = Field(default=None, description="""The reason that a person rejected the entity.""")

    @field_validator('definition')
    def pattern_definition(cls, v):
        pattern=re.compile(r"\S")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid definition format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid definition format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('title')
    def pattern_title(cls, v):
        pattern=re.compile(r"^\S(?: *\S)*(?!\n)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid title format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid title format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('body')
    def pattern_body(cls, v):
        pattern=re.compile(r"\S")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid body format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid body format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('id')
    def pattern_id(cls, v):
        pattern=re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*(?!\n)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid id format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('sources')
    def pattern_sources(cls, v):
        pattern=re.compile(r"^\S(?: *\S)*(?!\n)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid sources format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid sources format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('rejection_reason')
    def pattern_rejection_reason(cls, v):
        pattern=re.compile(r"^\S(?: *\S)*(?!\n)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid rejection_reason format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid rejection_reason format: {v}"
            raise ValueError(err_msg)
        return v


class Discipline(TaxonomyNode):
    """
    A field of work in a domain.
    """
    broader: list[str] = Field(default=..., description="""The broader nodes in the taxonomy.""", min_length=1)
    definition: str = Field(default=..., description="""The meaning of the node.""")
    related: Optional[list[str]] = Field(default=None, description="""The nodes with an association to this node. This edge is symmetric.""")
    informs: Optional[list[str]] = Field(default=None, description="""The nodes that take the output of this node as an input. This edge is the flow from one step to the next.""")
    depends_on: Optional[list[str]] = Field(default=None, description="""The nodes that this node cannot exist without. A handoff from one step to the next uses informs.""")
    governs: Optional[list[str]] = Field(default=None, description="""The nodes that this node sets rules for. A governance node can name itself.""")
    implements: Optional[list[str]] = Field(default=None, description="""The domain nodes that this workspace node gives project values for.""")
    knowledge_type: KnowledgeType = Field(default=..., description="""The kind of knowledge in the node.""")
    exceptions: Optional[list[DirectiveException]] = Field(default=None, description="""The inherited directives that stop at this node.""")
    kind: Literal["https://github.com/jlm0/densho/schema/Discipline","densho:Discipline"] = Field(default=..., description="""The class of the entity. The value is the class CURIE, for example densho:Concept.""")
    title: str = Field(default=..., description="""The preferred name of the node.""")
    pointers: Optional[list[Union[AlwaysPointer,PathPointer,SkillPointer,TextPointer]]] = Field(default=None, description="""The routes from this node to other nodes.""")
    directives: Optional[list[Directive]] = Field(default=None, description="""The directives that live in this file.""")
    body: Optional[str] = Field(default=None, description="""The supporting prose of the node.""")
    id: str = Field(default=..., description="""The stable identifier. The identifier does not change when a file moves.""")
    status: Status = Field(default=..., description="""The lifecycle state.""")
    origin: Origin = Field(default=..., description="""The source of the entity in this repository.""")
    sources: Optional[list[str]] = Field(default=None, description="""The URLs, repository paths, or citations that support the entity.""")
    rejection_reason: Optional[str] = Field(default=None, description="""The reason that a person rejected the entity.""")

    @field_validator('definition')
    def pattern_definition(cls, v):
        pattern=re.compile(r"\S")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid definition format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid definition format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('title')
    def pattern_title(cls, v):
        pattern=re.compile(r"^\S(?: *\S)*(?!\n)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid title format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid title format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('body')
    def pattern_body(cls, v):
        pattern=re.compile(r"\S")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid body format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid body format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('id')
    def pattern_id(cls, v):
        pattern=re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*(?!\n)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid id format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('sources')
    def pattern_sources(cls, v):
        pattern=re.compile(r"^\S(?: *\S)*(?!\n)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid sources format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid sources format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('rejection_reason')
    def pattern_rejection_reason(cls, v):
        pattern=re.compile(r"^\S(?: *\S)*(?!\n)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid rejection_reason format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid rejection_reason format: {v}"
            raise ValueError(err_msg)
        return v


class PracticeArea(TaxonomyNode):
    """
    A narrower area of work.
    """
    broader: list[str] = Field(default=..., description="""The broader nodes in the taxonomy.""", min_length=1)
    definition: str = Field(default=..., description="""The meaning of the node.""")
    related: Optional[list[str]] = Field(default=None, description="""The nodes with an association to this node. This edge is symmetric.""")
    informs: Optional[list[str]] = Field(default=None, description="""The nodes that take the output of this node as an input. This edge is the flow from one step to the next.""")
    depends_on: Optional[list[str]] = Field(default=None, description="""The nodes that this node cannot exist without. A handoff from one step to the next uses informs.""")
    governs: Optional[list[str]] = Field(default=None, description="""The nodes that this node sets rules for. A governance node can name itself.""")
    implements: Optional[list[str]] = Field(default=None, description="""The domain nodes that this workspace node gives project values for.""")
    knowledge_type: KnowledgeType = Field(default=..., description="""The kind of knowledge in the node.""")
    exceptions: Optional[list[DirectiveException]] = Field(default=None, description="""The inherited directives that stop at this node.""")
    kind: Literal["https://github.com/jlm0/densho/schema/PracticeArea","densho:PracticeArea"] = Field(default=..., description="""The class of the entity. The value is the class CURIE, for example densho:Concept.""")
    title: str = Field(default=..., description="""The preferred name of the node.""")
    pointers: Optional[list[Union[AlwaysPointer,PathPointer,SkillPointer,TextPointer]]] = Field(default=None, description="""The routes from this node to other nodes.""")
    directives: Optional[list[Directive]] = Field(default=None, description="""The directives that live in this file.""")
    body: Optional[str] = Field(default=None, description="""The supporting prose of the node.""")
    id: str = Field(default=..., description="""The stable identifier. The identifier does not change when a file moves.""")
    status: Status = Field(default=..., description="""The lifecycle state.""")
    origin: Origin = Field(default=..., description="""The source of the entity in this repository.""")
    sources: Optional[list[str]] = Field(default=None, description="""The URLs, repository paths, or citations that support the entity.""")
    rejection_reason: Optional[str] = Field(default=None, description="""The reason that a person rejected the entity.""")

    @field_validator('definition')
    def pattern_definition(cls, v):
        pattern=re.compile(r"\S")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid definition format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid definition format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('title')
    def pattern_title(cls, v):
        pattern=re.compile(r"^\S(?: *\S)*(?!\n)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid title format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid title format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('body')
    def pattern_body(cls, v):
        pattern=re.compile(r"\S")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid body format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid body format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('id')
    def pattern_id(cls, v):
        pattern=re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*(?!\n)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid id format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('sources')
    def pattern_sources(cls, v):
        pattern=re.compile(r"^\S(?: *\S)*(?!\n)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid sources format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid sources format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('rejection_reason')
    def pattern_rejection_reason(cls, v):
        pattern=re.compile(r"^\S(?: *\S)*(?!\n)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid rejection_reason format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid rejection_reason format: {v}"
            raise ValueError(err_msg)
        return v


class Concept(TaxonomyNode):
    """
    A principle, a technique, or a body of knowledge.
    """
    broader: list[str] = Field(default=..., description="""The broader nodes in the taxonomy.""", min_length=1)
    definition: str = Field(default=..., description="""The meaning of the node.""")
    related: Optional[list[str]] = Field(default=None, description="""The nodes with an association to this node. This edge is symmetric.""")
    informs: Optional[list[str]] = Field(default=None, description="""The nodes that take the output of this node as an input. This edge is the flow from one step to the next.""")
    depends_on: Optional[list[str]] = Field(default=None, description="""The nodes that this node cannot exist without. A handoff from one step to the next uses informs.""")
    governs: Optional[list[str]] = Field(default=None, description="""The nodes that this node sets rules for. A governance node can name itself.""")
    implements: Optional[list[str]] = Field(default=None, description="""The domain nodes that this workspace node gives project values for.""")
    knowledge_type: KnowledgeType = Field(default=..., description="""The kind of knowledge in the node.""")
    exceptions: Optional[list[DirectiveException]] = Field(default=None, description="""The inherited directives that stop at this node.""")
    kind: Literal["https://github.com/jlm0/densho/schema/Concept","densho:Concept"] = Field(default=..., description="""The class of the entity. The value is the class CURIE, for example densho:Concept.""")
    title: str = Field(default=..., description="""The preferred name of the node.""")
    pointers: Optional[list[Union[AlwaysPointer,PathPointer,SkillPointer,TextPointer]]] = Field(default=None, description="""The routes from this node to other nodes.""")
    directives: Optional[list[Directive]] = Field(default=None, description="""The directives that live in this file.""")
    body: Optional[str] = Field(default=None, description="""The supporting prose of the node.""")
    id: str = Field(default=..., description="""The stable identifier. The identifier does not change when a file moves.""")
    status: Status = Field(default=..., description="""The lifecycle state.""")
    origin: Origin = Field(default=..., description="""The source of the entity in this repository.""")
    sources: Optional[list[str]] = Field(default=None, description="""The URLs, repository paths, or citations that support the entity.""")
    rejection_reason: Optional[str] = Field(default=None, description="""The reason that a person rejected the entity.""")

    @field_validator('definition')
    def pattern_definition(cls, v):
        pattern=re.compile(r"\S")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid definition format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid definition format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('title')
    def pattern_title(cls, v):
        pattern=re.compile(r"^\S(?: *\S)*(?!\n)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid title format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid title format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('body')
    def pattern_body(cls, v):
        pattern=re.compile(r"\S")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid body format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid body format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('id')
    def pattern_id(cls, v):
        pattern=re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*(?!\n)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid id format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('sources')
    def pattern_sources(cls, v):
        pattern=re.compile(r"^\S(?: *\S)*(?!\n)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid sources format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid sources format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('rejection_reason')
    def pattern_rejection_reason(cls, v):
        pattern=re.compile(r"^\S(?: *\S)*(?!\n)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid rejection_reason format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid rejection_reason format: {v}"
            raise ValueError(err_msg)
        return v


class Skill(KnowledgeNode):
    """
    A reusable capability that composes knowledge from any branch of the taxonomy.
    """
    description: str = Field(default=..., description="""The text that an agent reads to select the skill.""")
    invocation: Invocation = Field(default=..., description="""The actor that starts the skill.""")
    skill_type: SkillType = Field(default=..., description="""The kind of work that the skill does.""")
    uses: Optional[list[str]] = Field(default=None, description="""The knowledge that the skill composes.""")
    applies: Optional[list[str]] = Field(default=None, description="""The directives that the skill applies.""")
    steps: Optional[list[str]] = Field(default=None, description="""The steps of a flow skill, in their order. Each step is a node under the node that the flow uses.""")
    knowledge_type: KnowledgeType = Field(default=..., description="""The kind of knowledge in the node.""")
    exceptions: Optional[list[DirectiveException]] = Field(default=None, description="""The inherited directives that stop at this node.""")
    kind: Literal["https://github.com/jlm0/densho/schema/Skill","densho:Skill"] = Field(default=..., description="""The class of the entity. The value is the class CURIE, for example densho:Concept.""")
    title: str = Field(default=..., description="""The preferred name of the node.""")
    pointers: Optional[list[Union[AlwaysPointer,PathPointer,SkillPointer,TextPointer]]] = Field(default=None, description="""The routes from this node to other nodes.""")
    directives: Optional[list[Directive]] = Field(default=None, description="""The directives that live in this file.""")
    body: Optional[str] = Field(default=None, description="""The supporting prose of the node.""")
    id: str = Field(default=..., description="""The stable identifier. The identifier does not change when a file moves.""")
    status: Status = Field(default=..., description="""The lifecycle state.""")
    origin: Origin = Field(default=..., description="""The source of the entity in this repository.""")
    sources: Optional[list[str]] = Field(default=None, description="""The URLs, repository paths, or citations that support the entity.""")
    rejection_reason: Optional[str] = Field(default=None, description="""The reason that a person rejected the entity.""")

    @field_validator('description')
    def pattern_description(cls, v):
        pattern=re.compile(r"^\S(?: *\S)*(?!\n)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid description format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid description format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('title')
    def pattern_title(cls, v):
        pattern=re.compile(r"^\S(?: *\S)*(?!\n)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid title format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid title format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('body')
    def pattern_body(cls, v):
        pattern=re.compile(r"\S")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid body format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid body format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('id')
    def pattern_id(cls, v):
        pattern=re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*(?!\n)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid id format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('sources')
    def pattern_sources(cls, v):
        pattern=re.compile(r"^\S(?: *\S)*(?!\n)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid sources format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid sources format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('rejection_reason')
    def pattern_rejection_reason(cls, v):
        pattern=re.compile(r"^\S(?: *\S)*(?!\n)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid rejection_reason format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid rejection_reason format: {v}"
            raise ValueError(err_msg)
        return v


class Directive(GovernedEntity):
    """
    An atomic instruction with its own identity. A directive lives in the file of one node.
    """
    text: str = Field(default=..., description="""The instruction.""")
    scope: DirectiveScope = Field(default=..., description="""The nodes that the directive applies to. This field has no default, because inheritance is explicit.""")
    basis: Basis = Field(default=..., description="""The kind of source that supports the directive.""")
    also_attached_to: Optional[list[str]] = Field(default=None, description="""The nodes that the directive attaches to, in addition to the node that holds it.""")
    refines: Optional[list[str]] = Field(default=None, description="""The broader directives that this directive makes more specific. Both directives apply.""")
    conflicts_with: Optional[list[str]] = Field(default=None, description="""The directives that must not apply at the same node as this directive. This relationship is symmetric.""")
    id: str = Field(default=..., description="""The stable identifier. The identifier does not change when a file moves.""")
    status: Status = Field(default=..., description="""The lifecycle state.""")
    origin: Origin = Field(default=..., description="""The source of the entity in this repository.""")
    sources: Optional[list[str]] = Field(default=None, description="""The URLs, repository paths, or citations that support the entity.""")
    rejection_reason: Optional[str] = Field(default=None, description="""The reason that a person rejected the entity.""")

    @field_validator('text')
    def pattern_text(cls, v):
        pattern=re.compile(r"^\S(?: *\S)*(?!\n)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid text format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid text format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('id')
    def pattern_id(cls, v):
        pattern=re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*(?!\n)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid id format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('sources')
    def pattern_sources(cls, v):
        pattern=re.compile(r"^\S(?: *\S)*(?!\n)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid sources format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid sources format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('rejection_reason')
    def pattern_rejection_reason(cls, v):
        pattern=re.compile(r"^\S(?: *\S)*(?!\n)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid rejection_reason format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid rejection_reason format: {v}"
            raise ValueError(err_msg)
        return v


class DirectiveException(ConfiguredBaseModel):
    """
    A statement that a node steps out of a directive that it would otherwise inherit. Only an accepted exception stops the directive.
    """
    directive: str = Field(default=..., description="""The directive that the exception stops.""")
    reason: str = Field(default=..., description="""The reason that the directive does not apply at this node.""")
    status: Status = Field(default=..., description="""The lifecycle state.""")
    rejection_reason: Optional[str] = Field(default=None, description="""The reason that a person rejected the entity.""")

    @field_validator('reason')
    def pattern_reason(cls, v):
        pattern=re.compile(r"^\S(?: *\S)*(?!\n)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid reason format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid reason format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('rejection_reason')
    def pattern_rejection_reason(cls, v):
        pattern=re.compile(r"^\S(?: *\S)*(?!\n)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid rejection_reason format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid rejection_reason format: {v}"
            raise ValueError(err_msg)
        return v


class Pointer(ConfiguredBaseModel):
    """
    A route that tells an agent when and how to load a node.
    """
    kind: Literal["https://github.com/jlm0/densho/schema/Pointer","densho:Pointer"] = Field(default=..., description="""The class of the entity. The value is the class CURIE, for example densho:Concept.""")
    target: str = Field(default=..., description="""The node that the pointer routes to.""")
    trigger: str = Field(default=..., description="""The condition that tells an agent to follow the pointer.""")

    @field_validator('trigger')
    def pattern_trigger(cls, v):
        pattern=re.compile(r"^\S(?: *\S)*(?!\n)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid trigger format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid trigger format: {v}"
            raise ValueError(err_msg)
        return v


class AlwaysPointer(Pointer):
    """
    A pointer to a node that the harness loads at session start.
    """
    kind: Literal["https://github.com/jlm0/densho/schema/AlwaysPointer","densho:AlwaysPointer"] = Field(default=..., description="""The class of the entity. The value is the class CURIE, for example densho:Concept.""")
    target: str = Field(default=..., description="""The node that the pointer routes to.""")
    trigger: str = Field(default=..., description="""The condition that tells an agent to follow the pointer.""")

    @field_validator('trigger')
    def pattern_trigger(cls, v):
        pattern=re.compile(r"^\S(?: *\S)*(?!\n)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid trigger format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid trigger format: {v}"
            raise ValueError(err_msg)
        return v


class PathPointer(Pointer):
    """
    A pointer to a node that the harness loads when the agent opens a matching file.
    """
    paths: list[str] = Field(default=..., description="""The file patterns that load the target.""", min_length=1)
    kind: Literal["https://github.com/jlm0/densho/schema/PathPointer","densho:PathPointer"] = Field(default=..., description="""The class of the entity. The value is the class CURIE, for example densho:Concept.""")
    target: str = Field(default=..., description="""The node that the pointer routes to.""")
    trigger: str = Field(default=..., description="""The condition that tells an agent to follow the pointer.""")

    @field_validator('paths')
    def pattern_paths(cls, v):
        pattern=re.compile(r"^\S(?: *\S)*(?!\n)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid paths format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid paths format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('trigger')
    def pattern_trigger(cls, v):
        pattern=re.compile(r"^\S(?: *\S)*(?!\n)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid trigger format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid trigger format: {v}"
            raise ValueError(err_msg)
        return v


class SkillPointer(Pointer):
    """
    A pointer to a skill that the agent selects from the skill listing.
    """
    kind: Literal["https://github.com/jlm0/densho/schema/SkillPointer","densho:SkillPointer"] = Field(default=..., description="""The class of the entity. The value is the class CURIE, for example densho:Concept.""")
    target: str = Field(default=..., description="""The node that the pointer routes to.""")
    trigger: str = Field(default=..., description="""The condition that tells an agent to follow the pointer.""")

    @field_validator('trigger')
    def pattern_trigger(cls, v):
        pattern=re.compile(r"^\S(?: *\S)*(?!\n)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid trigger format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid trigger format: {v}"
            raise ValueError(err_msg)
        return v


class TextPointer(Pointer):
    """
    A pointer to a node that the agent opens when it reads the pointer text.
    """
    kind: Literal["https://github.com/jlm0/densho/schema/TextPointer","densho:TextPointer"] = Field(default=..., description="""The class of the entity. The value is the class CURIE, for example densho:Concept.""")
    target: str = Field(default=..., description="""The node that the pointer routes to.""")
    trigger: str = Field(default=..., description="""The condition that tells an agent to follow the pointer.""")

    @field_validator('trigger')
    def pattern_trigger(cls, v):
        pattern=re.compile(r"^\S(?: *\S)*(?!\n)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid trigger format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid trigger format: {v}"
            raise ValueError(err_msg)
        return v


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
KnowledgeGraph.model_rebuild()
GovernedEntity.model_rebuild()
Node.model_rebuild()
Root.model_rebuild()
KnowledgeNode.model_rebuild()
TaxonomyNode.model_rebuild()
Domain.model_rebuild()
Discipline.model_rebuild()
PracticeArea.model_rebuild()
Concept.model_rebuild()
Skill.model_rebuild()
Directive.model_rebuild()
DirectiveException.model_rebuild()
Pointer.model_rebuild()
AlwaysPointer.model_rebuild()
PathPointer.model_rebuild()
SkillPointer.model_rebuild()
TextPointer.model_rebuild()
