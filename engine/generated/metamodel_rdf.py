# id: https://github.com/jlm0/densho/schema/metamodel
# description: This schema defines what can exist in the knowledge graph.
# license: https://creativecommons.org/publicdomain/zero/1.0/

import dataclasses
import re
from dataclasses import dataclass
from datetime import (
    date,
    datetime,
    time
)
from typing import (
    Any,
    ClassVar,
    Dict,
    List,
    Optional,
    Union
)

from jsonasobj2 import (
    JsonObj,
    as_dict
)
from linkml_runtime.linkml_model.meta import (
    EnumDefinition,
    PermissibleValue,
    PvFormulaOptions
)
from linkml_runtime.utils.curienamespace import CurieNamespace
from linkml_runtime.utils.enumerations import EnumDefinitionImpl
from linkml_runtime.utils.formatutils import (
    camelcase,
    sfx,
    underscore
)
from linkml_runtime.utils.metamodelcore import (
    bnode,
    empty_dict,
    empty_list
)
from linkml_runtime.utils.slot import Slot
from linkml_runtime.utils.yamlutils import (
    YAMLRoot,
    extended_float,
    extended_int,
    extended_str
)
from rdflib import (
    Namespace,
    URIRef
)

from linkml_runtime.linkml_model.types import String, Uriorcurie
from linkml_runtime.utils.metamodelcore import URIorCURIE

metamodel_version = "1.12.0"
version = "0.1.0"

# Namespaces
DCTERMS = CurieNamespace('dcterms', 'http://purl.org/dc/terms/')
DENSHO = CurieNamespace('densho', 'https://github.com/jlm0/densho/schema/')
LINKML = CurieNamespace('linkml', 'https://w3id.org/linkml/')
RDF = CurieNamespace('rdf', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#')
SKOS = CurieNamespace('skos', 'http://www.w3.org/2004/02/skos/core#')
DEFAULT_ = DENSHO


# Types

# Class references
class GovernedEntityId(extended_str):
    pass


class NodeId(GovernedEntityId):
    pass


class RootId(NodeId):
    pass


class KnowledgeNodeId(NodeId):
    pass


class TaxonomyNodeId(KnowledgeNodeId):
    pass


class DomainId(TaxonomyNodeId):
    pass


class DisciplineId(TaxonomyNodeId):
    pass


class PracticeAreaId(TaxonomyNodeId):
    pass


class ConceptId(TaxonomyNodeId):
    pass


class SkillId(KnowledgeNodeId):
    pass


class DirectiveId(GovernedEntityId):
    pass


@dataclass(repr=False)
class KnowledgeGraph(YAMLRoot):
    """
    The root and the knowledge nodes of one repository. A graph has exactly one root.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DENSHO["KnowledgeGraph"]
    class_class_curie: ClassVar[str] = "densho:KnowledgeGraph"
    class_name: ClassVar[str] = "KnowledgeGraph"
    class_model_uri: ClassVar[URIRef] = DENSHO.KnowledgeGraph

    root: Union[dict, "Root"] = None
    nodes: Union[dict[Union[str, KnowledgeNodeId], Union[dict, "KnowledgeNode"]], list[Union[dict, "KnowledgeNode"]]] = empty_dict()
    result: Optional[Union[str, "CompiledResult"]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.root):
            self.MissingRequiredField("root")
        if not isinstance(self.root, Root):
            self.root = Root(**as_dict(self.root))

        if self._is_empty(self.nodes):
            self.MissingRequiredField("nodes")
        self._normalize_inlined_as_list(slot_name="nodes", slot_type=KnowledgeNode, key_name="id", keyed=True)

        if self.result is not None and not isinstance(self.result, CompiledResult):
            self.result = CompiledResult(self.result)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class GovernedEntity(YAMLRoot):
    """
    An addressable entity that governance tracks.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DENSHO["GovernedEntity"]
    class_class_curie: ClassVar[str] = "densho:GovernedEntity"
    class_name: ClassVar[str] = "GovernedEntity"
    class_model_uri: ClassVar[URIRef] = DENSHO.GovernedEntity

    id: Union[str, GovernedEntityId] = None
    status: Union[str, "Status"] = None
    origin: Union[str, "Origin"] = None
    sources: Optional[Union[str, list[str]]] = empty_list()
    rejection_reason: Optional[str] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, GovernedEntityId):
            self.id = GovernedEntityId(self.id)

        if self._is_empty(self.status):
            self.MissingRequiredField("status")
        if not isinstance(self.status, Status):
            self.status = Status(self.status)

        if self._is_empty(self.origin):
            self.MissingRequiredField("origin")
        if not isinstance(self.origin, Origin):
            self.origin = Origin(self.origin)

        if not isinstance(self.sources, list):
            self.sources = [self.sources] if self.sources is not None else []
        self.sources = [v if isinstance(v, str) else str(v) for v in self.sources]

        if self.rejection_reason is not None and not isinstance(self.rejection_reason, str):
            self.rejection_reason = str(self.rejection_reason)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class Node(GovernedEntity):
    """
    One file in the graph. A node holds its knowledge, its directives, and its pointers.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DENSHO["Node"]
    class_class_curie: ClassVar[str] = "densho:Node"
    class_name: ClassVar[str] = "Node"
    class_model_uri: ClassVar[URIRef] = DENSHO.Node

    id: Union[str, NodeId] = None
    status: Union[str, "Status"] = None
    origin: Union[str, "Origin"] = None
    kind: Union[str, URIorCURIE] = None
    title: str = None
    pointers: Optional[Union[Union[dict, "Pointer"], list[Union[dict, "Pointer"]]]] = empty_list()
    directives: Optional[Union[dict[Union[str, DirectiveId], Union[dict, "Directive"]], list[Union[dict, "Directive"]]]] = empty_dict()
    body: Optional[str] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.kind):
            self.MissingRequiredField("kind")
        self.kind = str(self.class_class_curie if self.class_class_curie is not None else self.class_class_uri)

        if self._is_empty(self.title):
            self.MissingRequiredField("title")
        if not isinstance(self.title, str):
            self.title = str(self.title)

        self._normalize_inlined_as_list(slot_name="pointers", slot_type=Pointer, key_name="kind", keyed=False)

        self._normalize_inlined_as_list(slot_name="directives", slot_type=Directive, key_name="id", keyed=True)

        if self.body is not None and not isinstance(self.body, str):
            self.body = str(self.body)

        super().__post_init__(**kwargs)


    def __new__(cls, *args, **kwargs):

        type_designator = "kind"
        if not type_designator in kwargs:
            return super().__new__(cls,*args,**kwargs)
        else:
            type_designator_value = kwargs[type_designator]
            target_cls = cls._class_for("class_class_curie", type_designator_value)


            if target_cls is None:
                target_cls = cls._class_for("class_class_uri", type_designator_value)


            if target_cls is None:
                target_cls = cls._class_for("class_model_uri", type_designator_value)


            if target_cls is None:
                raise ValueError(f"Wrong type designator value: class {cls.__name__} "
                                 f"has no subclass with ['class_class_curie', 'class_class_uri', 'class_model_uri']='{kwargs[type_designator]}'")
            return super().__new__(target_cls,*args,**kwargs)



@dataclass(repr=False)
class Root(Node):
    """
    The top node of the graph. Agents load the root first.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DENSHO["Root"]
    class_class_curie: ClassVar[str] = "densho:Root"
    class_name: ClassVar[str] = "Root"
    class_model_uri: ClassVar[URIRef] = DENSHO.Root

    id: Union[str, RootId] = None
    status: Union[str, "Status"] = None
    origin: Union[str, "Origin"] = None
    kind: Union[str, URIorCURIE] = None
    title: str = None
    pointers: Union[Union[dict, "Pointer"], list[Union[dict, "Pointer"]]] = None
    use_a_skill: Optional[Union[Union[str, DirectiveId], list[Union[str, DirectiveId]]]] = empty_list()
    create_a_rule: Optional[Union[Union[str, DirectiveId], list[Union[str, DirectiveId]]]] = empty_list()

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, RootId):
            self.id = RootId(self.id)

        if self._is_empty(self.pointers):
            self.MissingRequiredField("pointers")
        self._normalize_inlined_as_list(slot_name="pointers", slot_type=Pointer, key_name="kind", keyed=False)

        if not isinstance(self.use_a_skill, list):
            self.use_a_skill = [self.use_a_skill] if self.use_a_skill is not None else []
        self.use_a_skill = [v if isinstance(v, DirectiveId) else DirectiveId(v) for v in self.use_a_skill]

        if not isinstance(self.create_a_rule, list):
            self.create_a_rule = [self.create_a_rule] if self.create_a_rule is not None else []
        self.create_a_rule = [v if isinstance(v, DirectiveId) else DirectiveId(v) for v in self.create_a_rule]

        super().__post_init__(**kwargs)
        if self._is_empty(self.kind):
            self.MissingRequiredField("kind")
        self.kind = str(self.class_class_curie if self.class_class_curie is not None else self.class_class_uri)


