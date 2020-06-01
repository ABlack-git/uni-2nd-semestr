from typing import List, Set, Union
from collections import deque

from main import Task


class Node:
    def __init__(self, unscheduled: Set[Task], schedule: List[Task]):
        self.unscheduled: Set[Task] = unscheduled
        self.schedule: List[Task] = schedule
        self.cost: int = compute_cost(self.schedule)
        self.u_min_r = 0 if len(self.unscheduled) == 0 else min_release(self.unscheduled)

    def get_children(self):
        children = []
        for task in self.unscheduled:
            s = self.schedule + [task]
            u = self.unscheduled.copy()
            u.remove(task)
            children.append(Node(schedule=s, unscheduled=u))
        return children

    def __str__(self):
        return ' '.join([str(task.task_id) for task in self.schedule])


def compute_cost(tasks: List[Task]):
    cost = 0
    if len(tasks) > 0:
        for task in tasks:
            if cost >= task.release:
                cost += task.duration
            else:
                cost += task.release + task.duration
    return cost


def max_deadline(tasks: List[Task]):
    return max([task.deadline for task in tasks])


def min_release(tasks: List[Task]):
    return min([task.release for task in tasks])


def check_missed_deadline(node: Node) -> bool:
    for task in node.unscheduled:
        if max(node.cost, task.release) + task.duration > task.deadline:
            return True
    return False


def check_upper_bound(node: Node, upper_bound) -> bool:
    lb = max(node.cost, node.u_min_r) + sum([task.duration for task in node.unscheduled])
    if lb >= upper_bound:
        return True
    else:
        return False


def check_decomposition(node: Node) -> bool:
    if node.cost > 0:
        return node.cost <= node.u_min_r
    else:
        return False


def find_solution(tasks: Union[List[Task], Set[Task]]):
    solution: Union[None, List[Task]] = None
    ub = max([task.deadline for task in tasks]) + 1
    stack = deque()
    children = Node(set(tasks), []).get_children()
    for child in children:
        stack.append(child)

    while len(stack) != 0:
        node: Node = stack.pop()
        # check node for condition, skip if violated
        if check_missed_deadline(node):
            continue
        if check_upper_bound(node, ub):
            continue
        if check_decomposition(node):
            sol = find_solution(node.unscheduled)
            solution = node.schedule.copy() + sol
            break

        children = node.get_children()
        if len(children) == 0:
            # feasible solution
            solution = node.schedule
            ub = node.cost
        else:
            # add all children on stack
            for child in children:
                stack.append(child)
    return solution
