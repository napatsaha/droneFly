import logging
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib
from matplotlib.animation import FuncAnimation

from analysis.aggregate import DiffAggregator, MultiDiffAggregator
from analysis.detector import ZScorePeakDetection


if __name__ == "__main__":
    animate = True

    logger = logging.getLogger("ZScorer")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())

    filename = "../data/Straight_24-04-22_14-03.csv"
    data = pd.read_csv(filename)
    metric = ["agx", "agy", "agz"]
    aggregator = MultiDiffAggregator(window=5, metrics=metric)

    detector = ZScorePeakDetection(window=20, threshold=5, influence=0.01)

    if animate:
        matplotlib.use("TkAgg")

    originals = []
    signals = []
    timesec = []
    # for row in data.itertuples():

    # fig, ax = plt.subplots(2,1,figsize=(5,10))
    # ax[0].plot([], [], '-')
    # ax[1].plot([], [], '-')

    def init():
        ax[0].set_title(metric)
        ax[1].set_title("Signal")

        ax[1].set_ylim(-0.5, 1.5)

    # def reset():
    #     originals = []
    #     signals = []
    #     timesec = []

    def update(row):
        # global  originals, signals, timesec
        # newvalue = getattr(row, metric)

        # row = data.iloc[row_id, :]

        # if row.Index == 0:
        #     reset()

        newvalue = aggregator(row)
        bump = detector(newvalue)

        originals.append(newvalue)
        signals.append(int(bump))
        timesec.append(row.time_elapsed)

        lines0.set_data(timesec, originals)
        lines1.set_data(timesec, signals)

        ax[0].set_xlim(min(timesec), max(timesec))
        ax[0].set_ylim(min(originals), max(originals))

        ax[1].set_xlim(min(timesec), max(timesec))

        return lines0, lines1

        # if bump:
        #     print(f"{row.Index} {row.time_elapsed} -- Mean: {detector.mean:.0f} -- Std: {detector.std:.2f}")


    if animate:
        fig, ax = plt.subplots(2, 1, figsize=(5, 10))
        lines0,  = ax[0].plot([], [], '-')
        lines1,  = ax[1].plot([], [], '-')
        frameiter = data.itertuples()
        anim = FuncAnimation(fig, func=update, frames=frameiter, init_func=init,
                             save_count=data.shape[0], interval=100, repeat=False)
        # anim.save("../figure/test", writer="ffmpeg")


    else:
        fig, ax = plt.subplots(2, 1, figsize=(5, 10))
        for row in data.itertuples():
            newvalue = aggregator(row)
            bump = detector(newvalue)

            originals.append(newvalue)
            signals.append(int(bump))
            timesec.append(row.time_elapsed)

        ax[0].plot(timesec, originals, '-')
        ax[1].plot(timesec, signals, '-')

        ax[0].set_title(metric)
        ax[1].set_title("Signal")

    plt.show()
