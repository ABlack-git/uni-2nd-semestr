from typing import Dict


class Bounded:
    def __init__(self, lb=None, ub=None):
        self.lb = lb
        self.ub = ub


class Customer(Bounded):
    def __init__(self):
        super().__init__()
        self.products = []


class InputData:
    def __init__(self, c_size, p_size):
        self.c_size = c_size
        self.p_size = p_size
        self.customers: Dict[int, Customer] = {k: Customer() for k in range(1, self.c_size + 1)}
        self.products: Dict[int, Bounded] = {k: Bounded(0, 0) for k in range(p_size)}
