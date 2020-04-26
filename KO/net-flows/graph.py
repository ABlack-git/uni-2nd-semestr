from entites import InputData
from typing import List, Union, Dict
from collections import deque


class Edge:
    def __init__(self, s, t, flow=0, lb=0, ub=0):
        self.lb: int = lb
        self.ub: int = ub
        self.s: int = s  # source vertex
        self.t: int = t  # sink vertex
        self.flow: int = flow
        self.reverse: Edge = None


class Graph:
    def __init__(self, c_size, p_size, additional_nodes=False):
        self.c_size = c_size
        self.p_size = p_size
        self.additional_nodes = additional_nodes
        self.num_nodes = self.c_size + self.p_size + (4 if self.additional_nodes else 2)
        self._sink_idx = self.c_size + self.p_size + 1
        self.first_p = self.c_size + 1
        self._source_idx = 0
        if self.additional_nodes:
            self._source_hat_idx = self._sink_idx + 1
            self._sink_hat_idx = self._source_hat_idx + 1

        self.adj_list: List[List[Edge]] = [[] for _ in range(self.num_nodes)]
        self.in_edges: List[List[Edge]] = [[] for _ in range(self.num_nodes)]
        self.edge_map: List[Dict[int, Edge]] = [{} for _ in range(self.num_nodes)]

    def add_edge(self, s, t, lb, ub):
        e = Edge(s, t, lb=lb, ub=ub)
        self.adj_list[s].append(e)
        self.in_edges[t].append(e)
        self.edge_map[s][t] = e

    def _add_edge(self, e: Edge):
        self.adj_list[e.s].append(e)

    def get_edge(self, s, t):
        return self.edge_map[s][t]

    def get_out_edges_of(self, v) -> List[Edge]:
        return self.adj_list[v]

    def get_in_edges_of(self, v):
        return self.in_edges[v]

    def get_balance_of(self, v):
        return sum([e.lb for e in self.get_in_edges_of(v)]) - sum([e.lb for e in self.get_out_edges_of(v)])

    def add_reverse_edges(self):
        for s in range(self.num_nodes):
            for e in self.get_out_edges_of(s):
                if e.ub == 0:
                    continue
                re = Edge(e.t, e.s, ub=0)
                re.reverse = e
                e.reverse = re
                self._add_edge(re)

    @property
    def sink_idx(self):
        if self.additional_nodes:
            return self._sink_hat_idx
        return self._sink_idx

    @property
    def source_idx(self):
        if self.additional_nodes:
            return self._source_hat_idx
        return self._source_idx


def build_graph_from_input(data: InputData) -> Graph:
    g = Graph(data.c_size, data.p_size)
    for c_id, c in data.customers.items():
        g.add_edge(g.source_idx, c_id, lb=c.lb, ub=c.ub)
        for p in c.products:
            g.add_edge(c_id, g.first_p + p, lb=0, ub=1)

    for p_id, p in data.products.items():
        g.add_edge(g.first_p + p_id, g.sink_idx, lb=p.lb, ub=p.ub)
    return g


def build_graph_with_zero_lb(g: Graph) -> Graph:
    g_hat = Graph(g.c_size, g.p_size, additional_nodes=True)
    g_hat.add_edge(g.sink_idx, g.source_idx, 0, float('inf'))
    for i in range(g.num_nodes):
        for e in g.get_out_edges_of(i):
            g_hat.add_edge(e.s, e.t, lb=0, ub=e.ub - e.lb)
        balance_i = g.get_balance_of(i)
        if balance_i > 0:
            g_hat.add_edge(g_hat.source_idx, i, 0, balance_i)
        elif balance_i < 0:
            g_hat.add_edge(i, g_hat.sink_idx, 0, -balance_i)
        else:
            pass

    return g_hat


def shortest_path_bfs(g: Graph) -> List[Union[None, Edge]]:
    q = deque()
    q.append(g.source_idx)
    parent: List[Union[None, Edge]] = [None] * g.num_nodes
    while len(q) > 0:
        v = q.popleft()
        for e in g.get_out_edges_of(v):
            if parent[e.t] is None and e.t != g.source_idx and e.ub > e.flow:
                parent[e.t] = e
                q.append(e.t)
    return parent


def find_augmenting_path(g: Graph):
    path = shortest_path_bfs(g)
    df = float('inf')
    e = path[g.sink_idx]
    while e is not None:
        df = min(df, e.ub - e.flow)
        e = path[e.s]
    return df, path


def maximise_flow(g: Graph):
    """
    :param g: g_hat = build_graph_with_zero_lb(g) and g_hat.add_reverse_edges()
    :return:
    """
    while True:
        df, path = find_augmenting_path(g)
        if path[g.sink_idx] is None:
            break
        e = path[g.sink_idx]
        while e is not None:
            e.flow += df
            e.reverse.flow -= df
            e = path[e.s]


def s_hat_edges_saturated(g: Graph):
    for e in g.get_out_edges_of(g.source_idx):
        if e.ub != e.flow:
            return False
    return True


def get_review_assignments(g: Graph):
    ret = [[] for _ in range(g.c_size)]
    for c in range(g.c_size):
        for e in g.get_out_edges_of(c + 1):
            if e.flow == 1:
                ret[c].append(e.t - g.first_p + 1)
    return ret
