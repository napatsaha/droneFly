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
from sklearn.cluster import KMeans

import droneFly
from droneFly import aggregate, detect_peak, collision


class DataContainer:
    time_elapsed = []
    agg_values = []
    zscores = []

    aggregator = None
    peaker = None

    def __init__(self):
        pass


def calculate_score(filename) -> DataContainer:
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

    data_container = DataContainer()

    agg_values = []
    zscores = []

    for row in subdata.itertuples():
        agg_value = aggregator(row).item()
        # print(row.Index, agg_value)
        zscore = peaker.calculate(agg_value)
        collide = peaker(agg_value)

        agg_values.append(agg_value)
        zscores.append(zscore)

    data_container.time_elapsed = data.time_elapsed
    data_container.agg_values = np.array(agg_values)
    data_container.zscores = np.array(zscores)

    data_container.aggregator = aggregator
    data_container.peaker = peaker

    return data_container


def plot_offline(file_list: list, shape: tuple, labels: Optional[list]):
    n = len(file_list)

    assert n <= np.prod(shape), "Supplied shape cannot support file list"
    if labels is not None:
        assert len(labels) == n, "Length of supplied labels does not match length of file list"

    fig, axs = plt.subplots(*shape, sharey='row', sharex=True, figsize=(12, 8))

    for i, ax in enumerate(axs.flat):
        data = calculate_score(file_list[i])
        ax.plot(data.time_elapsed, data.agg_values)
        # ax.axhline(data.peaker.threshold, linestyle='dashed', color='red')
        ax.set_ylabel("Agg Values")
        ax.set_xlabel("Time Elapsed (sec)")
        if labels is not None:
            ax.set_title(labels[i])

    for ax in axs.flat:
        ax.label_outer()

    plt.suptitle(f"{data.aggregator}\n{data.peaker}")
    plt.tight_layout()
    plt.show()


def plot_offline_grid(file_list: list, labels: Optional[list], n_clusters: Optional[int] = 2):
    n = len(file_list)
    NC = n_clusters  # Number of clusters

    if labels is not None:
        assert len(labels) == n, "Length of supplied labels does not match length of file list"

    column_headers = ["Agg_Values", "Z Scores", "Derivatives"]

    fig, axs = plt.subplots(nrows=n, ncols=3, figsize=(4.5*3, 3.5*n))

    cm = plt.get_cmap('Set1_r', lut=NC)

    for i, axs_row in enumerate(axs):
        data = calculate_score(file_list[i])
        label = labels[i] if labels is not None else None

        d1 = np.diff(data.agg_values)
        d2 = np.diff(d1)

        X = np.abs(np.c_[d1[1:], d2])

        km = KMeans(n_clusters=NC)
        km.fit(X)
        cluster = km.labels_
        largest_cluster = np.bincount(km.labels_).argmax()
        cluster_filter = cluster != largest_cluster
        print(f"Percentage of outliers = {cluster_filter.mean():.0%}\tCluster with largest group: #{largest_cluster}")

        for j, ax in enumerate(axs_row):
            if j == 0:
                ax.plot(data.time_elapsed, data.agg_values)
                ax.scatter(data.time_elapsed[2:][cluster_filter],
                           data.agg_values[2:][cluster_filter],
                           c=cm(cluster[cluster_filter]))
                ax.set_xlabel("Time Elapsed (sec)")
            elif j==1:
                ax.plot(data.time_elapsed, data.zscores)
                ax.scatter(data.time_elapsed[2:][cluster_filter],
                           data.zscores[2:][cluster_filter],
                           c=cm(cluster[cluster_filter]))
                ax.axhline(data.peaker.threshold, linestyle='dashed', color='red')
                ax.set_xlabel("Time Elapsed (sec)")
            elif j== 2:
                ax.scatter(X[:,0], X[:,1], c=cm(cluster))
                ax.set_xscale('log')
                ax.set_yscale('log')
            if i == 0:
                ax.set_title(column_headers[j])
            if j == 0:
                ax.set_ylabel(label, rotation=0, size='large')

    for ax in axs.flat:
        ax.label_outer()

    fig.suptitle(f"Grid Comparison \n {data.aggregator}\n{data.peaker}")
    fig.tight_layout()
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

    # plot_offline(files, (2, 3), labels)

    plot_offline_grid(files, labels)