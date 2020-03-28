import numpy as np


class Sliceable:
    def __getitem__(self, item):
        print(item, type(item))
        if isinstance(item, slice):
            tmp = np.zeros(4)
            return tmp[item]


sliceme = Sliceable()
print(sliceme[:])
sliceme["3", :]
