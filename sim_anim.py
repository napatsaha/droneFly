import time, random, threading
from collections import deque

import numpy as np
import pandas as pd
# import matplotlib.pyplot as plt
import matplotlib
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
from matplotlib import animation

matplotlib.use("TkAgg")


class DataTracker:
    """
    Tracks plottable data gleaned from state queries during collision handling.
    """
    def __init__(self, metrics, max_size=100):
        self.metrics = metrics
        self.y_data = {}
        self.x_data = deque(maxlen=max_size)
        for met in metrics:
            self.y_data[met] = deque(maxlen=max_size)

    def add_data(self, dic: dict):
        for met in self.metrics:
            value = dic.get(met)
            self.y_data[met].append(value)
        self.x_data.append(time.time() - t0)

    def get_data(self):
        x = list(self.x_data)
        y = [self.y_data[met] for met in self.metrics]
        return x, y


def simulate_data():
    global finished
    data = pd.read_csv(FILE_SIM)

    loader = data.iterrows()

    while True:
        try:
            idx, row = next(loader)
            data_tracker.add_data(row.to_dict())

            time.sleep(1/FPS)
        except StopIteration:
            finished = True
            break

        # if idx > data.shape[0]:
        #     break



# def init_plot():
#     ax.set_ylim(-1, 1)
#     ax.set_xlim(0, 50)
    #
    # return l,



# def plot_data():
#     """
#     Thread
#     :return:
#     :rtype:
#     """



if __name__ == "__main__":
    FPS = 2
    N = 80
    FILE_SIM = "data/Curved_24-04-22_14-47-46.csv"
    # fig = plt.figure()
    t0 = time.time()

    metrics = ["agx", "agy", "agz"]

    data_tracker = DataTracker(metrics, max_size=N)
    finished = False

    simulator = threading.Thread(target=simulate_data, name="simulator")
    # plotter = threading.Thread(target=plot_data, name="plotter")

    # plotter.start()

    fig, axs = plt.subplots(1, len(metrics), figsize=(15,7))
    lines = [axis.plot([], [], 'o-')[0] for axis in axs]

    def frames():
        while not finished:
            time.sleep(1 / FPS)

            yield data_tracker.get_data()

    def update_plot(args):
        # global l
        # print(args)
        xt, yts = args
        for line, yt, ax in zip(lines, yts, axs):
            line.set_data(xt, yt)
            if len(xt) > 1:
                ax.set_xlim(min(xt), max(xt))
            if len(yt) > 1:
                ax.set_ylim(min(yt), max(yt))
            # line, = ax.plot(xt, yt)
        return lines

    simulator.start()

    anim = animation.FuncAnimation(fig, update_plot, frames=frames, cache_frame_data=False, interval=100, repeat=False)
    plt.show()
