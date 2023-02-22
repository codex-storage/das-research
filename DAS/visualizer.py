#!/bin/python3

class Visualizer:

    def __init__(self, execID):
        self.execID = execID
        self.folderPath = "results/"+self.execID

    def plottingData(self):
        data = []
        print("Getting data from the folder...")
        return data

    def similarKeys(self, data):
        filteredKeys = []
        print("Getting filtered keys from data...")
        return filteredKeys

    def plotHeatmaps(self):
        data = self.plottingData()
        filteredKeys = self.similarKeys(data)
        print("Plotting heatmaps...")
