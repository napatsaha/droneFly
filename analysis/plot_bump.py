import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

save = False

# Tuples of file paths and labels (if known)
files = [
    ("../data/2024-05-08/Gust_24-05-08_16-17-42.csv", ""),
    ("../data/2024-05-08/Gust_24-05-08_16-17-11.csv", ""),
    # ("../data/24-05-20_15-29-21-282172.csv", ""),
    # ("../data/24-05-20_15-39-07-387409.csv", "")
]
# f_bump = "data/Curved_24-04-22_14-47-46.csv"
# f_cont = "data/Curved_24-04-22_14-46-45.csv"


datas = [
    pd.read_csv(file_path) for file_path, _ in files
]
# bumped = pd.read_csv(f_bump)
# non_bumped = pd.read_csv(f_cont)

exp_type = files[0][0].split("/")[-1].split("_")[0]
labels = [
    label if len(label) > 0 else file.split("/")[-1].split("_")[-1]
    for file, label in files
]
# exp_type = f_bump.split("/")[-1].split("_")[0]
# id_bump = f_bump.split("/")[-1].split("_")[-1]
# id_cont = f_cont.split("/")[-1].split("_")[-1]

metrics = np.array([
    ["pitch", "roll", "yaw"],
    ["vgx", "vgy", "vgz"],
    ["agx", "agy", "agz"]
])

fig, ax = plt.subplots(3, 3, figsize=(15, 15))

for i in range(3):
    for j in range(3):
        metric = metrics[i, j]
        for dataframe, label in zip(datas, labels):
            ax[i, j].plot(dataframe.time_elapsed, dataframe[metric],
                          label=label)
            # ax[i,j].plot(bumped.time_elapsed, bumped[metric],
            #              label="bumped")
            # ax[i,j].plot(non_bumped.time_elapsed, non_bumped[metric],
            #              label="not_bumped")
        ax[i, j].set_title(metric)

fig.legend(*ax[0, 0].get_legend_handles_labels(), loc="upper center")
plt.suptitle(exp_type)
if save:
    suffix = "-".join(labels)
    plt.savefig(os.path.join("../figure", f"{exp_type}_{suffix}.png"))
plt.show()
