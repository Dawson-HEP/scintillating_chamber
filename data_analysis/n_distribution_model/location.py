import numpy as np
import pandas as pd

#Truncate Data
def clean(df):
    time = 1000  #ms
    df = df[df["time"] < time]


#Insert file name here
dfs = [
    "",
    "",
    ""

]

#Read Every CSV
record = []
for i in dfs:
    record.append(pd.read_csv(i))


#Clean Data and find Length of csv
frequency = []
for df in record:
    clean(df)
    frequency.append(df.shape[0])


#Find the maximum
max = frequency.max()
max_id = frequency.index(max)

print(f"max = {max}, datapoint = {max_id}")
print(f"Position: {dfs[max_id]}")

