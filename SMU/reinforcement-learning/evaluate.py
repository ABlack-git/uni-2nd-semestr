import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from typing import List

import numpy as np


def evaluate(rewards: List[float], name, simp_factor=1000, exp_factor=0.7):
    # TODO implement your own code here if you want to
    # or alternatively you can modify the existing code
    # if you reuse the averaging, you should probably change the parameters

    np.set_printoptions(precision=5)
    rewards_arr = np.array(rewards)
    print(f"Wins: {np.sum(rewards_arr == 1)}, Loses: {np.sum(rewards_arr == -1)}, Ties: {np.sum(rewards_arr == 0)}")
    print("Average")
    print(np.sum(rewards) / len(rewards))

    # to use this plot function you have to install matplotlib
    # use conda install matplotlib
    plot_series(simple_moving_average(rewards, simp_factor), 'simple', name)
    plot_series(exponential_moving_average(rewards, exp_factor), 'exp', name)


# check Wikipedia: https://en.wikipedia.org/wiki/Moving_average
def simple_moving_average(x: List[float], n: int) -> float:
    mean = np.zeros(len(x) - n + 1)
    tmp_sum = np.sum(x[0:n])
    for i in range(len(mean) - 1):
        mean[i] = tmp_sum
        tmp_sum -= x[i]
        tmp_sum += x[i + n]
    mean[len(mean) - 1] = tmp_sum
    return mean / n


# check Wikipedia: https://en.wikipedia.org/wiki/Moving_average
def exponential_moving_average(x: List[float], alpha: float) -> float:
    mean = np.zeros(len(x))
    mean[0] = x[0]
    for i in range(1, len(x)):
        mean[i] = alpha * x[i] + (1.0 - alpha) * mean[i - 1]
    return mean


# you can use this function to get a plot
# you need first to install matplotlib (conda install matplotlib)
# and then uncomment this function and lines 1-3
def plot_series(arr, avg_type, name):
    plt.plot(arr)
    plt.savefig(f'{avg_type}_moving_average_{name}.pdf')
    plt.close()