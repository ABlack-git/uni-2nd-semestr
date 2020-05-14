from graphv2 import Graph, Node, Edge
from typing import List, Dict, Union
from inoutdata import InputData
from collections import deque
import copy
import sys


class MinCostGraph(Graph):
    def __init__(self):
        super(MinCostGraph, self).__init__()
        self.source_node: Node = None
        self.sink_node: Node = None
        self.l1_nodes: List[Node] = []
        self.l2_nodes: List[Node] = []
        self.forward_edges: Dict[int, Edge] = {}
        self.backward_edges: Dict[int, Edge] = {}
        self.source_hat_node: Node = None
        self.sink_hat_node: Node = None

    def add_node_by_type(self, node_type):
        if node_type not in ('sink', 'source', 'sink_hat', 'source_hat', 'l1', 'l2'):
            raise ValueError(f'Unknown node type: {node_type}')
        node = self.add_node()
        if node_type == 'sink':
            self.sink_node = node
        elif node_type == 'source':
            self.source_node = node
        elif node_type == 'sink_hat':
            self.sink_hat_node = node
        elif node_type == 'source_hat':
            self.source_hat_node = node
        elif node_type == 'l1':
            self.l1_nodes.append(node)
        elif node_type == 'l2':
            self.l2_nodes.append(node)
        return node

    def add_forward_edge(self, src: Node, dest: Node, lb, ub, cost, flow):
        e = self.add_edge(src, dest, lb, ub, cost, flow)
        self.forward_edges[e.id] = e
        return e

    def add_reverse_edge(self, e: Edge, lb, ub, cost, flow):
        e_rev = self.add_edge(e.dst, e.src, lb, ub, cost, flow)
        e.reverse = e_rev
        e_rev.reverse = e
        self.backward_edges[e_rev.id] = e_rev

    def edge_is_forward(self, e: Edge) -> bool:
        return e.id in self.forward_edges

    def remove_edge(self, edge_id: int):
        if edge_id in self.backward_edges:
            del self.backward_edges[edge_id]
        elif edge_id in self.forward_edges:
            del self.forward_edges[edge_id]
        super(MinCostGraph, self).remove_edge(edge_id)


def get_obj_mapping(g: MinCostGraph) -> List[int]:
    mappings = []
    for i, node in enumerate(g.l1_nodes):
        for e in node.out_edges.values():
            if e.flow == 1:
                mappings.append(g.l2_nodes.index(e.dst) + 1)
    return mappings


def build_mincost_graph(data: InputData, f1_index, f2_index):
    g = MinCostGraph()
    g.add_node_by_type('source')
    g.add_node_by_type('sink')
    for i in range(data.num_objects):
        node_l1 = g.add_node_by_type('l1')
        g.add_forward_edge(g.source_node, node_l1, lb=1, ub=1, cost=0, flow=1)
        node_l2 = g.add_node_by_type('l2')
        g.add_forward_edge(node_l2, g.sink_node, lb=1, ub=1, cost=0, flow=1)

    distance_matrix = data.get_distance_matrix(f1_index, f2_index)
    for i in range(data.num_objects):
        for j in range(data.num_objects):
            flow = 1 if i == j else 0
            g.add_forward_edge(g.l1_nodes[i], g.l2_nodes[j], lb=0, ub=1, cost=distance_matrix[i][j], flow=flow)
    return g


def remove_edges_with_zero_lb(g: MinCostGraph):
    for e in list(g.edge_dict.values()):
        if e.ub == 0:
            g.remove_edge(e.id)


def build_residual_graph(g: MinCostGraph):
    g_res = copy.deepcopy(g)

    for e in list(g_res.edge_dict.values()):
        g_res.add_reverse_edge(e, lb=0, ub=e.flow - e.lb, cost=-e.cost, flow=0)
        e.ub = e.ub - e.flow
        e.lb = 0
        e.flow = 0

    # add dummy vertex and connections
    g_res.add_node_by_type('source_hat')
    for node in g_res.node_dict.values():
        g_res.add_forward_edge(g_res.source_hat_node, node, lb=0, ub=sys.maxsize, cost=0, flow=0)
    return g_res


def bellman_ford_negative_cycle(g: MinCostGraph) -> Union[List[Edge], None]:
    remove_edges_with_zero_lb(g)
    distances = {key: float('inf') for key in g.node_dict.keys()}
    parent = {key: None for key in g.node_dict.keys()}
    distances[g.source_hat_node.id] = 0
    last_updated_node = None
    for _ in range(g.num_nodes):
        last_updated_node = None
        for e in g.edge_dict.values():
            dist = distances[e.src.id] + e.cost
            if dist < distances[e.dst.id]:
                distances[e.dst.id] = dist
                parent[e.dst.id] = e.src
                last_updated_node = e.dst

    if last_updated_node is None:
        return None
    else:
        y = last_updated_node
        for _ in parent:
            y = parent[y.id]
        curr = y
        path = deque()
        cntr = 0
        while True:
            if cntr > g.num_nodes:
                raise InterruptedError('To many iterations in bellman-ford')
            path.appendleft(curr)
            if curr is y and len(path) > 1:
                break
            curr = parent[curr.id]
            cntr += 1
    return _edges_from_path(path)


def _edges_from_path(path: deque) -> List[Edge]:
    src_node = path.popleft()
    edges = []
    try:

        while True:
            dst_node = path.popleft()
            e = src_node.get_out_edge(dst_node)
            edges.append(e)
            src_node = dst_node
    except IndexError as e:
        return edges


def minimize_cost(g: MinCostGraph):
    """
    Cycle cancelling algorithm, main loop
    :return:
    """
    g_res = build_residual_graph(g)
    cntr = 0
    while True:
        if cntr > g.num_nodes * 2:
            raise InterruptedError('To many iterations in min-cost')
        cycle = bellman_ford_negative_cycle(g_res)
        if cycle is None:
            break
        capacity = min([e.ub for e in cycle])
        for e in cycle:
            if g_res.edge_is_forward(e):
                e_hat = g.node_dict[e.src.id].get_out_edge(e.dst)
                e_hat.flow = e_hat.flow + capacity
            else:
                e_rev = g.node_dict[e.dst.id].get_out_edge(e.src)
                g.edge_dict[e_rev.id].flow = g.edge_dict[e_rev.id].flow - capacity
            e.ub = e.ub - capacity

            if e.reverse is None:
                if g_res.edge_is_forward(e):
                    g_res.add_reverse_edge(e, lb=0, ub=capacity, cost=-e.cost, flow=0)
                else:
                    e_hat = g_res.add_forward_edge(e.dst, e.src, lb=0, ub=capacity, cost=-e.cost, flow=0)
                    e_hat.reverse = e
                    e.reverse = e_hat
            else:
                e.reverse.ub = e.reverse.ub + capacity
        cntr += 1
