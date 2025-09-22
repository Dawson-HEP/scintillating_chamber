import numpy as np
import matplotlib.pyplot as plt
import polars as pl

#Create Dataframes
csv_x = [
    "sample_data.csv"
]

dfs_x = []
for i in csv_x:
    dfs_x.append(pl.read_csv(i))

csv_y = [
    "sample_data.csv"
]

dfs = []
for i in csv_y:
    dfs.append(pl.read_csv(i))

#Filter
rates_x = []
for df in dfs_x:
    hits = (df["trigger_data"] == 0).sum()

    rate_of_0 = hits / df.shape[0]

    rate = 1 - rate_of_0

    rates_x.append(rate)

rates_y = []
for df in dfs_x:
    hits = (df["trigger_data"] == 0).sum()

    rate_of_0 = hits / df.shape[0]

    rate = 1 - rate_of_0

    rates_y.append(rate)


#Create distribution
R2D = np.outer(rates_y, rates_x)

x = len(rates_x)
y = len(rates_y)
X, Y = np.meshgrid(x,y)

fig = plt.figure()
ax = fig.add_subplot(111, projection = "3d")

ax.plot_surface(X, Y, R2D, cmap = "terrain")
ax.set_xlabel("X position")
ax.set_ylabel("Y position")
ax.set_zlabel("Hit Rate")

plt.show()





