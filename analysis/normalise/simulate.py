"""
Comparing signal detection using different normalising strategies.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def normalise1d(arr):
    mu = arr.mean()
    sigma = arr.std()
    if sigma == 0:
        return arr - mu
    else:
        return (arr - mu) / sigma

def normalise(arr):
    return np.apply_along_axis(normalise1d, axis=0, arr=arr)

def agg_func(arr):
    """
    diff -> abs -> sum
    """
    return np.sum(np.abs(np.diff(arr, axis=0)), axis=0)

def agg_func1(arr):
    """
    norm -> diff -> abs -> sum
    """
    arr = normalise(arr)
    return np.sum(np.abs(np.diff(arr, axis=0)), axis=0)

def agg_func2(arr):
    """
    diff -> norm -> abs -> sum
    """
    arr = np.diff(arr, axis=0)
    arr = normalise(arr)
    return np.sum(np.abs(arr), axis=0)

def agg_func3(arr):
    """
    diff -> abs -> norm -> sum
    """
    arr = np.abs(np.diff(arr, axis=0))
    arr = normalise(arr)
    return np.sum(arr, axis=0)

def agg_func4(arr):
    """
    global_norm -> diff -> abs -> sum
    """
    arr = (arr - MU) / SIGMA
    return np.sum(np.abs(np.diff(arr, axis=0)), axis=0)

dat = pd.read_csv(r"../../data/24-05-20_15-40-59-164986.csv")

metrics = ['agx', 'agy', 'agz']
WINDOW_SIZE = 5
N = dat.shape[0] - WINDOW_SIZE

fig, axs = plt.subplots(3, 2, figsize=(10,10))
axs = axs.flatten()

MU = dat.loc[:, metrics].mean(axis=0).values
SIGMA = dat.loc[:, metrics].std(axis=0).values

for ax_i, agg in enumerate([agg_func, agg_func1, agg_func2, agg_func3, agg_func4]):
    ax = axs[ax_i]

    res = np.empty((N, ))
    idxs = []

    for idx in range(N):
        sample = dat.iloc[idx:(idx+WINDOW_SIZE)].loc[:, metrics].values
        sample = agg(sample)
        # sample = sample / sum(sample)
        res[idx] = sample.sum()

    # res = pd.DataFrame(res, columns=metrics)
    # sns.kdeplot(res, ax=ax)
    ax.plot(dat.time_elapsed[:N], res)
    # ax.set_xlim(0,1)
    # ax.set_xlabel("Proportion in weights")
    ax.set_title(agg.__doc__.strip())

plt.show()