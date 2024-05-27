"""
For offline analysis and plotting of collected data using custom Collision Detection Algorithms
(Aggregator + Peaker combination)

[Work in Progress]
"""

import os

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd
import os

import droneFly
from droneFly import aggregate, detect_peak, collision

metric = ["agx", "agy", "agz"]
agg_kwargs = dict(window=5)
pk_kwargs = dict(window=20, threshold=50, influence=0.1)
data_file = "2024-05-24\\24-05-24_16-36-30-503328.csv"

data = pd.read_csv(os.path.join(droneFly.DATA_DIR, data_file))
subdata = data.loc[:, metric]

# aggregator = aggregate.MultiDiffAggregator(metrics=metric, **agg_kwargs)
aggregator = aggregate.NormAggregator(metrics=metric, **agg_kwargs)

peaker = detect_peak.ZScorePeakDetection(**pk_kwargs)

agg_values = []
zscores = []

for row in subdata.itertuples():
    agg_value = aggregator(row).item()
    print(row.Index, agg_value)
    zscore = peaker.calculate(agg_value)
    collide = peaker(agg_value)

    agg_values.append(agg_value)
    zscores.append(zscore)

plt.plot(data.time_elapsed, zscores)
plt.show()
