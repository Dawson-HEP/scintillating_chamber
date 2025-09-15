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

    #Truncate Data
    def clean(self,df):
        time = 1000  #ms
        df = df[df["time"] < time]   
    


    #Clean Data and find Length of csv
    def findLength(self):

        self.frequency = []
        for df in self.record:
            self.clean(df)
            self.frequency.append(df.shape[0])


    def findMax(self):
        #Find the maximum
        self.max = self.frequency.max()
        self.max_id = self.frequency.index(self.max)

    def output(self):
        self.readcsv()
        self.findLength()
        self.findMax()


        print(f"max = {max}, datapoint = {self.max_id}")
        print(f"Position: {self.dfs[self.max_id]}")
        print(self.dfs)



files = [
    ""

]

x = locator(files)

x.output()