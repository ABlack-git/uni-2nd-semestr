from typing import Dict, List
import numpy as np


class InputData:
    def __init__(self, num_objects, num_frames):
        self.num_objects: int = num_objects
        self.num_frames: int = num_frames
        self.frames: Dict[int, np.ndarray] = {}

    def get_distance_matrix(self, f1: int, f2: int):
        """
        Rows reference objects from f1, cols reference objects from f2
        :param f1:
        :param f2:
        :return:
        """
        distance_matrix = np.zeros((self.num_objects, self.num_objects))
        f1_objects = self.frames[f1]
        f2_objects = self.frames[f2]
        for i in range(0, self.num_objects):
            for j in range(0, self.num_objects):
                distance_matrix[i, j] = np.linalg.norm(f1_objects[i] - f2_objects[j])
        return distance_matrix


def read_input(path: str) -> InputData:
    with open(path, 'r') as f:
        num_objects, num_frames = [int(x) for x in f.readline().split()]
        input_data = InputData(num_objects, num_frames)
        for frame in range(num_frames):
            positions = [int(x) for x in f.readline().split()]
            x_pos = positions[::2]
            y_pos = positions[1::2]
            input_data.frames[frame] = np.array([x_pos, y_pos]).T
    return input_data


def save_output(data: List[List[int]], path: str):
    with open(path, 'w') as f:
        for i, line in enumerate(data):
            line_str = ' '.join([str(x) for x in line])
            f.write(line_str)
            if i + 1 != len(data):
                f.write('\n')