@dataclass(repr=False)
class KnowledgeNode(Node):
    """
    A node that holds domain knowledge or workspace knowledge.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DENSHO["KnowledgeNode"]
    class_class_curie: ClassVar[str] = "densho:KnowledgeNode"
    class_name: ClassVar[str] = "KnowledgeNode"
    class_model_uri: ClassVar[URIRef] = DENSHO.KnowledgeNode

    id: Union[str, KnowledgeNodeId] = None
    status: Union[str, "Status"] = None
    origin: Union[str, "Origin"] = None
    kind: Union[str, URIorCURIE] = None
    title: str = None
    knowledge_type: Union[str, "KnowledgeType"] = None
    exceptions: Optional[Union[Union[dict, "DirectiveException"], list[Union[dict, "DirectiveException"]]]] = empty_list()

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.knowledge_type):
            self.MissingRequiredField("knowledge_type")
        if not isinstance(self.knowledge_type, KnowledgeType):
            self.knowledge_type = KnowledgeType(self.knowledge_type)

        self._normalize_inlined_as_list(slot_name="exceptions", slot_type=DirectiveException, key_name="reason", keyed=False)

        super().__post_init__(**kwargs)
        if self._is_empty(self.kind):
            self.MissingRequiredField("kind")
        self.kind = str(self.class_class_curie if self.class_class_curie is not None else self.class_class_uri)


@dataclass(repr=False)
class TaxonomyNode(KnowledgeNode):
    """
    A node in the classification from domain to concept.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = SKOS["Concept"]
    class_class_curie: ClassVar[str] = "skos:Concept"
    class_name: ClassVar[str] = "TaxonomyNode"
    class_model_uri: ClassVar[URIRef] = DENSHO.TaxonomyNode

    id: Union[str, TaxonomyNodeId] = None
    status: Union[str, "Status"] = None
    origin: Union[str, "Origin"] = None
    kind: Union[str, URIorCURIE] = None
    title: str = None
    knowledge_type: Union[str, "KnowledgeType"] = None
    definition: str = None
    related: Optional[Union[Union[str, TaxonomyNodeId], list[Union[str, TaxonomyNodeId]]]] = empty_list()
    informs: Optional[Union[Union[str, TaxonomyNodeId], list[Union[str, TaxonomyNodeId]]]] = empty_list()
    depends_on: Optional[Union[Union[str, TaxonomyNodeId], list[Union[str, TaxonomyNodeId]]]] = empty_list()
    governs: Optional[Union[Union[str, NodeId], list[Union[str, NodeId]]]] = empty_list()
    implements: Optional[Union[Union[str, TaxonomyNodeId], list[Union[str, TaxonomyNodeId]]]] = empty_list()

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.definition):
            self.MissingRequiredField("definition")
        if not isinstance(self.definition, str):
            self.definition = str(self.definition)

        if not isinstance(self.related, list):
            self.related = [self.related] if self.related is not None else []
        self.related = [v if isinstance(v, TaxonomyNodeId) else TaxonomyNodeId(v) for v in self.related]

        if not isinstance(self.informs, list):
            self.informs = [self.informs] if self.informs is not None else []
        self.informs = [v if isinstance(v, TaxonomyNodeId) else TaxonomyNodeId(v) for v in self.informs]

        if not isinstance(self.depends_on, list):
            self.depends_on = [self.depends_on] if self.depends_on is not None else []
        self.depends_on = [v if isinstance(v, TaxonomyNodeId) else TaxonomyNodeId(v) for v in self.depends_on]

        if not isinstance(self.governs, list):
            self.governs = [self.governs] if self.governs is not None else []
        self.governs = [v if isinstance(v, NodeId) else NodeId(v) for v in self.governs]

        if not isinstance(self.implements, list):
            self.implements = [self.implements] if self.implements is not None else []
        self.implements = [v if isinstance(v, TaxonomyNodeId) else TaxonomyNodeId(v) for v in self.implements]

        super().__post_init__(**kwargs)
        if self._is_empty(self.kind):
            self.MissingRequiredField("kind")
        self.kind = str(self.class_class_curie if self.class_class_curie is not None else self.class_class_uri)


