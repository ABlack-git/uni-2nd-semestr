#!/usr/bin/env python3
import sys
from typing import List
from inoutdata import InputData, read_input, save_output
from mincostflow import build_mincost_graph, minimize_cost, get_obj_mapping


def main():
    in_path = sys.argv[1]
    out_path = sys.argv[2]
    input_data: InputData = read_input(in_path)
    out_data: List[List[int]] = []
    for frame in range(0, input_data.num_frames - 1):
        g = build_mincost_graph(input_data, frame, frame + 1)
        minimize_cost(g)
        out_data.append(get_obj_mapping(g))
    save_output(out_data, out_path)


if __name__ == '__main__':
    main()
