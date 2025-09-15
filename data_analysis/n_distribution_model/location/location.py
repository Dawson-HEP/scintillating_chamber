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
    def findLength(self):

        time = 1000
        self.frequency = []

        for df in self.record:

            df = df[df["time"] < time] 
            
            self.frequency.append(df.shape[0])


    def findMax(self):
        #Find the maximum
        self.max = max(self.frequency)
        self.max_id = self.frequency.index(self.max)

    def output(self):
        self.readcsv()
        self.findLength()
        self.findMax()


        print(f"max = {self.max}, datapoint = {self.max_id}")
        print(f"Position: {self.dfs[self.max_id]}")
        print(self.dfs)



files = [
    ""

]

x = locator(files)

x.output()