import copy
from collections import deque
from typing import Dict, Any, List, Union, Tuple

from graphv2 import Graph, Node, Edge


class MaxFlowGraph(Graph):
    def __init__(self):
        super(MaxFlowGraph, self).__init__()
        self.source: Node = self.add_node()
        self.sink: Node = self.add_node()
        self.source_hat: Node = None
        self.sink_hat: Node = None

        self.node_mapping: Dict[Any, Node] = {}
        self.forward_edges = {}
        self.backward_edges = {}
        self.aux_edges = {}

    def add_node_by_name(self, name):
        self.node_mapping[name] = self.add_node(name)
        return self.node_mapping[name]

    def add_edge(self, src: Node, dst: Node, lb, ub, cost=0, flow=0, e_type='forward') -> Edge:
        e = super(MaxFlowGraph, self).add_edge(src, dst, lb, ub, cost, flow)
        if e_type == 'forward':
            self.forward_edges[e.id] = e
        elif e_type == 'aux':
            self.aux_edges[e.id] = e
        else:
            raise ValueError(f'Unknown e_type: {e_type}')
        return e

    def add_reverse_edge(self, e: Edge):
        e_rev = super(MaxFlowGraph, self).add_edge(e.dst, e.src, lb=0, ub=0)
        e.reverse = e_rev
        e_rev.reverse = e
        self.backward_edges[e.id] = e
        return e_rev

    @property
    def g_source(self):
        return self.source if self.source_hat is None else self.source_hat

    @property
    def g_sink(self):
        return self.sink if self.sink_hat is None else self.sink_hat

    def add_reverse_edges(self):
        for e in list(self.edge_dict.values()):
            if e.ub != 0:
                self.add_reverse_edge(e)


def s_hat_edges_saturated(g: MaxFlowGraph):
    for e in g.g_source.out_edges.values():
        if e.ub != e.flow:
            return False
    return True


def assign_flow(g_src: MaxFlowGraph, g_dst: MaxFlowGraph):
    for e_id, e in g_dst.edge_dict.items():
        e.flow = g_src.edge_dict[e_id].flow + e.lb


def build_graph_with_zero_lb(g: MaxFlowGraph) -> MaxFlowGraph:
    g_hat = copy.deepcopy(g)
    g_hat.source_hat = g_hat.add_node()
    g_hat.sink_hat = g_hat.add_node()

    for node in g_hat.node_dict.values():
        if node is g_hat.source_hat or node is g_hat.sink_hat:
            continue
        balance = g.node_dict[node.id].get_balance()
        for e in node.out_edges.values():
            e.ub = e.ub - e.lb
            e.lb = 0
        if balance > 0:
            g_hat.add_edge(g_hat.source_hat, node, lb=0, ub=balance, e_type='aux')
        elif balance < 0:
            g_hat.add_edge(node, g_hat.sink_hat, lb=0, ub=-balance, e_type='aux')
        else:
            pass

    g_hat.add_edge(g_hat.sink, g_hat.source, lb=0, ub=float('inf'), e_type='aux')
    return g_hat


def maximise_flow(g: MaxFlowGraph):
    g_copy = copy.deepcopy(g)
    g_copy.add_reverse_edges()
    while True:
        df, path = find_augmenting_paths(g_copy)
        if g_copy.g_sink.id not in path:
            break
        e: Edge = path[g_copy.g_sink.id]
        while e is not None:
            e.flow += df
            e.reverse.flow -= df
            e = path[e.src.id] if e.src.id in path else None

    for e in g_copy.forward_edges.values():
        g.forward_edges[e.id].flow = e.flow
    for e in g_copy.aux_edges.values():
        g.aux_edges[e.id].flow = e.flow


def find_augmenting_paths(g: MaxFlowGraph) -> Tuple[float, dict]:
    path = shortest_path_bfs(g)
    df = float('inf')
    e: Edge = path[g.g_sink.id] if g.g_sink.id in path else None
    while e is not None:
        df = min(df, e.ub - e.flow)
        e = path[e.src.id] if e.src.id in path else None
    return df, path


def shortest_path_bfs(g: MaxFlowGraph) -> dict:
    q = deque()
    q.append(g.g_source)
    parent: dict = {}
    while len(q) > 0:
        v: Node = q.popleft()
        for e in v.out_edges.values():
            if e.dst.id not in parent and e.dst.id != g.g_source.id and e.ub > e.flow:
                parent[e.dst.id] = e
                q.append(e.dst)
    return parent
