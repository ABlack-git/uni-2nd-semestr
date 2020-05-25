import sys

from entites import InputData
from maxflow import MaxFlowGraph, build_graph_with_zero_lb, maximise_flow, s_hat_edges_saturated, assign_flow


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


def build_graph(data: InputData):
    g = MaxFlowGraph()
    for c_id, c in data.customers.items():
        c_node = g.add_node_by_name(f'c_{c_id}')
        g.add_edge(g.source, c_node, c.lb, c.ub)

    for p_id, p in data.products.items():
        p_node = g.add_node_by_name(f'p_{p_id+1}')
        g.add_edge(p_node, g.sink, p.lb, p.ub)

    for c_id, c in data.customers.items():

        for p_id in c.products:
            c_node = g.node_mapping[f'c_{c_id}']
            p_node = g.node_mapping[f'p_{p_id+1}']
            g.add_edge(c_node, p_node, lb=0, ub=1)
    return g


def get_review_assignments(g: MaxFlowGraph, data: InputData):
    assignments = [[] for _ in range(len(data.customers))]
    for c_id in data.customers.keys():
        node = g.node_mapping[f'c_{c_id}']
        for e in node.out_edges.values():
            if e.flow == 1:
                assignments[c_id-1].append(e.dst.name.split('_')[1])
    return assignments


def main():
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    data = read_input(input_path)
    g = build_graph(data)
    g_hat = build_graph_with_zero_lb(g)
    maximise_flow(g_hat)
    if s_hat_edges_saturated(g_hat):
        assign_flow(g_hat, g)
        maximise_flow(g)
        reviews = get_review_assignments(g, data)
    else:
        reviews = [[-1]]

    save_output(output_path, reviews)


if __name__ == '__main__':
    main()
