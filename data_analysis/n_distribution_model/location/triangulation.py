from helper import *
from caen_digitizer import *
import gaussian_estimation as ge
 
# data
import numpy as np


import random

def getMaxMask(data):

    ch_event = getMask(0, data)

    for _channel_trigger in range(1,10):

        masked = getMask(_channel_trigger, data)


        if masked[0].shape[0] > ch_event[0].shape[0]:
            ch_event = masked
    

    return ch_event[0]

def getMask(_channel_trigger, data):
    signal_max = data.waveforms['amplitude'][:, _channel_trigger]
    signal_min = data.waveforms['wave'][:, _channel_trigger].min(axis=1)
    mask_event = (signal_min > -15) & (signal_max > 10)

    return np.where(mask_event)


fileDir = "/Users/andyyu/Documents/Python/HEP/dawson_hep/scintillating_chamber/data_analysis/n_distribution_model/location/data"

dfs = []
f = list(range(0,18))
f.remove(3)

# k = [random.choice(f) for i in range(3)]

k = [1, 6,3]
for runNo in k:
    data = digitizer(f'{fileDir}/run{runNo:06}.root', events=None, channels=[i for i in range(17, 27) ], signal_filter='converted')

    dfs.append(data)

rates = []
for file in dfs:
    selected_events = len(getMaxMask(file))
    r = selected_events / len(file.waveforms['wave'])
    print(selected_events,r)
    rates.append(r)

print(rates)
# locations = [(-250.1,-148.9), (-245.1, -149.0), (-240.1, -148.9)]
d = 20
y = -250.1, -225.1, -210.0
x = -149.0, -148.9, -148.9
center = ge.x_0(*x, *y, *rates, d), ge.y_0(*x, *y, *rates, d)

print(center)