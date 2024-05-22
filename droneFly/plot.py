"""
For plotting signals post data collection.

Useful for comparing different collision detectors, aggregators, peak detectors setup.
"""

import os

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd
import os

print()
import droneFly
from droneFly import aggregate, detect_peak, collision

metric = ["agx", "agy", "agz"]
agg_kwargs = dict(window=5)
pk_kwargs = dict(window=20, threshold=5, influence=0.1)
data_file = "Gust_24-05-08_16-12-16.csv"

data = pd.read_csv(os.path.join(droneFly.DATA_DIR, data_file))
subdata = data.loc[:, metric]

# aggregator = aggregate.MultiDiffAggregator(metrics=metric, **agg_kwargs)
aggregator = aggregate.NormAggregator(metrics=metric, **agg_kwargs)

peaker = detect_peak.ZScorePeakDetection(**pk_kwargs)

agg_values = []
collides = []

for row in subdata.itertuples():
    agg_value = aggregator(row)
    print(row.Index, agg_value)
    collide = peaker(agg_value)

    agg_values.append(agg_value)
    collides.append(collide)

sns.lineplot(x=data.time_elapsed, y=np.array(agg_values).flatten())
plt.show()
