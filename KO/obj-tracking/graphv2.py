import sys
from typing import Dict


class Edge:
    def __init__(self, edge_id: int, src: 'Node', dst: 'Node', cost=0, flow=0, lb=0, ub=0):
        self.id = edge_id
        self.lb: int = lb
        self.ub: int = ub
        self.src: 'Node' = src
        self.dst: 'Node' = dst
        self.cost: int = cost
        self.flow: int = flow
        self.reverse: Edge = None

    def __str__(self):
        return f'id: {self.id}, src: {self.src.id}, dst: {self.dst.id}, cost: {self.cost}, flow: {self.flow}, ' \
               f'address: {hex(id(self))}'


class Node:
    def __init__(self, node_id: int):
        self.id = node_id
        self.in_edges: Dict[int, Edge] = {}
        self.out_edges: Dict[int, Edge] = {}

    def add_in_edge(self, src: 'Node', e: Edge):
        self.in_edges[src.id] = e

    def add_out_edge(self, dst: 'Node', e: Edge):
        self.out_edges[dst.id] = e

    def remove_in_edge(self, src: 'Node'):
        del self.in_edges[src.id]

    def remove_out_edge(self, dst: 'Node'):
        del self.out_edges[dst.id]

    def get_in_edge(self, src: 'Node'):
        return self.in_edges[src.id]

    def get_out_edge(self, dst: 'Node'):
        return self.out_edges[dst.id]

    def get_edges(self):
        return list(self.in_edges.values()) + list(self.out_edges.values())

    def __str__(self):
        return f'id: {self.id}, address: {hex(id(self))}'


class Graph:
    def __init__(self):
        self.num_nodes = 0
        self.num_edges = 0
        self.node_id_generator = iter(range(sys.maxsize))
        self.edge_id_generator = iter(range(sys.maxsize))

        self.adjacency_dict: Dict[int, Dict[int, Node]] = {}
        self.edge_dict: Dict[int, Edge] = {}
        self.node_dict: Dict[int, Node] = {}

    def __get_node_id(self):
        return next(self.node_id_generator)

    def __get_edge_id(self):
        return next(self.edge_id_generator)

    def add_node(self) -> Node:
        self.num_nodes += 1
        node_id = self.__get_node_id()
        node = Node(node_id)
        self.node_dict[node_id] = node
        self.adjacency_dict[node_id] = {}
        return node

    def add_edge(self, src: Node, dst: Node, lb, ub, cost, flow=0) -> Edge:
        if dst.id in self.adjacency_dict[src.id]:
            raise ValueError()
        self.adjacency_dict[src.id][dst.id] = dst
        edge_id = self.__get_edge_id()
        e = Edge(edge_id, src, dst, cost=cost, lb=lb, ub=ub, flow=flow)
        src.add_out_edge(dst, e)
        dst.add_in_edge(src, e)
        self.edge_dict[edge_id] = e
        self.num_edges += 1
        return e

    def remove_edge(self, edge_id: int):
        e = self.edge_dict.pop(edge_id)
        if e.reverse is not None:
            e.reverse.reverse = None
        e.src.remove_out_edge(e.dst)
        e.dst.remove_in_edge(e.src)
        if e.src.id in self.adjacency_dict:
            del self.adjacency_dict[e.src.id][e.dst.id]
        del e
        self.num_edges -= 1

    def remove_node(self, node_id: int):
        node = self.node_dict.pop(node_id)
        del self.adjacency_dict[node.id]
        for e in node.get_edges():
            self.remove_edge(e.id)
        del node
        self.num_nodes -= 1