@dataclass(repr=False)
class Domain(TaxonomyNode):
    """
    The top level of the taxonomy. A domain has no broader node.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DENSHO["Domain"]
    class_class_curie: ClassVar[str] = "densho:Domain"
    class_name: ClassVar[str] = "Domain"
    class_model_uri: ClassVar[URIRef] = DENSHO.Domain

    id: Union[str, DomainId] = None
    status: Union[str, "Status"] = None
    origin: Union[str, "Origin"] = None
    kind: Union[str, URIorCURIE] = None
    title: str = None
    knowledge_type: Union[str, "KnowledgeType"] = None
    definition: str = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, DomainId):
            self.id = DomainId(self.id)

        super().__post_init__(**kwargs)
        if self._is_empty(self.kind):
            self.MissingRequiredField("kind")
        self.kind = str(self.class_class_curie if self.class_class_curie is not None else self.class_class_uri)


@dataclass(repr=False)
class Discipline(TaxonomyNode):
    """
    A field of work in a domain.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DENSHO["Discipline"]
    class_class_curie: ClassVar[str] = "densho:Discipline"
    class_name: ClassVar[str] = "Discipline"
    class_model_uri: ClassVar[URIRef] = DENSHO.Discipline

    id: Union[str, DisciplineId] = None
    status: Union[str, "Status"] = None
    origin: Union[str, "Origin"] = None
    kind: Union[str, URIorCURIE] = None
    title: str = None
    knowledge_type: Union[str, "KnowledgeType"] = None
    definition: str = None
    broader: Union[Union[str, DomainId], list[Union[str, DomainId]]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, DisciplineId):
            self.id = DisciplineId(self.id)

        if self._is_empty(self.broader):
            self.MissingRequiredField("broader")
        if not isinstance(self.broader, list):
            self.broader = [self.broader] if self.broader is not None else []
        self.broader = [v if isinstance(v, DomainId) else DomainId(v) for v in self.broader]

        super().__post_init__(**kwargs)
        if self._is_empty(self.kind):
            self.MissingRequiredField("kind")
        self.kind = str(self.class_class_curie if self.class_class_curie is not None else self.class_class_uri)


@dataclass(repr=False)
class PracticeArea(TaxonomyNode):
    """
    A narrower area of work.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DENSHO["PracticeArea"]
    class_class_curie: ClassVar[str] = "densho:PracticeArea"
    class_name: ClassVar[str] = "PracticeArea"
    class_model_uri: ClassVar[URIRef] = DENSHO.PracticeArea

    id: Union[str, PracticeAreaId] = None
    status: Union[str, "Status"] = None
    origin: Union[str, "Origin"] = None
    kind: Union[str, URIorCURIE] = None
    title: str = None
    knowledge_type: Union[str, "KnowledgeType"] = None
    definition: str = None
    broader: Union[Union[str, TaxonomyNodeId], list[Union[str, TaxonomyNodeId]]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, PracticeAreaId):
            self.id = PracticeAreaId(self.id)

        if self._is_empty(self.broader):
            self.MissingRequiredField("broader")
        if not isinstance(self.broader, list):
            self.broader = [self.broader] if self.broader is not None else []
        self.broader = [v if isinstance(v, TaxonomyNodeId) else TaxonomyNodeId(v) for v in self.broader]

        super().__post_init__(**kwargs)
        if self._is_empty(self.kind):
            self.MissingRequiredField("kind")
        self.kind = str(self.class_class_curie if self.class_class_curie is not None else self.class_class_uri)


@dataclass(repr=False)
class Concept(TaxonomyNode):
    """
    A principle, a technique, or a body of knowledge.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DENSHO["Concept"]
    class_class_curie: ClassVar[str] = "densho:Concept"
    class_name: ClassVar[str] = "Concept"
    class_model_uri: ClassVar[URIRef] = DENSHO.Concept

    id: Union[str, ConceptId] = None
    status: Union[str, "Status"] = None
    origin: Union[str, "Origin"] = None
    kind: Union[str, URIorCURIE] = None
    title: str = None
    knowledge_type: Union[str, "KnowledgeType"] = None
    definition: str = None
    broader: Union[Union[str, TaxonomyNodeId], list[Union[str, TaxonomyNodeId]]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, ConceptId):
            self.id = ConceptId(self.id)

        if self._is_empty(self.broader):
            self.MissingRequiredField("broader")
        if not isinstance(self.broader, list):
            self.broader = [self.broader] if self.broader is not None else []
        self.broader = [v if isinstance(v, TaxonomyNodeId) else TaxonomyNodeId(v) for v in self.broader]

        super().__post_init__(**kwargs)
        if self._is_empty(self.kind):
            self.MissingRequiredField("kind")
        self.kind = str(self.class_class_curie if self.class_class_curie is not None else self.class_class_uri)


