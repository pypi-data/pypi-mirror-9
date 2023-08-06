# Copyright (c) 2015 Universidade Federal Fluminense (UFF)
# Copyright (c) 2015 Polytechnic Institute of New York University.
# This file is part of noWorkflow.
# Please, consult the license terms in the LICENSE file.

from __future__ import (absolute_import, print_function,
                        division, unicode_literals)

import time

from copy import deepcopy
from collections import namedtuple, OrderedDict, defaultdict

from .model import Model
from .trial import Trial, TreeElement, Single, Call
from .trial import Mixed, Group
from .trial_activation_visitors import TrialGraphVisitor
from .trial_activation_visitors import TrialGraphCombineVisitor
from ..utils import OrderedCounter, concat_iter


class hashabledict(dict):
    def el(self, e):
        if isinstance(e, dict):
            return hashabledict(e)
        else:
            return e

    def __key(self):
        return tuple((k,self.el(self[k])) for k in sorted(self))
    def __hash__(self):
        return hash(self.__key())
    def __eq__(self, other):
        return self.__key() == other.__key()


class activationdict(dict):
    def __key(self):
        return tuple((k,self[k]) for k in sorted(self))
    def __hash__(self):
        return hash(self.__key())
    def __eq__(self, other):
        return self['name'] == other['name']


class fadict(dict):
    def __key(self):
        return (self['name'],
                self['content_hash_before'],
                self['content_hash_after'])
    def __hash__(self):
        return hash(self.__key())
    def __eq__(self, other):
        return ((self['content_hash_before'] == other['content_hash_before'])
            and (self['content_hash_after'] == other['content_hash_after']))


class Diff(Model):
    """ This model represents a diff between two trials
    Initialize it by passing both trials ids:
        diff = Diff(2)

    There are two visualization modes for the graph:
        exact match: calls are only combined when all the sub-call match
            diff.graph_type = 0
        combined: calls are combined without considering the sub-calls
            diff.graph_type = 1

    There are also three visualization modes for the diff:
        combine graphs: combines both trial graphs
            diff.display_mode = 0
        side by side: displays both graphs side by side
            diff.display_mode = 1
        combined and side by side: combine graphs and displays both separated graphs
            diff.display_mode = 2


    You can change the graph width and height by the variables:
        diff.graph_width = 600
        diff.graph_height = 400
    """

    DEFAULT = {
        'graph_width': 500,
        'graph_height': 500,
        'graph_type': 0,
        'display_mode': 0,
    }

    def __init__(self, trial_id1, trial_id2, exit=False, **kwargs):
        super(Diff, self).__init__(trial_id1, trial_id2, exit=exit, **kwargs)
        self.initialize_default(kwargs)

        self.trial1 = Trial(trial_id1, exit=exit)
        self.trial2 = Trial(trial_id2, exit=exit)
        self._graph_types = {
            0: self.independent_naive_activation_graph,
            1: self.combined_naive_activation_graph
        }
        self._display_modes = {
            0: "combined",
            1: "side by side",
            2: "both",
        }
        self._independent_cache = None
        self._combined_cache = None


    def trial(self):
        """ Returns a tuple with the information of both trials """
        return diff_dict(self.trial1.info(), self.trial2.info())

    def modules(self):
        """ Diffs modules from trials """
        fn = lambda x: hashabledict(x)
        return diff_set(
            set(self.trial1.modules(fn)[1]),
            set(self.trial2.modules(fn)[1]))

    def environment(self):
        """ Diffs environment variables """
        return diff_set(
            dict_to_set(self.trial1.environment()),
            dict_to_set(self.trial2.environment()))

    def file_accesses(self):
        """ Diffs file accesses """
        return diff_set(
            set(fadict(fa) for fa in self.trial1.file_accesses()),
            set(fadict(fa) for fa in self.trial2.file_accesses()))

    def independent_naive_activation_graph(self):
        """ Generates an activation graph for both trials and transforms it into an
            exact match graph supported by d3 """
        if not self._independent_cache:
            g1 = self.trial1.independent_activation_graph()
            g2 = self.trial2.independent_activation_graph()
            self._independent_cache = NaiveGraphDiff(g1, g2).to_dict(), g1, g2
        return self._independent_cache

    def combined_naive_activation_graph(self):
        """ Generates an activation graph for both trials and transforms it into an
            combined graph supported by d3 """
        if not self._combined_cache:
            g1 = self.trial1.combined_activation_graph()
            g2 = self.trial2.combined_activation_graph()
            self._combined_cache = NaiveGraphDiff(g1, g2).to_dict(), g1, g2
        return self._combined_cache

    def _repr_html_(self):
        """ Displays d3 graph on ipython notebook """
        uid = str(int(time.time()*1000000))

        result = """
            <div class="nowip-diff" data-width="{width}"
                 data-height="{height}" data-uid="{uid}"
                 data-id1="{id1}" data-id2="{id2}" data-mode="{mode}">
                {data}
            </div>
        """.format(
            uid=uid, id1=self.trial1.id, id2=self.trial2.id,
            mode=self.display_mode,
            data=self.escape_json(self._graph_types[self.graph_type]()),
            width=self.graph_width, height=self.graph_height)
        return result


