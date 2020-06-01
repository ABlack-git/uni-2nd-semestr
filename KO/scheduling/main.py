#!/usr/bin/env python3
import sys
import bnb
from typing import List


class Task:
    def __init__(self, task_id, release: int, duration: int, deadline: int):
        self.task_id = task_id
        self.release = release
        self.duration = duration
        self.deadline = deadline


class InputData:
    def __init__(self):
        self.num_tasks: int = -1
        self.tasks: List[Task] = []


def read_input(path: str) -> InputData:
    data = InputData()
    with open(path, 'r') as f:
        data.num_tasks = int(f.readline())
        for i in range(data.num_tasks):
            p, r, d = (int(x) for x in f.readline().split())
            data.tasks.append(Task(i, r, p, d))
    return data


def save_output(path: str, solution):
    with open(path, 'w') as f:
        if solution is None:
            f.write(str(-1))
        else:
            for i, s in enumerate(start_time(solution)):
                f.write(str(s))
                if i + 1 < len(solution):
                    f.write('\n')


def start_time(tasks: List[Task]):
    start_times = {k: -1 for k in range(len(tasks))}
    cost = 0
    for task in tasks:
        if cost >= task.release:
            start_times[task.task_id] = cost
            cost += task.duration
        else:
            start_times[task.task_id] = task.release
            cost += task.release + task.duration
    return [start_times[i] for i in range(len(tasks))]


def main():
    input_path = sys.argv[1]
    output_path = sys.argv[2]

    data = read_input(input_path)
    solution = bnb.find_solution(data.tasks)
    save_output(output_path, solution)
    # print(bnb.log)
    # print(sum([v for v in bnb.log.values()]))


if __name__ == '__main__':
    main()