@dataclass(repr=False)
class Skill(KnowledgeNode):
    """
    A reusable capability that composes knowledge from any branch of the taxonomy.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DENSHO["Skill"]
    class_class_curie: ClassVar[str] = "densho:Skill"
    class_name: ClassVar[str] = "Skill"
    class_model_uri: ClassVar[URIRef] = DENSHO.Skill

    id: Union[str, SkillId] = None
    status: Union[str, "Status"] = None
    origin: Union[str, "Origin"] = None
    kind: Union[str, URIorCURIE] = None
    title: str = None
    knowledge_type: Union[str, "KnowledgeType"] = None
    description: str = None
    invocation: Union[str, "Invocation"] = None
    skill_type: Union[str, "SkillType"] = None
    uses: Optional[Union[Union[str, TaxonomyNodeId], list[Union[str, TaxonomyNodeId]]]] = empty_list()
    applies: Optional[Union[Union[str, DirectiveId], list[Union[str, DirectiveId]]]] = empty_list()
    steps: Optional[Union[str, list[str]]] = empty_list()

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, SkillId):
            self.id = SkillId(self.id)

        if self._is_empty(self.description):
            self.MissingRequiredField("description")
        if not isinstance(self.description, str):
            self.description = str(self.description)

        if self._is_empty(self.invocation):
            self.MissingRequiredField("invocation")
        if not isinstance(self.invocation, Invocation):
            self.invocation = Invocation(self.invocation)

        if self._is_empty(self.skill_type):
            self.MissingRequiredField("skill_type")
        if not isinstance(self.skill_type, SkillType):
            self.skill_type = SkillType(self.skill_type)

        if not isinstance(self.uses, list):
            self.uses = [self.uses] if self.uses is not None else []
        self.uses = [v if isinstance(v, TaxonomyNodeId) else TaxonomyNodeId(v) for v in self.uses]

        if not isinstance(self.applies, list):
            self.applies = [self.applies] if self.applies is not None else []
        self.applies = [v if isinstance(v, DirectiveId) else DirectiveId(v) for v in self.applies]

        if not isinstance(self.steps, list):
            self.steps = [self.steps] if self.steps is not None else []
        self.steps = [v if isinstance(v, str) else str(v) for v in self.steps]

        super().__post_init__(**kwargs)
        if self._is_empty(self.kind):
            self.MissingRequiredField("kind")
        self.kind = str(self.class_class_curie if self.class_class_curie is not None else self.class_class_uri)


@dataclass(repr=False)
class Directive(GovernedEntity):
    """
    An atomic instruction with its own identity. A directive lives in the file of one node.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DENSHO["Directive"]
    class_class_curie: ClassVar[str] = "densho:Directive"
    class_name: ClassVar[str] = "Directive"
    class_model_uri: ClassVar[URIRef] = DENSHO.Directive

    id: Union[str, DirectiveId] = None
    status: Union[str, "Status"] = None
    origin: Union[str, "Origin"] = None
    text: str = None
    scope: Union[str, "DirectiveScope"] = None
    basis: Union[str, "Basis"] = None
    also_attached_to: Optional[Union[Union[str, NodeId], list[Union[str, NodeId]]]] = empty_list()
    refines: Optional[Union[Union[str, DirectiveId], list[Union[str, DirectiveId]]]] = empty_list()
    conflicts_with: Optional[Union[Union[str, DirectiveId], list[Union[str, DirectiveId]]]] = empty_list()

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, DirectiveId):
            self.id = DirectiveId(self.id)

        if self._is_empty(self.text):
            self.MissingRequiredField("text")
        if not isinstance(self.text, str):
            self.text = str(self.text)

        if self._is_empty(self.scope):
            self.MissingRequiredField("scope")
        if not isinstance(self.scope, DirectiveScope):
            self.scope = DirectiveScope(self.scope)

        if self._is_empty(self.basis):
            self.MissingRequiredField("basis")
        if not isinstance(self.basis, Basis):
            self.basis = Basis(self.basis)

        if not isinstance(self.also_attached_to, list):
            self.also_attached_to = [self.also_attached_to] if self.also_attached_to is not None else []
        self.also_attached_to = [v if isinstance(v, NodeId) else NodeId(v) for v in self.also_attached_to]

        if not isinstance(self.refines, list):
            self.refines = [self.refines] if self.refines is not None else []
        self.refines = [v if isinstance(v, DirectiveId) else DirectiveId(v) for v in self.refines]

        if not isinstance(self.conflicts_with, list):
            self.conflicts_with = [self.conflicts_with] if self.conflicts_with is not None else []
        self.conflicts_with = [v if isinstance(v, DirectiveId) else DirectiveId(v) for v in self.conflicts_with]

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class DirectiveException(YAMLRoot):
    """
    A statement that a node steps out of a directive that it would otherwise inherit. Only an accepted exception stops
    the directive.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DENSHO["DirectiveException"]
    class_class_curie: ClassVar[str] = "densho:DirectiveException"
    class_name: ClassVar[str] = "DirectiveException"
    class_model_uri: ClassVar[URIRef] = DENSHO.DirectiveException

    directive: Union[str, DirectiveId] = None
    reason: str = None
    status: Union[str, "Status"] = None
    rejection_reason: Optional[str] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.directive):
            self.MissingRequiredField("directive")
        if not isinstance(self.directive, DirectiveId):
            self.directive = DirectiveId(self.directive)

        if self._is_empty(self.reason):
            self.MissingRequiredField("reason")
        if not isinstance(self.reason, str):
            self.reason = str(self.reason)

        if self._is_empty(self.status):
            self.MissingRequiredField("status")
        if not isinstance(self.status, Status):
            self.status = Status(self.status)

        if self.rejection_reason is not None and not isinstance(self.rejection_reason, str):
            self.rejection_reason = str(self.rejection_reason)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class Pointer(YAMLRoot):
    """
    A route that tells an agent when and how to load a node.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DENSHO["Pointer"]
    class_class_curie: ClassVar[str] = "densho:Pointer"
    class_name: ClassVar[str] = "Pointer"
    class_model_uri: ClassVar[URIRef] = DENSHO.Pointer

    kind: Union[str, URIorCURIE] = None
    target: Union[str, NodeId] = None
    trigger: str = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.kind):
            self.MissingRequiredField("kind")
        self.kind = str(self.class_class_curie if self.class_class_curie is not None else self.class_class_uri)

        if self._is_empty(self.target):
            self.MissingRequiredField("target")
        if not isinstance(self.target, NodeId):
            self.target = NodeId(self.target)

        if self._is_empty(self.trigger):
            self.MissingRequiredField("trigger")
        if not isinstance(self.trigger, str):
            self.trigger = str(self.trigger)

        super().__post_init__(**kwargs)


    def __new__(cls, *args, **kwargs):

        type_designator = "kind"
        if not type_designator in kwargs:
            return super().__new__(cls,*args,**kwargs)
        else:
            type_designator_value = kwargs[type_designator]
            target_cls = cls._class_for("class_class_curie", type_designator_value)


            if target_cls is None:
                target_cls = cls._class_for("class_class_uri", type_designator_value)


            if target_cls is None:
                target_cls = cls._class_for("class_model_uri", type_designator_value)


            if target_cls is None:
                raise ValueError(f"Wrong type designator value: class {cls.__name__} "
                                 f"has no subclass with ['class_class_curie', 'class_class_uri', 'class_model_uri']='{kwargs[type_designator]}'")
            return super().__new__(target_cls,*args,**kwargs)



