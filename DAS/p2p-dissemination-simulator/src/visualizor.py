import matplotlib.pyplot as plt
import numpy as np
import os

class Visualizor:
    """This class helps the visualization of the results"""

    def __init__(self, execID, config, results):
        """Initialize the visualizer module"""
        self.execID = execID
        self.config = config
        self.results = results
        os.makedirs("results/"+self.execID+"/plots", exist_ok=True)
    
    def plotAll(self):
        for result in self.results:
            plotPath = "results/"+self.execID+"/plots/"+str(result.shape)
            os.makedirs(plotPath, exist_ok=True)
            
            self.plotProgress(result, plotPath)
            self.plotRowCol(result, plotPath)
            self.plotSelectedRowChannelProgress(result, plotPath)

    def plotProgress(self, result, plotPath):
        """Plots the percentage of nodes ready in the network"""
        vector1 = [x * 100 for x in result.metrics["progress"]["nodes ready"]]
        vector3 = [x * 100 for x in result.metrics["progress"]["samples received"]]
        
        title = "Nodes ready"
        legLoc = 2
        colors = ["g-", "b-"]
        labels = ["Nodes", "Samples"]
        xlabel = "Time (ms)"
        ylabel = "Percentage (%)"
        data = [vector1, vector3]
        xdots = [x * self.config.stepDuration for x in range(len(vector3))]
        path = plotPath + "/nodesReady.png"
        yaxismax = 100

        plt.figure()
        for i, d in enumerate(data):
            plt.plot(xdots, d, colors[i], label=labels[i])
        
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.ylim(0, yaxismax)
        plt.legend(loc=legLoc)
        plt.grid(True)
        plt.savefig(path)
        plt.close()


    def plotRowCol(self, result, plotPath):
        """Plots the percentage of nodes ready in the network"""
        vector1 = result.metrics["rowDist"]
        vector2 = result.metrics["columnDist"]
        
        if len(vector1) > len(vector2):
            vector2 += [np.nan] * (len(vector1) - len(vector2))
        elif len(vector1) < len(vector2):
            vector1 += [np.nan] * (len(vector2) - len(vector1))
        
        title = "Row Column distribution"
        legLoc = 2
        colors = ["r+", "b+"]
        labels = ["Rows", "Columns"]
        xlabel = "Row/Column ID"
        ylabel = "Nodes subscribed"
        data = [vector1, vector2]
        xdots = range(len(vector1))
        path = plotPath + "/RowColDist.png"
        
        yaxismax = max(np.nanmax(vector1), np.nanmax(vector2))
        
        plt.figure()
        for i, d in enumerate(data):
            plt.plot(xdots, d, colors[i], label=labels[i])
        
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.ylim(0, yaxismax)
        plt.legend(loc=legLoc)
        plt.grid(True)
        
        plt.savefig(path)
        plt.close()

    def plotSelectedRowChannelProgress(self, result, plotPath):
        vector1 = [x * 100 for x in result.metrics["progress"]["selected row nodes ready"]]
        vector3 = [x * 100 for x in result.metrics["progress"]["selected row samples received"]]
        
        title = "Nodes ready for a selected row channel"
        legLoc = 2
        colors = ["g-", "b-"]
        labels = ["Nodes", "Samples"]
        xlabel = "Time (ms)"
        ylabel = "Percentage (%)"
        data = [vector1, vector3]
        xdots = [x * self.config.stepDuration for x in range(len(vector3))]
        path = plotPath + "/nodesReadyForSelectedRow.png"
        yaxismax = 100

        plt.figure()
        for i, d in enumerate(data):
            plt.plot(xdots, d, colors[i], label=labels[i])
        
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.ylim(0, yaxismax)
        plt.legend(loc=legLoc)
        plt.grid(True)
        plt.savefig(path)
        plt.close()
