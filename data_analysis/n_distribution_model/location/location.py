import numpy as np
import pandas as pd

class locator:
    def __init__(self, files):
        self.dfs = files
    
     #Read Every CSV
    def readcsv(self):
        self.record = []
        for i in self.dfs:
            self.record.append(pd.read_csv(i))

    

    #Clean Data and find Length of csv
    # def findLength(self):

    #     time = 1000
    #     self.frequency = []

    #     for df in self.record:

    #         df = df[df["time"] <= time] 

    #         self.frequency.append(df.shape[0])


    # def findMaxFrequency(self):
    #     #Find the maximum
    #     self.max = max(self.frequency)
    #     self.max_id = self.frequency.index(self.max)

    # def printMax(self):
    #     self.readcsv()
    #     self.findLength()
    #     self.findMax()


    #     print(f"max = {self.max}, datapoint = {self.max_id}")
    #     print(f"Position: {self.dfs[self.max_id]}")
    #     print(self.dfs)


    def findMaxRate(self):
        self.max_rate = max(self.rates)
        self.max_rate_id = self.rates.index(self.max_rate)

    def getRate(self):
        self.readcsv()


        self.rates = []

        for df in self.record:
            hits = df["trigger_data"].sum()

            rate = hits / df.shape[0]

            self.rates.append(rate)
        
        
        self.findMaxRate()
        
        print(f"max rate: {self.max_rate}, datapoint = {self.max_rate_id}")
        print(f"Position: {self.dfs[self.max_rate_id]}")
        print(self.dfs)



files = [


]

x = locator(files)

x.getRate()