#!/usr/bin/env python3
import sys
import graph
from entites import InputData


def read_input(path):
    with open(path, 'r') as f:
        c_size, p_size = f.readline().split()
        c_size, p_size = int(c_size), int(p_size)
        data = InputData(c_size, p_size)
        for i in range(1, c_size + 1):
            c_line = f.readline().split()
            data.customers[i].lb = int(c_line[0])
            c_line[0] = 'r'
            data.customers[i].ub = int(c_line[1])
            c_line[1] = 'r'
            data.customers[i].products = [int(p) - 1 for p in c_line if p != 'r']
            for p in data.customers[i].products:
                data.products[p].ub += 1
        p_line = f.readline().split()
        p_line = [int(p) for p in p_line]
        for i in range(p_size):
            data.products[i].lb = p_line[i]
    return data


def save_output(path, reviews):
    with open(path, 'w') as f:
        for i, line in enumerate(reviews):
            line = [str(x) for x in line]
            f.write(' '.join(line))
            if i + 1 != len(reviews):
                f.write('\n')


def main():
    in_path = sys.argv[1]
    out_path = sys.argv[2]
    data = read_input(in_path)
    g = graph.build_graph_from_input(data)
    g_hat = graph.build_graph_with_zero_lb(g)
    g_hat.add_reverse_edges()
    graph.maximise_flow(g_hat)
    if graph.s_hat_edges_saturated(g_hat):
        for v in range(g.num_nodes):
            for e in g.get_out_edges_of(v):
                e_hat = g_hat.get_edge(e.s, e.t)
                e.flow = e_hat.flow + e.lb
        g.add_reverse_edges()
        graph.maximise_flow(g)
        reviews = graph.get_review_assignments(g)
    else:
        reviews = [[-1]]

    save_output(out_path, reviews)


main()