@dataclass(repr=False)
class AlwaysPointer(Pointer):
    """
    A pointer to a node that the harness loads at session start.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DENSHO["AlwaysPointer"]
    class_class_curie: ClassVar[str] = "densho:AlwaysPointer"
    class_name: ClassVar[str] = "AlwaysPointer"
    class_model_uri: ClassVar[URIRef] = DENSHO.AlwaysPointer

    kind: Union[str, URIorCURIE] = None
    target: Union[str, NodeId] = None
    trigger: str = None

    def __post_init__(self, *_: str, **kwargs: Any):

        super().__post_init__(**kwargs)
        if self._is_empty(self.kind):
            self.MissingRequiredField("kind")
        self.kind = str(self.class_class_curie if self.class_class_curie is not None else self.class_class_uri)


@dataclass(repr=False)
class PathPointer(Pointer):
    """
    A pointer to a node that the harness loads when the agent opens a matching file.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DENSHO["PathPointer"]
    class_class_curie: ClassVar[str] = "densho:PathPointer"
    class_name: ClassVar[str] = "PathPointer"
    class_model_uri: ClassVar[URIRef] = DENSHO.PathPointer

    kind: Union[str, URIorCURIE] = None
    target: Union[str, NodeId] = None
    trigger: str = None
    paths: Union[str, list[str]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.paths):
            self.MissingRequiredField("paths")
        if not isinstance(self.paths, list):
            self.paths = [self.paths] if self.paths is not None else []
        self.paths = [v if isinstance(v, str) else str(v) for v in self.paths]

        super().__post_init__(**kwargs)
        if self._is_empty(self.kind):
            self.MissingRequiredField("kind")
        self.kind = str(self.class_class_curie if self.class_class_curie is not None else self.class_class_uri)


@dataclass(repr=False)
class SkillPointer(Pointer):
    """
    A pointer to a skill that the agent selects from the skill listing.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DENSHO["SkillPointer"]
    class_class_curie: ClassVar[str] = "densho:SkillPointer"
    class_name: ClassVar[str] = "SkillPointer"
    class_model_uri: ClassVar[URIRef] = DENSHO.SkillPointer

    kind: Union[str, URIorCURIE] = None
    trigger: str = None
    target: Union[str, SkillId] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.target):
            self.MissingRequiredField("target")
        if not isinstance(self.target, SkillId):
            self.target = SkillId(self.target)

        super().__post_init__(**kwargs)
        if self._is_empty(self.kind):
            self.MissingRequiredField("kind")
        self.kind = str(self.class_class_curie if self.class_class_curie is not None else self.class_class_uri)


@dataclass(repr=False)
class TextPointer(Pointer):
    """
    A pointer to a node that the agent opens when it reads the pointer text.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DENSHO["TextPointer"]
    class_class_curie: ClassVar[str] = "densho:TextPointer"
    class_name: ClassVar[str] = "TextPointer"
    class_model_uri: ClassVar[URIRef] = DENSHO.TextPointer

    kind: Union[str, URIorCURIE] = None
    target: Union[str, NodeId] = None
    trigger: str = None

    def __post_init__(self, *_: str, **kwargs: Any):

        super().__post_init__(**kwargs)
        if self._is_empty(self.kind):
            self.MissingRequiredField("kind")
        self.kind = str(self.class_class_curie if self.class_class_curie is not None else self.class_class_uri)


