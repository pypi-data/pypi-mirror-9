# -*- coding:utf-8 -*-
# (setenv "LC_ALL" "ja_JP.UTF-8")
import sys
import logging
from functools import lru_cache
from django.db.models import (
    ManyToOneRel,
    OneToOneRel,
    ManyToManyRel
)
from collections import (
    OrderedDict,
    defaultdict
)
from django.utils.functional import cached_property
logger = logging.getLogger(__name__)


class Node(object):
    def __init__(self, model, dependencies):
        self.model = model
        self.dependencies = dependencies


class RNode(object):
    def __init__(self, node, dependencies):
        self.node = node
        self.dependencies = dependencies


class Relation(object):
    def __init__(self, name, type, from_, to, backref, through, fkname):
        self.name = name
        self.from_ = from_
        self.to = to
        self.type = type
        self.backref = backref
        self.through = through
        self.fkname = fkname


class Brain(object):  # bad name..
    def is_skip(self, m):
        return m._meta.abstract

    def is_foreinkey(self, f):
        return f.rel is not None

    def fkname_from_field(self, f):
        suffix = f.db_column or "_id"
        return f.name + suffix

    def collect_dependencies(self, m):
        for f in m._meta.local_fields:
            if self.is_foreinkey(f):
                yield f
        for f in m._meta.local_many_to_many:
            yield f

    def detect_reltype(self, fk):
        rel = fk.rel
        if isinstance(rel, OneToOneRel):
            return "11"
        elif isinstance(rel, ManyToManyRel):
            return "MM"
        elif isinstance(rel, ManyToOneRel):
            return "M1"

    def detect_reverse_reltype(self, reltype):
        if reltype == "M1":
            return "1M"
        return reltype

    def detect_reverse_foreignkey(self, model, name, rtype):
        if rtype == "MM":
            for f in model._meta.many_to_many:
                if f.name == name:
                    return f
            else:
                return None

    def detect_ref_name(self, fk):
        return fk.name

    def detect_backref_name(self, fk):
        backref = fk.related.get_accessor_name()
        if backref == "+":
            return None
        return backref

    def detect_through(self, fk, reltype):
        if reltype != "MM":
            return None
        return fk.rel.through


class Walker(object):
    def __init__(self, models, brain=Brain()):
        self.models = models
        self.brain = brain
        self.history = OrderedDict()  # model -> Node
        self.through_models = {}

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
        parents = []
        node = Node(model=m, dependencies=parents)
        self.history[m] = node
        for fk in self.brain.collect_dependencies(m):
            type_ = self.brain.detect_reltype(fk)
            to_node = self.walk(fk.rel.to)
            if to_node is None:
                continue
            ref = self.brain.detect_ref_name(fk)
            backref = self.brain.detect_backref_name(fk)
            through = self.brain.detect_through(fk, type_)
            fkname = self.brain.fkname_from_field(fk)
            if through is not None:
                through_model = through
                through = self.walk(through_model)
                self.through_models[through_model] = through
                fkname = None
            relation = Relation(name=ref, type=type_, from_=node, to=to_node, backref=backref, through=through, fkname=fkname)
            parents.append(relation)
        return node

    def __getitem__(self, model):
        return self.history[model]

    def __contains__(self, model):
        return model in self.history


