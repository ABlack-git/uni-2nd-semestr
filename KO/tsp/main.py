#!/usr/bin/env python3
import sys

import gurobipy as grb
import numpy as np
import subtourelim


def read_input(path):
    with open(path, 'r') as f:
        n, w, h = [int(x) for x in f.readline().split()]
        c = 3
        stripes = np.zeros((n, h, 2, c))
        for stripe_num in range(n):
            stripe = [int(x) for x in f.readline().split()]
            for stripe_row in range(h):
                row = stripe[stripe_row * (w * c):(stripe_row * (w * c) + (w * c))]
                for stripe_col in range(2):
                    col = row[stripe_col * (w - 1) * c:stripe_col * (w - 1) * c + c]
                    for channel in range(c):
                        stripes[stripe_num, stripe_row, stripe_col, channel] = col[channel]
    return stripes


def compute_distances(stripes: np.ndarray):
    left_border = stripes[:, :, 0, :]
    right_border = stripes[:, :, 1, :]
    distances = np.zeros((stripes.shape[0] + 1, stripes.shape[0] + 1))
    tmp_dst = np.sum(np.sum(np.abs(right_border[:, np.newaxis, :] - left_border), axis=-1), axis=-1)
    distances[1:distances.shape[0] + 1, 1:distances.shape[1] + 1] = tmp_dst[:]
    return distances


def compute_distances_slow(stripes: np.ndarray):
    dist = np.zeros((stripes.shape[0], stripes.shape[0]))
    for i in range(stripes.shape[0]):
        for j in range(stripes.shape[0]):
            dist[i, j] = np.sum(np.sum(np.abs(stripes[i, :, 1, :] - stripes[j, :, 0, :]), axis=1))
    return dist


def save_output(path, permutations):
    solution = []
    for i in range(1, len(permutations) + 1):
        solution.append(str(permutations[i]))
    with open(path, 'w') as f:
        f.write(' '.join(solution))


def get_permutations(var: grb.tupledict):
    adj_list = {}
    for i, j in var.keys():
        if var[i, j].x > 0.5:
            adj_list[i] = j
    permutations = {}  # key: node, val: permutation
    start = 0
    next_node = adj_list[start]
    counter = 1
    permutations[counter] = next_node
    while True:
        next_node = adj_list[next_node]
        if next_node == start:
            break
        counter += 1
        permutations[counter] = next_node

    return permutations


def main():
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    stripes = read_input(input_file)
    tmp_dst = compute_distances_slow(stripes)
    distances = compute_distances(stripes)
    model = grb.Model()
    model.Params.lazyConstraints = 1
    model._num_nodes = stripes.shape[0] + 1
    indices = [(i, j) for i in range(model._num_nodes) for j in range(model._num_nodes) if i != j]
    x_vars: grb.tupledict = model.addVars(indices, vtype=grb.GRB.BINARY, name='x')
    model._x = x_vars
    model._dists = distances

    model.addConstrs((x_vars.sum(i, '*') == 1 for i in range(model._num_nodes)), name='out-deg')
    model.addConstrs((x_vars.sum('*', j) == 1 for j in range(model._num_nodes)), name='in-deg')

    model.setObjective(grb.quicksum([x_vars[i, j] * distances[i, j] for i, j in indices]), grb.GRB.MINIMIZE)
    model.optimize(subtourelim.tsp_callback)
    perms = get_permutations(x_vars)
    save_output(output_file, perms)


if __name__ == '__main__':
    main()