# Enumerations
class CompiledResult(EnumDefinitionImpl):
    """
    The kinds of compiled graph.
    """
    in_force = PermissibleValue(
        text="in_force",
        description="The graph holds only the accepted directives and exceptions.")
    proposals = PermissibleValue(
        text="proposals",
        description="The graph also holds the proposed directives and exceptions, which are not in force.")

    _defn = EnumDefinition(
        name="CompiledResult",
        description="The kinds of compiled graph.",
    )

class KnowledgeType(EnumDefinitionImpl):
    """
    The kinds of knowledge.
    """
    domain = PermissibleValue(
        text="domain",
        description="Universal knowledge.")
    workspace = PermissibleValue(
        text="workspace",
        description="Knowledge that is specific to one project.")

    _defn = EnumDefinition(
        name="KnowledgeType",
        description="The kinds of knowledge.",
    )

class Origin(EnumDefinitionImpl):
    """
    The sources of an entity.
    """
    template = PermissibleValue(
        text="template",
        description="The template supplied the entity.")
    project = PermissibleValue(
        text="project",
        description="The project added the entity.")

    _defn = EnumDefinition(
        name="Origin",
        description="The sources of an entity.",
    )

class Status(EnumDefinitionImpl):
    """
    The lifecycle states.
    """
    proposed = PermissibleValue(
        text="proposed",
        description="""An author recommends the entity. No reviewer approved it. A proposed directive or exception is not in force.""")
    accepted = PermissibleValue(
        text="accepted",
        description="A reviewer approved the entity. An accepted directive or exception is in force.")
    deprecated = PermissibleValue(
        text="deprecated",
        description="The entity stays for reference. Do not apply it to new work.")
    rejected = PermissibleValue(
        text="rejected",
        description="""A person rejected the proposal. A rejected entity is not in force, and no generated file holds it.""")

    _defn = EnumDefinition(
        name="Status",
        description="The lifecycle states.",
    )

class Invocation(EnumDefinitionImpl):
    """
    The actors that can start a skill.
    """
    agent = PermissibleValue(
        text="agent",
        description="The agent can start the skill by itself.")
    person = PermissibleValue(
        text="person",
        description="Only a person starts the skill. The agent does not start it by itself.")

    _defn = EnumDefinition(
        name="Invocation",
        description="The actors that can start a skill.",
    )

class SkillType(EnumDefinitionImpl):
    """
    The kinds of skill.
    """
    task = PermissibleValue(
        text="task",
        description="The skill does one task in 1 or more steps, in their order. Each step has a step file.")
    lens = PermissibleValue(
        text="lens",
        description="The skill reviews work from one angle, or runs other lens skills.")
    system = PermissibleValue(
        text="system",
        description="The skill runs an operation of Densho on the graph.")

    _defn = EnumDefinition(
        name="SkillType",
        description="The kinds of skill.",
    )

class Basis(EnumDefinitionImpl):
    """
    The kinds of source that support a directive.
    """
    standard = PermissibleValue(
        text="standard",
        description="A published standard or a versioned specification.")
    research = PermissibleValue(
        text="research",
        description="An empirical study or a model from research.")
    practitioner = PermissibleValue(
        text="practitioner",
        description="A method of a named author or company.")
    judgment = PermissibleValue(
        text="judgment",
        description="No source supports the directive.")

    _defn = EnumDefinition(
        name="Basis",
        description="The kinds of source that support a directive.",
    )

class DirectiveScope(EnumDefinitionImpl):
    """
    The nodes that a directive applies to.
    """
    node = PermissibleValue(
        text="node",
        description="""The directive applies only to the nodes that it attaches to and to each skill that uses one of them.""")
    subtree = PermissibleValue(
        text="subtree",
        description="""The directive applies to the attached nodes and to each node under them. Each node is under the root. A skill is under each node that it uses.""")

    _defn = EnumDefinition(
        name="DirectiveScope",
        description="The nodes that a directive applies to.",
    )

# Slots
class slots:
    pass

slots.root = Slot(uri=DENSHO.root, name="root", curie=DENSHO.curie('root'),
                   model_uri=DENSHO.root, domain=None, range=Union[dict, Root])

slots.nodes = Slot(uri=DENSHO.nodes, name="nodes", curie=DENSHO.curie('nodes'),
                   model_uri=DENSHO.nodes, domain=None, range=Union[dict[Union[str, KnowledgeNodeId], Union[dict, KnowledgeNode]], list[Union[dict, KnowledgeNode]]])

slots.result = Slot(uri=DENSHO.result, name="result", curie=DENSHO.curie('result'),
                   model_uri=DENSHO.result, domain=None, range=Optional[Union[str, "CompiledResult"]])

slots.id = Slot(uri=DENSHO.id, name="id", curie=DENSHO.curie('id'),
                   model_uri=DENSHO.id, domain=None, range=URIRef,
                   pattern=re.compile(r'^[a-z][a-z0-9]*(-[a-z0-9]+)*(?!\n)$'))

