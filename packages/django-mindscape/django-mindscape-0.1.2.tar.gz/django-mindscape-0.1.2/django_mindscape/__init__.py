# -*- coding:utf-8 -*-
# (setenv "LC_ALL" "ja_JP.UTF-8")
import sys
import logging
logger = logging.getLogger(__name__)
from django.db.models import (
    ManyToOneRel,
    OneToOneRel,
    ManyToManyRel
)
from collections import (
    namedtuple,
    OrderedDict,
)
from django.utils.functional import cached_property

Node = namedtuple("Node", "model dependencies")
RNode = namedtuple("RNode", "node children")
Relation = namedtuple("Relation", "name from_ to type")


class Brain(object):  # bad name..
    def is_skip(self, m):
        return m._meta.abstract

    def collect_dependencies(self, m):
        for f in m._meta.local_fields:
            if f.rel is not None:
                yield f
        for f in m._meta.local_many_to_many:
            yield f

    def detect_reltype(self, rel):
        if isinstance(rel, OneToOneRel):
            return "11"
        elif isinstance(rel, ManyToManyRel):
            return "MM"
        elif isinstance(rel, ManyToOneRel):
            return "M1"


class Walker(object):
    def __init__(self, models, brain=Brain(), bidirection=False):
        self.models = models
        self.brain = brain
        self.history = OrderedDict()  # model -> Node
        self.temporary = {}  # model -> None (for a case bidirection is True)
        self.bidirection = bidirection

    @property
    def active_models(self):
        return self.history.keys()

    def walkall(self):
        for m in self.models:
            self.walk(m)

    def walk(self, m):
        if m in self.history:
            return self.history[m]
        if self.brain.is_skip(m):
            return
        return self._walk(m)

    def _walk(self, m):
        logger.debug("walking: model=%s", m)
        dependencies = []
        node = Node(model=m, dependencies=dependencies)
        self.history[m] = node
        for fk in self.brain.collect_dependencies(m):
            type_ = self.brain.detect_reltype(fk.rel)
            to_node = self.walk(fk.rel.to)
            if to_node is None:
                continue
            relation = Relation(name=fk.name, type=type_, from_=node, to=to_node)
            dependencies.append(relation)
            if self.bidirection:
                self._with_bidirection(node, fk)
        return node

    def _with_bidirection(self, node, fk):
        logger.debug("not supported")
        pass

    def __getitem__(self, model):
        return self.history[model]

    def __contains__(self, model):
        return model in self.history


class ReverseWalker(object):
    def __init__(self, walker, models=None):
        self.walker = walker
        self.toplevel = []
        self.cache = {}  # moel -> rnode
        self.models = models or walker.active_models

    def walkall(self):
        for m in self.models:
            node = self.walker[m]
            self.traverse(node)
        return self.models

    def traverse(self, node):
        if node.model in self.cache:
            return self.cache[node.model]
        children = []
        rnode = RNode(node=node, children=children)
        self.cache[node.model] = rnode
        if not node.dependencies:
            self.toplevel.append(rnode)
        for rel in node.dependencies:
            self.traverse(rel.to).children.append(rnode)
        return rnode

    def __getitem__(self, model):
        return self.cache[model]


def ordering_from_rwalker(rwalker):
    rwalker.walkall()
    ordered_models = []
    rhistory = set()  # model

    def traverse(rnode, category):
        model = rnode.node.model
        if model in rhistory:
            return category
        rhistory.add(model)
        for rel in rnode.node.dependencies:
            traverse(rwalker[rel.to.model], category)
        category.append(model)
        for c in rnode.children:
            traverse(c, category)
        return category

    for rnode in rwalker.toplevel:
        category = traverse(rnode, [])
        if not category:
            continue
        ordered_models.append(category)
    return ordered_models


def ordering(walker, models=None):
    rwalker = ReverseWalker(walker, models=models)
    return ordering_from_rwalker(rwalker)


class ModelMapProvider(object):
    def __init__(self, walker):
        self.walker = walker

    @cached_property
    def dependencies(self):
        """model to parent"""
        self.walker.walkall()
        return self.walker.history  # model -> Node

    @cached_property
    def rwalker(self):
        self.dependencies  # hmm
        return ReverseWalker(self.walker)

    @cached_property
    def reverse_dependencies(self):
        """model to children"""
        self.rwalker.walkall()
        return self.rwalker.cache  # model -> RNode

    @cached_property
    def ordered_models(self):
        """flatten ordered model's  list"""
        return [x for xs in self.cluster_models for x in xs]

    @cached_property
    def cluster_models(self):  # todo:rename
        """list of cluster ordered model's list"""
        self.dependencies  # hmm
        return ordering_from_rwalker(self.rwalker)


def _output(io, s):
    io.write(s)
    io.write("\n")


def write_tree_all(walker, output=_output, io=sys.stderr):
    for model in walker.active_models:
        write_tree(walker, model, output=output, io=io)


def write_tree(walker, model, output=_output, io=sys.stderr):
    history = set()

    def _write_tree(rel, indent):
        k = (rel.name, rel.to.model)
        if k in history:
            return
        history.add(k)

        node = rel.to
        model = node.model.__name__
        name = rel.name
        fmt = "{indent}{model}[{name}({reltype})]"
        output(io, fmt.format(indent=" " * indent, model=model, name=name, reltype=rel.type))
        for rel in node.dependencies:
            _write_tree(rel, indent + 2)

    output(io, model.__name__)
    node = walker[model]
    for relation in node.dependencies:
        _write_tree(relation, 2)
