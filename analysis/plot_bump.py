import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

save = True

# Tuples of file paths and labels (if known)
files = [
    # ("../data/2024-05-24/24-05-24_13-31-42-850137.csv", "Gust (x3)"),
    # ("../data/2024-05-24/24-05-24_13-34-28-017670.csv", "Control"),
    # ("../data/2024-05-24/24-05-24_16-36-30-503328.csv", "Gust1"),
    # ("../data/2024-05-24/24-05-24_16-37-19-450541.csv", 'Gust2'),
    # ("../data/2024-05-24/24-05-24_16-38-28-935844.csv", 'Gust3'),
    # ("../data/2024-05-24/24-05-24_16-40-16-242862.csv", "Bump1"),
    # ("../data/2024-05-24/24-05-24_16-41-02-542899.csv", 'Bump2'),
    ("../data/2024-05-24/24-05-24_16-44-43-301562.csv", 'Bump3')
    # ("../data/2024-05-08/Gust_24-05-08_16-17-42.csv", ""),
    # ("../data/2024-05-08/Gust_24-05-08_16-17-11.csv", ""),
    # (r"C:\Users\napat\Python\droneFly\data\2024-04-22\Curved_24-04-22_14-46-45.csv", ""),
    # (r"C:\Users\napat\Python\droneFly\data\2024-04-22\Curved_24-04-22_14-47-46.csv", "")
]
# f_bump = "data/Curved_24-04-22_14-47-46.csv"
# f_cont = "data/Curved_24-04-22_14-46-45.csv"


datas = [
    pd.read_csv(file_path) for file_path, _ in files
]
# bumped = pd.read_csv(f_bump)
# non_bumped = pd.read_csv(f_cont)

date_info = os.path.split(os.path.split(files[0][0])[0])[-1]
experiment_info = ' vs '.join([label for file, label in files])
file_info = ' | '.join([':'.join(os.path.split(file)[1].split('_')[1].split('-')[:3]) for file, label in files])
title = experiment_info + "\n" + date_info + '\n' + file_info
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
    ["agx", "agy", "agz"],
    ['h','tof','baro']
])

nrow = metrics.shape[0]
ncol = metrics.shape[1]

fig, ax = plt.subplots(nrow, ncol, figsize=(15, 15))

for i in range(nrow):
    for j in range(ncol):
        metric = metrics[i, j]
        for dataframe, label in zip(datas, labels):
            ax[i, j].plot(dataframe.time_elapsed, dataframe[metric],
                          label=label)
            # ax[i,j].plot(bumped.time_elapsed, bumped[metric],
            #              label="bumped")
            # ax[i,j].plot(non_bumped.time_elapsed, non_bumped[metric],
            #              label="not_bumped")
        ax[i, j].set_title(metric)

fig.legend(*ax[0, 0].get_legend_handles_labels(), loc="upper left")
plt.suptitle(title)
if save:
    identifier = '-'.join([file.split('-')[-1].strip('.csv') for file, label in files])
    plt.savefig(os.path.join("../figure", f"{date_info}_{experiment_info}_{identifier}.png"))
plt.show()