slots.status = Slot(uri=DENSHO.status, name="status", curie=DENSHO.curie('status'),
                   model_uri=DENSHO.status, domain=None, range=Union[str, "Status"])

slots.origin = Slot(uri=DENSHO.origin, name="origin", curie=DENSHO.curie('origin'),
                   model_uri=DENSHO.origin, domain=None, range=Union[str, "Origin"])

slots.sources = Slot(uri=DCTERMS.source, name="sources", curie=DCTERMS.curie('source'),
                   model_uri=DENSHO.sources, domain=None, range=Optional[Union[str, list[str]]],
                   pattern=re.compile(r'^\S(?: *\S)*(?!\n)$'))

slots.rejection_reason = Slot(uri=DENSHO.rejection_reason, name="rejection_reason", curie=DENSHO.curie('rejection_reason'),
                   model_uri=DENSHO.rejection_reason, domain=None, range=Optional[str],
                   pattern=re.compile(r'^\S(?: *\S)*(?!\n)$'))

slots.kind = Slot(uri=RDF.type, name="kind", curie=RDF.curie('type'),
                   model_uri=DENSHO.kind, domain=None, range=Union[str, URIorCURIE])

slots.title = Slot(uri=SKOS.prefLabel, name="title", curie=SKOS.curie('prefLabel'),
                   model_uri=DENSHO.title, domain=None, range=str,
                   pattern=re.compile(r'^\S(?: *\S)*(?!\n)$'))

slots.pointers = Slot(uri=DENSHO.pointers, name="pointers", curie=DENSHO.curie('pointers'),
                   model_uri=DENSHO.pointers, domain=None, range=Optional[Union[Union[dict, Pointer], list[Union[dict, Pointer]]]])

slots.directives = Slot(uri=DENSHO.directives, name="directives", curie=DENSHO.curie('directives'),
                   model_uri=DENSHO.directives, domain=None, range=Optional[Union[dict[Union[str, DirectiveId], Union[dict, Directive]], list[Union[dict, Directive]]]])

slots.body = Slot(uri=DENSHO.body, name="body", curie=DENSHO.curie('body'),
                   model_uri=DENSHO.body, domain=None, range=Optional[str],
                   pattern=re.compile(r'\S'))

slots.knowledge_type = Slot(uri=DENSHO.knowledge_type, name="knowledge_type", curie=DENSHO.curie('knowledge_type'),
                   model_uri=DENSHO.knowledge_type, domain=None, range=Union[str, "KnowledgeType"])

slots.exceptions = Slot(uri=DENSHO.exceptions, name="exceptions", curie=DENSHO.curie('exceptions'),
                   model_uri=DENSHO.exceptions, domain=None, range=Optional[Union[Union[dict, DirectiveException], list[Union[dict, DirectiveException]]]])

slots.directive = Slot(uri=DENSHO.directive, name="directive", curie=DENSHO.curie('directive'),
                   model_uri=DENSHO.directive, domain=None, range=Union[str, DirectiveId])

slots.reason = Slot(uri=DENSHO.reason, name="reason", curie=DENSHO.curie('reason'),
                   model_uri=DENSHO.reason, domain=None, range=str,
                   pattern=re.compile(r'^\S(?: *\S)*(?!\n)$'))

slots.definition = Slot(uri=SKOS.definition, name="definition", curie=SKOS.curie('definition'),
                   model_uri=DENSHO.definition, domain=None, range=str,
                   pattern=re.compile(r'\S'))

slots.description = Slot(uri=DENSHO.description, name="description", curie=DENSHO.curie('description'),
                   model_uri=DENSHO.description, domain=None, range=str,
                   pattern=re.compile(r'^\S(?: *\S)*(?!\n)$'))

slots.invocation = Slot(uri=DENSHO.invocation, name="invocation", curie=DENSHO.curie('invocation'),
                   model_uri=DENSHO.invocation, domain=None, range=Union[str, "Invocation"])

slots.skill_type = Slot(uri=DENSHO.skill_type, name="skill_type", curie=DENSHO.curie('skill_type'),
                   model_uri=DENSHO.skill_type, domain=None, range=Union[str, "SkillType"])

slots.text = Slot(uri=DENSHO.text, name="text", curie=DENSHO.curie('text'),
                   model_uri=DENSHO.text, domain=None, range=str,
                   pattern=re.compile(r'^\S(?: *\S)*(?!\n)$'))

slots.scope = Slot(uri=DENSHO.scope, name="scope", curie=DENSHO.curie('scope'),
                   model_uri=DENSHO.scope, domain=None, range=Union[str, "DirectiveScope"])

slots.basis = Slot(uri=DENSHO.basis, name="basis", curie=DENSHO.curie('basis'),
                   model_uri=DENSHO.basis, domain=None, range=Union[str, "Basis"])

slots.also_attached_to = Slot(uri=DENSHO.also_attached_to, name="also_attached_to", curie=DENSHO.curie('also_attached_to'),
                   model_uri=DENSHO.also_attached_to, domain=None, range=Optional[Union[Union[str, NodeId], list[Union[str, NodeId]]]])

slots.refines = Slot(uri=DENSHO.refines, name="refines", curie=DENSHO.curie('refines'),
                   model_uri=DENSHO.refines, domain=None, range=Optional[Union[Union[str, DirectiveId], list[Union[str, DirectiveId]]]])

slots.conflicts_with = Slot(uri=DENSHO.conflicts_with, name="conflicts_with", curie=DENSHO.curie('conflicts_with'),
                   model_uri=DENSHO.conflicts_with, domain=None, range=Optional[Union[Union[str, DirectiveId], list[Union[str, DirectiveId]]]])

