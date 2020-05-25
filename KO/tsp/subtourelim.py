from typing import List, Dict

import gurobipy as grb
import numpy as np


def tsp_callback(model: grb.Model, where):
    if where == grb.GRB.Callback.MIPSOL:
        x = model._x
        sub_tours = find_sub_tours(x, model)
        if len(sub_tours) > 1:
            min_set = sub_tours[np.argmin([s['cost'] for s in sub_tours])]['path']
            model.cbLazy(grb.quicksum([x[i, j] for i, j in min_set if i != j]) <= (len(min_set) - 1))


def find_sub_tours(var: grb.tupledict, model: grb.Model) -> List[Dict]:
    adj_list = build_adj_list(var, model)
    visited = [False] * model._num_nodes
    sub_tours_list = []
    for i in range(model._num_nodes):
        if not visited[i]:
            visited[i] = True
            edge_set = graph_traversal(adj_list, i, visited, model._dists)
            sub_tours_list.append(edge_set)
    return sub_tours_list


def graph_traversal(adj_list: dict, start_v: int, visited, cost: np.ndarray) -> dict:
    edges = {'path': [], 'cost': 0}
    next_node = adj_list[start_v]
    edges['path'].append((start_v, next_node))
    edges['cost'] += cost[start_v, next_node]
    visited[next_node] = True
    while True:
        dst_node = adj_list[next_node]
        edges['path'].append((next_node, dst_node))
        edges['cost'] += cost[next_node, dst_node]
        next_node = dst_node
        visited[next_node] = True
        if next_node == start_v:
            break
    return edges


def build_adj_list(var: grb.tupledict, model: grb.Model) -> dict:
    adj_dict = {}
    for i, j in var.keys():
        if model.cbGetSolution(var[i, j]) > 0.5:
            adj_dict[i] = j
    return adj_dict