class BidirectionalWalker(Walker):
    def __init__(self, models, brain=Brain()):
        super(BidirectionalWalker, self).__init__(models, brain)
        self.related_node = {}

    def get_node(self, model):
        if model in self.related_node:
            return self.related_node[model]
        else:
            v = self.related_node[model] = Node(model=model, dependencies=[])
            return v

    def walk(self, m, skip_reverse=False):
        if m in self.history:
            return self.history[m]
        if self.brain.is_skip(m):
            return
        return self._walk(m, skip_reverse=skip_reverse)

    def _walk(self, m, skip_reverse=False):
        logger.debug("walking: model=%s", m)
        node = self.get_node(m)
        self.history[m] = node
        for fk in self.brain.collect_dependencies(m):
            type_ = self.brain.detect_reltype(fk)
            to_node = self.walk(fk.rel.to)
            if to_node is None:
                continue
            ref = self.brain.detect_ref_name(fk)
            backref = self.brain.detect_backref_name(fk)
            through = self.brain.detect_through(fk, type_)
            fkname = self.brain.fkname_from_field(fk)
            if through is not None:
                through_model = through
                through = self.walk(through_model, skip_reverse=True)
                self.through_models[through_model] = through
                fkname = None
            relation = Relation(name=ref, type=type_, from_=node, to=to_node, backref=backref, through=through, fkname=fkname)
            if backref is not None and not skip_reverse:
                if node not in to_node.dependencies:
                    # reverse relation. to -> from
                    rtype = self.brain.detect_reverse_reltype(type_)
                    back_fkname = None  # xxx
                    back_relation = Relation(name=backref, type=rtype, from_=to_node, to=node, backref=ref, through=through, fkname=back_fkname)
                    to_node.dependencies.append(back_relation)
            node.dependencies.append(relation)
        return node


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
        rnode = RNode(node=node, dependencies=children)
        self.cache[node.model] = rnode
        if not node.dependencies:
            self.toplevel.append(rnode)
        for rel in node.dependencies:
            self.traverse(rel.to).dependencies.append(rnode)
        return rnode

    def __getitem__(self, model):
        return self.cache[model]


def ordering_from_rwalker(rwalker):
    rwalker.walkall()
    ordered_models = []
    rhistory = set()  # model

    def traverse(rnode, category, queue):
        model = rnode.node.model
        if model in rhistory:
            # assert all(rel.to.model in category for rel in rnode.node.dependencies if not rnode.node.model == rel.to.model)
            return category
        rhistory.add(model)
        for rel in rnode.node.dependencies:
            traverse(rwalker[rel.to.model], category, queue)
        # assert all(rel.to.model in category for rel in rnode.node.dependencies if not rnode.node.model == rel.to.model)
        category.append(model)
        for c in rnode.dependencies:
            queue.append(c)
        return category

    for rnode in rwalker.toplevel:
        category = []
        queue = []
        category = traverse(rnode, category, queue)
        while queue:
            rnode_ = queue.pop(0)
            traverse(rnode_, category, queue)
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

    @property
    def brain(self):
        return self.walker.brain

    def is_through_model(self, model):
        return model in self.walker.through_models

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


# experimental

class Collector(object):
    def __init__(self, mmprovider):
        self.mmprovider = mmprovider
        self.brain = mmprovider.brain
        self.identity_map = defaultdict(dict)  # model -> pk -> object

    @lru_cache()
    def collect(self, ob):
        return self._collect(ob, set())

    def get_related_object(self, ob, fk, relation):
        ob_map = self.identity_map[relation.to.model]
        try:
            return ob_map[fk]
        except KeyError:
            v = ob_map[fk] = getattr(ob, relation.name, None)
            return v

    def _collect(self, ob, r, see_related=True):
        if ob in r:
            return r
        r.add(ob)
        model = ob.__class__
        mm_history = set()
        for relation in self.mmprovider.dependencies[model].dependencies:
            if relation.type == "MM" and see_related:
                mm_history.add((ob.__class__, relation.name))
                for relob in getattr(ob, relation.name).all():
                    self._collect(relob, r, see_related=False)
            elif relation.type == "M1" or relation.type == "11":
                if relation.fkname:
                    fk = getattr(ob, relation.fkname)
                    relob = self.get_related_object(ob, fk, relation)
                else:
                    relob = getattr(ob, relation.name)
                    self.identity_map[relob.__module__][getattr(relob, "id", None) or object()] = relob  # hmm
                if relob is not None:
                    self._collect(relob, r)

        # for MM
        for rnode in self.mmprovider.reverse_dependencies[model].dependencies:
            for relation in rnode.node.dependencies:
                if relation.type == "MM" and relation.to.model == model:
                    if (ob.__class__, relation.backref) not in mm_history:
                        for relob in getattr(ob, relation.backref).all():
                            self._collect(relob, r)

        return r


# shortcut function
def get_walker(models=None, brain=None, Walker=Walker):
    if models is None:
        from django.apps import apps
        models = apps.get_models()
    return Walker(models, brain=brain or Brain())


def get_mmprovider(models=None, brain=None):
    walker = get_walker(models, brain)
    return ModelMapProvider(walker)


def get_collector(models=None, brain=None):
    walker = get_walker(models, brain, Walker=BidirectionalWalker)
    return Collector(ModelMapProvider(walker))
