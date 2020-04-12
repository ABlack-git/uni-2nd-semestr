#!/usr/bin/env python3
import sys
import gurobipy as grb
from typing import Tuple, List


class InputData:
    def __init__(self, b_size: int, c_size: int):
        self.b_size = b_size
        self.c_size = c_size
        self.M = 0
        self.citizens_num_tasks = {key: 0 for key in range(self.c_size)}
        self.durations = {key: [] for key in range(self.c_size)}
        self.bureaucrats = {key: [] for key in range(self.b_size)}

    def add_task(self, citizen, order, bur, duration):
        self.citizens_num_tasks[citizen] += 1
        self.M += duration
        self.durations[citizen].append(duration)
        self.bureaucrats[bur].append((citizen, order))

    def get_d(self, citizen, order) -> int:
        return self.durations[citizen][order]

    def get_bur_tasks(self, b) -> List[Tuple[int, int]]:
        return self.bureaucrats[b]

    def get_citizen_num_tasks(self, citizen) -> int:
        return self.citizens_num_tasks[citizen]

    def mutually_exclusive_tasks(self):
        mutually_exclusive_tasks = []
        for b in range(self.b_size):
            for i, k in self.get_bur_tasks(b):
                for j, z in self.get_bur_tasks(b):
                    if i == j and k == z:
                        continue
                    mutually_exclusive_tasks.append((i, k, j, z))
        return mutually_exclusive_tasks

    @property
    def list_of_tasks(self):
        return [t for b in range(self.b_size) for t in self.get_bur_tasks(b)]

    def __str__(self):
        string = f'b_size: {self.b_size}\nc_size: {self.c_size}\nduration: \n'
        for i in range(self.c_size):
            string = string + f'        {i}: {self.durations[i]}\n'
        string = string + 'bureaucrats: \n'
        for b in range(self.b_size):
            string = string + f'        {b}: {self.bureaucrats[b]}\n'
        return string


def read_data(path) -> InputData:
    with open(path, 'r') as f:
        c_size, b_size = f.readline().split()
        c_size, b_size = int(c_size), int(b_size)
        data = InputData(b_size, c_size)
        for i in range(data.c_size):
            line_list = f.readline().split()
            bureaucrats = [int(b) for b in line_list[::2]]
            durations = [int(d) for d in line_list[1::2]]
            for k, b in enumerate(bureaucrats):
                data.add_task(i, k, b, durations[k])
    return data


def get_bur_policy(var, bur_tasks):
    tasks = [{'idx': (i, k), 'val': var[i, k].x} for i, k in bur_tasks]
    tasks.sort(key=lambda x: x['val'])
    return [str(x['idx'][0]) for x in tasks]


def save_solution(path, var, data: InputData, max_tf_val):
    with open(path, 'w') as f:
        f.write(str(max_tf_val))
        f.write('\n')
        for b in range(data.b_size):
            b_policy = get_bur_policy(var, data.get_bur_tasks(b))
            f.write(' '.join(b_policy))
            f.write('\n')


def main():
    input_file_path = sys.argv[1]
    output_file_path = sys.argv[2]
    data = read_data(input_file_path)
    model = grb.Model()
    mutually_exclusive_tasks = data.mutually_exclusive_tasks()
    # ADD VARIABLES
    start_t = model.addVars(data.list_of_tasks, vtype=grb.GRB.INTEGER, name='start_t')
    max_tf = model.addVar(vtype=grb.GRB.INTEGER, obj=1, name='max_tf')
    bur_busy = model.addVars(mutually_exclusive_tasks, vtype=grb.GRB.BINARY)
    # ADD CONSTRAINTS
    model.addConstrs(max_tf >= start_t[i, k] + data.get_d(i, k) for i, k in data.list_of_tasks)
    # order of tasks
    for i in range(data.c_size):
        for k in range(1, data.get_citizen_num_tasks(i)):
            model.addConstr(start_t[i, k] >= start_t[i, k - 1] + data.get_d(i, k - 1),
                            name=f'[{i},{k}] after [{i},{k - 1}]')
    # same bureaucrat can not work on several tasks at once
    for i, k, j, z in mutually_exclusive_tasks:
        model.addConstr(start_t[i, k] + data.get_d(i, k) <= start_t[j, z] + data.M * bur_busy[i, k, j, z])
        model.addConstr(start_t[j, z] + data.get_d(j, z) <= start_t[i, k] + data.M * (1 - bur_busy[i, k, j, z]))
    model.optimize()

    save_solution(output_file_path, start_t, data, int(max_tf.x))


main()
