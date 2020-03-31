#!/usr/bin/env python3
import sys
import gurobipy as g
from gurobipy import tupledict


def read_input():
    assert len(sys.argv) == 3
    input_file_path = sys.argv[1]
    output_file_path = sys.argv[2]
    return input_file_path, output_file_path


def read_file_to_list(path) -> list:
    with open(path, 'r') as f:
        line = f.readline()
        dems = line.split(' ')
    return [float(d) for d in dems]


def write_to_file(opt_obj_val: int, opt_vals: list, path: str):
    with open(path, 'w') as f:
        f.write(str(opt_obj_val))
        f.write('\n')
        f.write(' '.join(opt_vals))


if __name__ == '__main__':
    inp_f, out_f = read_input()
    demands = read_file_to_list(inp_f)
    model = g.Model()
    num_hours = len(demands)
    x: tupledict = model.addVars(num_hours, name='x', vtype=g.GRB.INTEGER)
    z: tupledict = model.addVars(num_hours, name='z', vtype=g.GRB.INTEGER)

    for i in range(num_hours):
        shifts_sum_i = g.quicksum([x[j % num_hours] for j in range(i - 7, i + 1)])
        model.addConstr(z[i] >= demands[i] - shifts_sum_i)
        model.addConstr(z[i] >= shifts_sum_i - demands[i])
    model.setObjective(z.sum(), g.GRB.MINIMIZE)
    model.optimize()
    print([int(x_i.getAttr('x')) for i, x_i in x.items()])
    print(sum([z_i.getAttr('x') for _, z_i in z.items()]))
    shifts = [str(int(x_i.getAttr('x'))) for i, x_i in x.items()]
    obj_val = int(sum([z_i.getAttr('x') for _, z_i in z.items()]))
    write_to_file(obj_val, shifts, out_f)
