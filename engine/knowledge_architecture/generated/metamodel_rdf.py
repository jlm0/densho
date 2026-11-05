# id: https://github.com/jlm0/knowledge-architecture/schema/metamodel
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
KA = CurieNamespace('ka', 'https://github.com/jlm0/knowledge-architecture/schema/')
LINKML = CurieNamespace('linkml', 'https://w3id.org/linkml/')
RDF = CurieNamespace('rdf', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#')
SKOS = CurieNamespace('skos', 'http://www.w3.org/2004/02/skos/core#')
DEFAULT_ = KA


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

    class_class_uri: ClassVar[URIRef] = KA["KnowledgeGraph"]
    class_class_curie: ClassVar[str] = "ka:KnowledgeGraph"
    class_name: ClassVar[str] = "KnowledgeGraph"
    class_model_uri: ClassVar[URIRef] = KA.KnowledgeGraph

    root: Union[dict, "Root"] = None
    nodes: Union[dict[Union[str, KnowledgeNodeId], Union[dict, "KnowledgeNode"]], list[Union[dict, "KnowledgeNode"]]] = empty_dict()

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.root):
            self.MissingRequiredField("root")
        if not isinstance(self.root, Root):
            self.root = Root(**as_dict(self.root))

        if self._is_empty(self.nodes):
            self.MissingRequiredField("nodes")
        self._normalize_inlined_as_list(slot_name="nodes", slot_type=KnowledgeNode, key_name="id", keyed=True)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class GovernedEntity(YAMLRoot):
    """
    An addressable entity that governance tracks.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = KA["GovernedEntity"]
    class_class_curie: ClassVar[str] = "ka:GovernedEntity"
    class_name: ClassVar[str] = "GovernedEntity"
    class_model_uri: ClassVar[URIRef] = KA.GovernedEntity

    id: Union[str, GovernedEntityId] = None
    status: Union[str, "Status"] = None
    origin: Union[str, "Origin"] = None
    sources: Optional[Union[str, list[str]]] = empty_list()

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

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class Node(GovernedEntity):
    """
    One file in the graph. A node holds its knowledge, its directives, and its pointers.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = KA["Node"]
    class_class_curie: ClassVar[str] = "ka:Node"
    class_name: ClassVar[str] = "Node"
    class_model_uri: ClassVar[URIRef] = KA.Node

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

    class_class_uri: ClassVar[URIRef] = KA["Root"]
    class_class_curie: ClassVar[str] = "ka:Root"
    class_name: ClassVar[str] = "Root"
    class_model_uri: ClassVar[URIRef] = KA.Root

    id: Union[str, RootId] = None
    status: Union[str, "Status"] = None
    origin: Union[str, "Origin"] = None
    kind: Union[str, URIorCURIE] = None
    title: str = None
    pointers: Union[Union[dict, "Pointer"], list[Union[dict, "Pointer"]]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, RootId):
            self.id = RootId(self.id)

        if self._is_empty(self.pointers):
            self.MissingRequiredField("pointers")
        self._normalize_inlined_as_list(slot_name="pointers", slot_type=Pointer, key_name="kind", keyed=False)

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

    class_class_uri: ClassVar[URIRef] = KA["KnowledgeNode"]
    class_class_curie: ClassVar[str] = "ka:KnowledgeNode"
    class_name: ClassVar[str] = "KnowledgeNode"
    class_model_uri: ClassVar[URIRef] = KA.KnowledgeNode

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
    class_model_uri: ClassVar[URIRef] = KA.TaxonomyNode

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

    class_class_uri: ClassVar[URIRef] = KA["Domain"]
    class_class_curie: ClassVar[str] = "ka:Domain"
    class_name: ClassVar[str] = "Domain"
    class_model_uri: ClassVar[URIRef] = KA.Domain

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

    class_class_uri: ClassVar[URIRef] = KA["Discipline"]
    class_class_curie: ClassVar[str] = "ka:Discipline"
    class_name: ClassVar[str] = "Discipline"
    class_model_uri: ClassVar[URIRef] = KA.Discipline

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

    class_class_uri: ClassVar[URIRef] = KA["PracticeArea"]
    class_class_curie: ClassVar[str] = "ka:PracticeArea"
    class_name: ClassVar[str] = "PracticeArea"
    class_model_uri: ClassVar[URIRef] = KA.PracticeArea

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

    class_class_uri: ClassVar[URIRef] = KA["Concept"]
    class_class_curie: ClassVar[str] = "ka:Concept"
    class_name: ClassVar[str] = "Concept"
    class_model_uri: ClassVar[URIRef] = KA.Concept

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

    class_class_uri: ClassVar[URIRef] = KA["Skill"]
    class_class_curie: ClassVar[str] = "ka:Skill"
    class_name: ClassVar[str] = "Skill"
    class_model_uri: ClassVar[URIRef] = KA.Skill

    id: Union[str, SkillId] = None
    status: Union[str, "Status"] = None
    origin: Union[str, "Origin"] = None
    kind: Union[str, URIorCURIE] = None
    title: str = None
    knowledge_type: Union[str, "KnowledgeType"] = None
    description: str = None
    uses: Optional[Union[Union[str, TaxonomyNodeId], list[Union[str, TaxonomyNodeId]]]] = empty_list()
    applies: Optional[Union[Union[str, DirectiveId], list[Union[str, DirectiveId]]]] = empty_list()

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, SkillId):
            self.id = SkillId(self.id)

        if self._is_empty(self.description):
            self.MissingRequiredField("description")
        if not isinstance(self.description, str):
            self.description = str(self.description)

        if not isinstance(self.uses, list):
            self.uses = [self.uses] if self.uses is not None else []
        self.uses = [v if isinstance(v, TaxonomyNodeId) else TaxonomyNodeId(v) for v in self.uses]

        if not isinstance(self.applies, list):
            self.applies = [self.applies] if self.applies is not None else []
        self.applies = [v if isinstance(v, DirectiveId) else DirectiveId(v) for v in self.applies]

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

    class_class_uri: ClassVar[URIRef] = KA["Directive"]
    class_class_curie: ClassVar[str] = "ka:Directive"
    class_name: ClassVar[str] = "Directive"
    class_model_uri: ClassVar[URIRef] = KA.Directive

    id: Union[str, DirectiveId] = None
    status: Union[str, "Status"] = None
    origin: Union[str, "Origin"] = None
    text: str = None
    scope: Union[str, "DirectiveScope"] = None
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
    A statement that a node steps out of a directive that it would otherwise inherit.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = KA["DirectiveException"]
    class_class_curie: ClassVar[str] = "ka:DirectiveException"
    class_name: ClassVar[str] = "DirectiveException"
    class_model_uri: ClassVar[URIRef] = KA.DirectiveException

    directive: Union[str, DirectiveId] = None
    reason: str = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.directive):
            self.MissingRequiredField("directive")
        if not isinstance(self.directive, DirectiveId):
            self.directive = DirectiveId(self.directive)

        if self._is_empty(self.reason):
            self.MissingRequiredField("reason")
        if not isinstance(self.reason, str):
            self.reason = str(self.reason)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class Pointer(YAMLRoot):
    """
    A route that tells an agent when and how to load a node.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = KA["Pointer"]
    class_class_curie: ClassVar[str] = "ka:Pointer"
    class_name: ClassVar[str] = "Pointer"
    class_model_uri: ClassVar[URIRef] = KA.Pointer

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

    class_class_uri: ClassVar[URIRef] = KA["AlwaysPointer"]
    class_class_curie: ClassVar[str] = "ka:AlwaysPointer"
    class_name: ClassVar[str] = "AlwaysPointer"
    class_model_uri: ClassVar[URIRef] = KA.AlwaysPointer

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

    class_class_uri: ClassVar[URIRef] = KA["PathPointer"]
    class_class_curie: ClassVar[str] = "ka:PathPointer"
    class_name: ClassVar[str] = "PathPointer"
    class_model_uri: ClassVar[URIRef] = KA.PathPointer

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

    class_class_uri: ClassVar[URIRef] = KA["SkillPointer"]
    class_class_curie: ClassVar[str] = "ka:SkillPointer"
    class_name: ClassVar[str] = "SkillPointer"
    class_model_uri: ClassVar[URIRef] = KA.SkillPointer

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

    class_class_uri: ClassVar[URIRef] = KA["TextPointer"]
    class_class_curie: ClassVar[str] = "ka:TextPointer"
    class_name: ClassVar[str] = "TextPointer"
    class_model_uri: ClassVar[URIRef] = KA.TextPointer

    kind: Union[str, URIorCURIE] = None
    target: Union[str, NodeId] = None
    trigger: str = None

    def __post_init__(self, *_: str, **kwargs: Any):

        super().__post_init__(**kwargs)
        if self._is_empty(self.kind):
            self.MissingRequiredField("kind")
        self.kind = str(self.class_class_curie if self.class_class_curie is not None else self.class_class_uri)


# Enumerations
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
        description="An author recommends the entity. No reviewer approved it.")
    accepted = PermissibleValue(
        text="accepted",
        description="A reviewer approved the entity.")
    deprecated = PermissibleValue(
        text="deprecated",
        description="The entity stays for reference. Do not apply it to new work.")

    _defn = EnumDefinition(
        name="Status",
        description="The lifecycle states.",
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

slots.root = Slot(uri=KA.root, name="root", curie=KA.curie('root'),
                   model_uri=KA.root, domain=None, range=Union[dict, Root])

slots.nodes = Slot(uri=KA.nodes, name="nodes", curie=KA.curie('nodes'),
                   model_uri=KA.nodes, domain=None, range=Union[dict[Union[str, KnowledgeNodeId], Union[dict, KnowledgeNode]], list[Union[dict, KnowledgeNode]]])

slots.id = Slot(uri=KA.id, name="id", curie=KA.curie('id'),
                   model_uri=KA.id, domain=None, range=URIRef,
                   pattern=re.compile(r'^[a-z][a-z0-9]*(-[a-z0-9]+)*(?!\n)$'))

slots.status = Slot(uri=KA.status, name="status", curie=KA.curie('status'),
                   model_uri=KA.status, domain=None, range=Union[str, "Status"])

slots.origin = Slot(uri=KA.origin, name="origin", curie=KA.curie('origin'),
                   model_uri=KA.origin, domain=None, range=Union[str, "Origin"])

slots.sources = Slot(uri=DCTERMS.source, name="sources", curie=DCTERMS.curie('source'),
                   model_uri=KA.sources, domain=None, range=Optional[Union[str, list[str]]],
                   pattern=re.compile(r'^\S(?: *\S)*(?!\n)$'))

slots.kind = Slot(uri=RDF.type, name="kind", curie=RDF.curie('type'),
                   model_uri=KA.kind, domain=None, range=Union[str, URIorCURIE])

slots.title = Slot(uri=SKOS.prefLabel, name="title", curie=SKOS.curie('prefLabel'),
                   model_uri=KA.title, domain=None, range=str,
                   pattern=re.compile(r'^\S(?: *\S)*(?!\n)$'))

slots.pointers = Slot(uri=KA.pointers, name="pointers", curie=KA.curie('pointers'),
                   model_uri=KA.pointers, domain=None, range=Optional[Union[Union[dict, Pointer], list[Union[dict, Pointer]]]])

slots.directives = Slot(uri=KA.directives, name="directives", curie=KA.curie('directives'),
                   model_uri=KA.directives, domain=None, range=Optional[Union[dict[Union[str, DirectiveId], Union[dict, Directive]], list[Union[dict, Directive]]]])

slots.body = Slot(uri=KA.body, name="body", curie=KA.curie('body'),
                   model_uri=KA.body, domain=None, range=Optional[str],
                   pattern=re.compile(r'\S'))

slots.knowledge_type = Slot(uri=KA.knowledge_type, name="knowledge_type", curie=KA.curie('knowledge_type'),
                   model_uri=KA.knowledge_type, domain=None, range=Union[str, "KnowledgeType"])

slots.exceptions = Slot(uri=KA.exceptions, name="exceptions", curie=KA.curie('exceptions'),
                   model_uri=KA.exceptions, domain=None, range=Optional[Union[Union[dict, DirectiveException], list[Union[dict, DirectiveException]]]])

slots.directive = Slot(uri=KA.directive, name="directive", curie=KA.curie('directive'),
                   model_uri=KA.directive, domain=None, range=Union[str, DirectiveId])

slots.reason = Slot(uri=KA.reason, name="reason", curie=KA.curie('reason'),
                   model_uri=KA.reason, domain=None, range=str,
                   pattern=re.compile(r'^\S(?: *\S)*(?!\n)$'))

slots.definition = Slot(uri=SKOS.definition, name="definition", curie=SKOS.curie('definition'),
                   model_uri=KA.definition, domain=None, range=str,
                   pattern=re.compile(r'\S'))

slots.description = Slot(uri=KA.description, name="description", curie=KA.curie('description'),
                   model_uri=KA.description, domain=None, range=str,
                   pattern=re.compile(r'^\S(?: *\S)*(?!\n)$'))

slots.text = Slot(uri=KA.text, name="text", curie=KA.curie('text'),
                   model_uri=KA.text, domain=None, range=str,
                   pattern=re.compile(r'^\S(?: *\S)*(?!\n)$'))

slots.scope = Slot(uri=KA.scope, name="scope", curie=KA.curie('scope'),
                   model_uri=KA.scope, domain=None, range=Union[str, "DirectiveScope"])

slots.also_attached_to = Slot(uri=KA.also_attached_to, name="also_attached_to", curie=KA.curie('also_attached_to'),
                   model_uri=KA.also_attached_to, domain=None, range=Optional[Union[Union[str, NodeId], list[Union[str, NodeId]]]])

slots.refines = Slot(uri=KA.refines, name="refines", curie=KA.curie('refines'),
                   model_uri=KA.refines, domain=None, range=Optional[Union[Union[str, DirectiveId], list[Union[str, DirectiveId]]]])

slots.conflicts_with = Slot(uri=KA.conflicts_with, name="conflicts_with", curie=KA.curie('conflicts_with'),
                   model_uri=KA.conflicts_with, domain=None, range=Optional[Union[Union[str, DirectiveId], list[Union[str, DirectiveId]]]])

slots.target = Slot(uri=KA.target, name="target", curie=KA.curie('target'),
                   model_uri=KA.target, domain=None, range=Union[str, NodeId])

slots.trigger = Slot(uri=KA.trigger, name="trigger", curie=KA.curie('trigger'),
                   model_uri=KA.trigger, domain=None, range=str,
                   pattern=re.compile(r'^\S(?: *\S)*(?!\n)$'))

slots.paths = Slot(uri=KA.paths, name="paths", curie=KA.curie('paths'),
                   model_uri=KA.paths, domain=None, range=Union[str, list[str]],
                   pattern=re.compile(r'^\S(?: *\S)*(?!\n)$'))

slots.edge = Slot(uri=KA.edge, name="edge", curie=KA.curie('edge'),
                   model_uri=KA.edge, domain=None, range=Optional[Union[str, GovernedEntityId]])

slots.broader = Slot(uri=SKOS.broader, name="broader", curie=SKOS.curie('broader'),
                   model_uri=KA.broader, domain=None, range=Union[Union[str, TaxonomyNodeId], list[Union[str, TaxonomyNodeId]]])

slots.related = Slot(uri=SKOS.related, name="related", curie=SKOS.curie('related'),
                   model_uri=KA.related, domain=None, range=Optional[Union[Union[str, TaxonomyNodeId], list[Union[str, TaxonomyNodeId]]]])

slots.informs = Slot(uri=KA.informs, name="informs", curie=KA.curie('informs'),
                   model_uri=KA.informs, domain=None, range=Optional[Union[Union[str, TaxonomyNodeId], list[Union[str, TaxonomyNodeId]]]])

slots.depends_on = Slot(uri=KA.depends_on, name="depends_on", curie=KA.curie('depends_on'),
                   model_uri=KA.depends_on, domain=None, range=Optional[Union[Union[str, TaxonomyNodeId], list[Union[str, TaxonomyNodeId]]]])

slots.governs = Slot(uri=KA.governs, name="governs", curie=KA.curie('governs'),
                   model_uri=KA.governs, domain=None, range=Optional[Union[Union[str, NodeId], list[Union[str, NodeId]]]])

slots.implements = Slot(uri=KA.implements, name="implements", curie=KA.curie('implements'),
                   model_uri=KA.implements, domain=None, range=Optional[Union[Union[str, TaxonomyNodeId], list[Union[str, TaxonomyNodeId]]]])

slots.uses = Slot(uri=KA.uses, name="uses", curie=KA.curie('uses'),
                   model_uri=KA.uses, domain=None, range=Optional[Union[Union[str, TaxonomyNodeId], list[Union[str, TaxonomyNodeId]]]])

slots.applies = Slot(uri=KA.applies, name="applies", curie=KA.curie('applies'),
                   model_uri=KA.applies, domain=None, range=Optional[Union[Union[str, DirectiveId], list[Union[str, DirectiveId]]]])

slots.Root_pointers = Slot(uri=KA.pointers, name="Root_pointers", curie=KA.curie('pointers'),
                   model_uri=KA.Root_pointers, domain=Root, range=Union[Union[dict, "Pointer"], list[Union[dict, "Pointer"]]])

slots.Discipline_broader = Slot(uri=SKOS.broader, name="Discipline_broader", curie=SKOS.curie('broader'),
                   model_uri=KA.Discipline_broader, domain=Discipline, range=Union[Union[str, DomainId], list[Union[str, DomainId]]])

slots.PracticeArea_broader = Slot(uri=SKOS.broader, name="PracticeArea_broader", curie=SKOS.curie('broader'),
                   model_uri=KA.PracticeArea_broader, domain=PracticeArea, range=Union[Union[str, TaxonomyNodeId], list[Union[str, TaxonomyNodeId]]])

slots.Concept_broader = Slot(uri=SKOS.broader, name="Concept_broader", curie=SKOS.curie('broader'),
                   model_uri=KA.Concept_broader, domain=Concept, range=Union[Union[str, TaxonomyNodeId], list[Union[str, TaxonomyNodeId]]])

slots.SkillPointer_target = Slot(uri=KA.target, name="SkillPointer_target", curie=KA.curie('target'),
                   model_uri=KA.SkillPointer_target, domain=SkillPointer, range=Union[str, SkillId])