class NaiveGraphDiff(object):

    def __init__(self, g1, g2):
        self.id = 0
        self.nodes = []
        self.edges = []
        self.context_edges = {}
        self.old_to_new = {}
        self.max_duration = dict(concat_iter(
            g1['max_duration'].items(), g2['max_duration'].items()))

        self.min_duration = dict(concat_iter(
            g1['min_duration'].items(), g2['min_duration'].items()))

        self.merge(g1, g2)

    def fix_caller_id(self, graph):
        called = {}
        seq = defaultdict(list)
        nodes = graph['nodes']
        edges = [hashabledict(x) for x in graph['edges']]
        for edge in edges:
            if edge['type'] == 'call':
                called[edge['target']] = edge['source']
            if edge['type'] == 'sequence':
                seq[edge['source']].append(edge)

        visited = set()
        while called:
            t = {}
            for nid, parent in called.items():
                nodes[nid]['caller_id'] = parent
                visited.add(nid)
                for e in seq[nid]:
                    if not e['target'] in visited:
                        t[e['target']] = parent
            called = t

    def merge(self, g1, g2):
        self.fix_caller_id(g1)
        self.fix_caller_id(g2)
        nodes1 = [hashabledict(x) for x in g1['nodes']]
        nodes2 = [hashabledict(x) for x in g2['nodes']]
        def cmp_node(x, y):
            if x['name'] != y['name']:
                return False
            if x['caller_id'] is None and y['caller_id'] is not None:
                return False
            if x['caller_id'] is not None and y['caller_id'] is None:
                return False
            if x['caller_id'] is None and y['caller_id'] is None:
                return True
            caller1, caller2 = nodes1[x['caller_id']], nodes2[y['caller_id']]
            return caller1['name'] == caller2['name']

        res, _ = lcs(nodes1, nodes2, cmp_node)

        for a, b in res.items():
            n = deepcopy(a)
            del n['node']
            n['node1'] = a['node']
            n['node2'] = b['node']
            n['node1']['original'] = a['index']
            n['node2']['original'] = b['index']
            n['index'] = self.id
            a['node']['diff'] = self.id
            b['node']['diff'] = self.id
            self.old_to_new[(1, a['index'])] = self.id
            self.old_to_new[(2, b['index'])] = self.id
            self.id += 1
            self.nodes.append(n)

        self.add_nodes(nodes1, 1)
        self.add_nodes(nodes2, 2)
        self.add_edges(g1['edges'], 1)
        self.add_edges(g2['edges'], 2)

    def add_nodes(self, nodes, ng):
        for node in nodes:
            if not (ng, node['index']) in self.old_to_new:
                nid = self.add_node(node)
                self.old_to_new[(ng, node['index'])] = nid
                node['node']['diff'] = nid

    def add_edges(self, edges, ng):
        for edge in edges:
            if (ng, edge['source']) in self.old_to_new:
                self.add_edge(self.old_to_new[(ng, edge['source'])],
                              self.old_to_new[(ng, edge['target'])],
                              edge)

    def add_node(self, node):
        n = deepcopy(node)
        node_id = n['index'] = self.id
        n['node']['original'] = node['index']
        self.nodes.append(n)
        self.id += 1
        return node_id

    def add_edge(self, source, target, edge):
        edge_key = "{} {} {}".format(source, target, edge['type'])

        if not edge_key in self.context_edges:
            e = deepcopy(edge)
            e['source'] = source
            e['target'] = target
            self.edges.append(e)
            self.context_edges[edge_key] = e
        else:
            e = self.context_edges[edge_key]
            e['count'] = (e['count'], edge['count'])

    def to_dict(self):
        return {
            'max_duration': self.max_duration,
            'min_duration': self.min_duration,
            'nodes': self.nodes,
            'edges': self.edges,
        }


def dict_to_set(d):
    result = set()
    for key, value in d.items():
        result.add(activationdict({'name': key, 'value': value}))
    return result

def diff_dict(before, after):
    result = {}
    for key in before.keys():
        if key != 'id' and before[key] != after[key]:
            result[key] = [before[key], after[key]]
    return result

def diff_set(before, after):
    removed = before - after
    added = after - before
    replaced = set()

    removed_by_name = {}
    for element_removed in removed:
        removed_by_name[element_removed['name']] = element_removed
    for element_added in added:
        element_removed = removed_by_name.get(element_added['name'])
        if element_removed:
            replaced.add((element_removed, element_added))
    for (element_removed, element_added) in replaced:
        removed.discard(element_removed)
        added.discard(element_added)

    return (added, removed, replaced)

def lcs(a, b, eq=lambda x, y: x == y):
    lengths = [[0 for j in range(len(b)+1)] for i in range(len(a)+1)]
    # row 0 and column 0 are initialized to 0 already
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            if eq(x, y):
                lengths[i+1][j+1] = lengths[i][j] + 1
            else:
                lengths[i+1][j+1] = \
                    max(lengths[i+1][j], lengths[i][j+1])
    # read the substring out from the matrix
    result_a, result_b = OrderedCounter(), OrderedCounter()
    x, y = len(a), len(b)
    while x != 0 and y != 0:
        if lengths[x][y] == lengths[x-1][y]:
            x -= 1
        elif lengths[x][y] == lengths[x][y-1]:
            y -= 1
        else:
            result_a[a[x-1]] = b[y-1]
            result_b[b[y-1]] = a[x-1]
            x -= 1
            y -= 1
    return result_a, result_b
