#!/usr/bin/env python3
import sys
import gurobipy as grb
from typing import List


class InputData:
    def __init__(self):
        self.num_prod_type: int = -1
        self.num_machines: int = -1
        self.total_cost: int = -1
        self.cost_24: int = -1
        self.total_num_prods_on_machine: List[int] = []
        self.num_of_produced_prods: List[int] = []
        self.costs: List[List[int]] = []
        self.prod_times: List[List[int]] = []


def read_input(path) -> InputData:
    with open(path, 'r') as f:
        data = InputData()
        data.num_prod_type = 13
        data.num_machines = 4
        data.total_cost = int(f.readline())
        data.cost_24 = int(f.readline())
        data.total_num_prods_on_machine = [int(x) for x in f.readline().split()]
        data.num_of_produced_prods = [int(x) for x in f.readline().split()]
        for i in range(data.num_machines):
            c_ij = [int(x) for x in f.readline().split()]
            data.costs.append(c_ij)
        for i in range(data.num_machines):
            p_ij = [int(x) for x in f.readline().split()]
            data.prod_times.append(p_ij)
    return data


def save_output(path, obj, produced):
    with open(path, 'w') as f:
        if len(produced) == 1:
            f.write('-1')
        else:
            f.write(str(obj))
            f.write('\n')
            for l, produced_on_machine in enumerate(produced):
                f.write(' '.join([str(x) for x in produced_on_machine]))
                if l != len(produced):
                    f.write('\n')


def get_output(x, data: InputData):
    num_produced = []
    for i in range(data.num_machines):
        tmp = []
        for j in range(data.num_prod_type):
            tmp.append(round(x[i, j].x))
        num_produced.append(tmp)
    return num_produced


def main():
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    data = read_input(input_path)
    model: grb.Model = grb.Model()
    x: grb.tupledict = model.addVars(data.num_machines, data.num_prod_type, vtype=grb.GRB.INTEGER, name='x')
    z = model.addVar(name='obj', vtype=grb.GRB.INTEGER)
    k = model.addVars(data.num_prod_type, lb=0, name='aux_var', vtype=grb.GRB.INTEGER)

    model.addConstr(grb.quicksum(x[0, j] * data.prod_times[0][j] - x[3, j] * data.prod_times[3][j]
                                 for j in range(data.num_prod_type)) <= z, name='obj_constr_1')
    model.addConstr(grb.quicksum(x[3, j] * data.prod_times[3][j] - x[0, j] * data.prod_times[0][j]
                                 for j in range(data.num_prod_type)) <= z, name='obj_constr_1')

    model.addConstr(z >= 0)
    for j in range(data.num_prod_type):
        model.addConstr(grb.quicksum(x[i, j] for i in range(data.num_machines)) >= data.num_of_produced_prods[j],
                        name=f'produced_prod_{j}')

    for i in range(data.num_machines):
        model.addConstr(grb.quicksum(x[i, j] for j in range(data.num_prod_type)) <= data.total_num_prods_on_machine[i],
                        name=f'on_machine_{i}')

    model.addConstr(grb.quicksum(data.costs[i][j] * x[i, j] for i in range(data.num_machines)
                                 for j in range(data.num_prod_type)) <= data.total_cost, name='total_cost')

    model.addConstr(grb.quicksum(x[1, j] * data.costs[1][j] + x[3, j] * data.costs[3][j]
                                  for j in range(data.num_prod_type)) <= data.cost_24, name='cost_24')

    model.addConstrs((x[3, j] == 6 * k[j] for j in range(data.num_prod_type)), name='batch')

    model.setObjective(z, grb.GRB.MINIMIZE)
    model.optimize()
    model.display()
    if model.Status == 3:
        produced = [-1]
        save_output(output_path, -1, produced)
    else:
        print(z.x)
        produced = get_output(x, data)
        save_output(output_path, int(z.x), produced)
    print(produced)


if __name__ == '__main__':
    main()
