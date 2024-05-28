"""
For offline analysis and plotting of collected data using custom Collision Detection Algorithms
(Aggregator + Peaker combination)

[Work in Progress]
"""

import os
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd
import os

import droneFly
from droneFly import aggregate, detect_peak, collision


def calculate_score(filename, return_detectors=True):
    metric = ["agx", "agy", "agz"]
    agg_kwargs = dict(window=10)
    pk_kwargs = dict(window=20, threshold=15, influence=0.1)
    # data_file = "2024-05-24\\24-05-24_16-36-30-503328.csv"
    file_date = "20"+filename.split("_")[0]

    data = pd.read_csv(os.path.join(droneFly.DATA_DIR, file_date, filename))
    subdata = data.loc[:, metric]

    # aggregator = aggregate.MultiDiffAggregator(metrics=metric, **agg_kwargs)
    aggregator = aggregate.NormAggregator(metrics=metric, **agg_kwargs)

    peaker = detect_peak.ZScorePeakDetection(**pk_kwargs)

    agg_values = []
    zscores = []

    for row in subdata.itertuples():
        agg_value = aggregator(row).item()
        # print(row.Index, agg_value)
        zscore = peaker.calculate(agg_value)
        collide = peaker(agg_value)

        agg_values.append(agg_value)
        zscores.append(zscore)

    if return_detectors:
        return (data.time_elapsed, zscores), (aggregator, peaker)
    else:
        return data.time_elapsed, zscores


def plot_offline(file_list: list, shape: tuple, labels: Optional[list]):
    n = len(file_list)

    assert n <= np.prod(shape), "Supplied shape cannot support file list"
    if labels is not None:
        assert len(labels) == n, "Length of supplied labels does not match length of file list"

    fig, axs = plt.subplots(*shape, sharey='row', sharex=True, figsize=(12, 8))

    for i, ax in enumerate(axs.flat):
        (x, y), (agg, pkk) = calculate_score(file_list[i], return_detectors=True)
        ax.plot(x, y)
        ax.axhline(pkk.threshold, linestyle='dashed', color='red')
        ax.set_ylabel("ZScore")
        ax.set_xlabel("Time Elapsed (sec)")
        if labels is not None:
            ax.set_title(labels[i])

    for ax in axs.flat:
        ax.label_outer()

    plt.suptitle(f"{agg}\n{pkk}")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    files = [
        "24-05-24_16-36-30-503328.csv",
        "24-05-24_16-37-19-450541.csv",
        "24-05-24_16-38-28-935844.csv",
        "24-05-24_16-40-16-242862.csv",
        "24-05-24_16-41-02-542899.csv",
        "24-05-24_16-44-43-301562.csv"
    ]

    labels = [f'Gust{i}' for i in range(1,4)] + [f'Bump{i}' for i in range(1,4)]

    plot_offline(files, (2, 3), labels)
