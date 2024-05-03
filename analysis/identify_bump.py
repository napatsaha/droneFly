
import pandas as pd
import matplotlib.pyplot as plt

files = [
    ("../data/Curved_24-04-22_14-47-46.csv", ""),
    ("../data/Curved_24-04-22_14-46-45.csv", "")
]

period = 5

datas = [
    pd.read_csv(file_path) for file_path, _ in files
]

cbf = pd.concat(datas, keys=["bumped", "non_bumped"])
cbf.groupby(level=0).std()
cbf.groupby(level=0).apply(lambda x: x.diff().abs().apply(lambda y: y.argmax())).T

for scalar in ["ag"+s for s in ("x","y","z")]:
    x = cbf.loc["bumped", scalar]
    deltax = x.diff().abs()
    changex = deltax.shift(periods=range(period)).sum(axis=1)
    plt.plot(changex.index, changex.values)
    plt.title(scalar)
    plt.show()
    print(scalar)
    print(changex.nlargest(n=period))

ag = cbf.loc["bumped", ("agx", "agy", "agz")]
dag = ag.diff().abs().sum(axis=1)
cag = dag.shift(periods=range(period)).sum(axis=1)
# print(cag.nlargest(10))
plt.plot(cag.index, cag.values)
plt.show()

print(cag.nlargest(n=period))
