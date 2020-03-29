import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import os
from typing import List

matplotlib.use('Agg')


def evaluate_stats(stats: dict, name, n, path='plots'):
    if not os.path.exists(path):
        os.makedirs(path)
    for key, val in stats.items():
        plt.plot(simple_moving_average(val, n), label=key)
    plt.legend(loc='upper left')
    plt.savefig(os.path.join(path, f'stats_moving_average_{name}.pdf'))
    plt.close()


def evaluate(rewards: List[float], name='', simp_factor=100, exp_factor=0.7, plot=True):
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
    if plot:
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
def plot_series(arr, avg_type, name, path='plots'):
    if not os.path.exists(path):
        os.makedirs(path)
    plt.plot(arr)
    plt.savefig(os.path.join(path, f'{avg_type}_moving_average_{name}.pdf'))
    plt.close()