slots.target = Slot(uri=DENSHO.target, name="target", curie=DENSHO.curie('target'),
                   model_uri=DENSHO.target, domain=None, range=Union[str, NodeId])

slots.trigger = Slot(uri=DENSHO.trigger, name="trigger", curie=DENSHO.curie('trigger'),
                   model_uri=DENSHO.trigger, domain=None, range=str,
                   pattern=re.compile(r'^\S(?: *\S)*(?!\n)$'))

slots.paths = Slot(uri=DENSHO.paths, name="paths", curie=DENSHO.curie('paths'),
                   model_uri=DENSHO.paths, domain=None, range=Union[str, list[str]],
                   pattern=re.compile(r'^\S(?: *\S)*(?!\n)$'))

slots.edge = Slot(uri=DENSHO.edge, name="edge", curie=DENSHO.curie('edge'),
                   model_uri=DENSHO.edge, domain=None, range=Optional[Union[str, GovernedEntityId]])

slots.broader = Slot(uri=SKOS.broader, name="broader", curie=SKOS.curie('broader'),
                   model_uri=DENSHO.broader, domain=None, range=Union[Union[str, TaxonomyNodeId], list[Union[str, TaxonomyNodeId]]])

slots.related = Slot(uri=SKOS.related, name="related", curie=SKOS.curie('related'),
                   model_uri=DENSHO.related, domain=None, range=Optional[Union[Union[str, TaxonomyNodeId], list[Union[str, TaxonomyNodeId]]]])

slots.informs = Slot(uri=DENSHO.informs, name="informs", curie=DENSHO.curie('informs'),
                   model_uri=DENSHO.informs, domain=None, range=Optional[Union[Union[str, TaxonomyNodeId], list[Union[str, TaxonomyNodeId]]]])

slots.depends_on = Slot(uri=DENSHO.depends_on, name="depends_on", curie=DENSHO.curie('depends_on'),
                   model_uri=DENSHO.depends_on, domain=None, range=Optional[Union[Union[str, TaxonomyNodeId], list[Union[str, TaxonomyNodeId]]]])

slots.governs = Slot(uri=DENSHO.governs, name="governs", curie=DENSHO.curie('governs'),
                   model_uri=DENSHO.governs, domain=None, range=Optional[Union[Union[str, NodeId], list[Union[str, NodeId]]]])

slots.implements = Slot(uri=DENSHO.implements, name="implements", curie=DENSHO.curie('implements'),
                   model_uri=DENSHO.implements, domain=None, range=Optional[Union[Union[str, TaxonomyNodeId], list[Union[str, TaxonomyNodeId]]]])

slots.uses = Slot(uri=DENSHO.uses, name="uses", curie=DENSHO.curie('uses'),
                   model_uri=DENSHO.uses, domain=None, range=Optional[Union[Union[str, TaxonomyNodeId], list[Union[str, TaxonomyNodeId]]]])

slots.applies = Slot(uri=DENSHO.applies, name="applies", curie=DENSHO.curie('applies'),
                   model_uri=DENSHO.applies, domain=None, range=Optional[Union[Union[str, DirectiveId], list[Union[str, DirectiveId]]]])

slots.steps = Slot(uri=DENSHO.steps, name="steps", curie=DENSHO.curie('steps'),
                   model_uri=DENSHO.steps, domain=None, range=Optional[Union[str, list[str]]],
                   pattern=re.compile(r'^[a-z][a-z0-9]*(-[a-z0-9]+)*(?!\n)$'))

slots.use_a_skill = Slot(uri=DENSHO.use_a_skill, name="use_a_skill", curie=DENSHO.curie('use_a_skill'),
                   model_uri=DENSHO.use_a_skill, domain=None, range=Optional[Union[Union[str, DirectiveId], list[Union[str, DirectiveId]]]])

slots.create_a_rule = Slot(uri=DENSHO.create_a_rule, name="create_a_rule", curie=DENSHO.curie('create_a_rule'),
                   model_uri=DENSHO.create_a_rule, domain=None, range=Optional[Union[Union[str, DirectiveId], list[Union[str, DirectiveId]]]])

slots.Root_pointers = Slot(uri=DENSHO.pointers, name="Root_pointers", curie=DENSHO.curie('pointers'),
                   model_uri=DENSHO.Root_pointers, domain=Root, range=Union[Union[dict, "Pointer"], list[Union[dict, "Pointer"]]])

slots.Discipline_broader = Slot(uri=SKOS.broader, name="Discipline_broader", curie=SKOS.curie('broader'),
                   model_uri=DENSHO.Discipline_broader, domain=Discipline, range=Union[Union[str, DomainId], list[Union[str, DomainId]]])

slots.PracticeArea_broader = Slot(uri=SKOS.broader, name="PracticeArea_broader", curie=SKOS.curie('broader'),
                   model_uri=DENSHO.PracticeArea_broader, domain=PracticeArea, range=Union[Union[str, TaxonomyNodeId], list[Union[str, TaxonomyNodeId]]])

slots.Concept_broader = Slot(uri=SKOS.broader, name="Concept_broader", curie=SKOS.curie('broader'),
                   model_uri=DENSHO.Concept_broader, domain=Concept, range=Union[Union[str, TaxonomyNodeId], list[Union[str, TaxonomyNodeId]]])

slots.SkillPointer_target = Slot(uri=DENSHO.target, name="SkillPointer_target", curie=DENSHO.curie('target'),
                   model_uri=DENSHO.SkillPointer_target, domain=SkillPointer, range=Union[str, SkillId])

