#!/bin/python3

import matplotlib.pyplot as plt
import numpy as np
import os

def plotData(conf):
    plt.clf()
    fig = plt.figure("9, 3")
    if conf["desLoc"] == 1:
        xDes = 0
    else:
        xDes = conf["xdots"][-1] * 0.6
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    plt.text(xDes, conf["yaxismax"]/4, conf["textBox"], fontsize=10, verticalalignment='top', bbox=props)
    for i in range(len(conf["data"])):
        if conf["type"] == "plot":
            plt.plot(conf["xdots"], conf["data"][i], conf["colors"][i], label=conf["labels"][i])
        if conf["type"] == "bar":
            plt.bar(conf["xdots"], conf["data"][i], label=conf["labels"][i])
    plt.title(conf["title"])
    plt.ylabel(conf["ylabel"])
    plt.xlabel(conf["xlabel"])
    plt.ylim(0, conf["yaxismax"]*1.1)
    plt.legend(loc=conf["legLoc"])
    plt.savefig(conf["path"], bbox_inches="tight")


class Visualizor:
    """This class helps the visualization of the results"""

    def __init__(self, execID, config, results):
        """Initialize the visualizer module"""
        self.execID = execID
        self.config = config
        self.results = results
        os.makedirs("results/"+self.execID+"/plots", exist_ok=True)
    
    def __get_attrbs__(self, result):
        text = str(result.shape).split("-")
        d = dict()
        for i in range(0, len(text), 2):
            d[text[i]] = text[i + 1]
        return d

    def plotHeatmaps(self, x, y):
        """Plot the heatmap using the parameters given as x axis and y axis"""
        print("Plotting heatmap "+x+" vs "+y)
        #Find the location of x in shape
        #Find the location of y in shape
        #Find the location od r in shape

        #Loop over all results
            #Add unique values foir every parameter

        #Find number of runs from r
        #If number of values for x and y > 3 then plot heatmap, otherwise finish

        #Create a 2D grid with the dimensions of the number of values for x and y
        #For all values of x
            #For all values of y
                # For all values in r
                    #Fixing all other values to 1 (in the mean time)
                    #Add/sum TTA into 2D grid
                    #if last r divide by number of runs

        #Plot 2D grid




    def plotAll(self):
        """Plot all the important elements of each result"""
        for result in self.results:
            plotPath = "results/"+self.execID+"/plots/"+str(result.shape)
            os.makedirs(plotPath, exist_ok=True)
            self.plotMissingSamples(result, plotPath)
            self.plotProgress(result, plotPath)
            self.plotSentData(result, plotPath)
            self.plotRecvData(result, plotPath)
            self.plotDupData(result, plotPath)
            if self.config.saveRCdist:
                self.plotRowCol(result, plotPath)

    def plotMissingSamples(self, result, plotPath):
        """Plots the missing samples in the network"""
        conf = {}
        attrbs = self.__get_attrbs__(result)
        conf["textBox"] = "Block Size R: "+attrbs['bsrn']+"\nBlock Size C: "+attrbs['bscn']\
        +"\nNumber of nodes: "+attrbs['nn']+"\nFailure rate: "+attrbs['fr']+" \nNetwork degree: "+attrbs['nd']
        conf["title"] = "Missing Samples"
        conf["type"] = "plot"
        conf["legLoc"] = 1
        conf["desLoc"] = 1
        conf["colors"] = ["m-"]
        conf["labels"] = ["Missing Samples"]
        conf["xlabel"] = "Time (ms)"
        conf["ylabel"] = "Number of Missing Samples"
        conf["data"] = [result.missingVector]
        conf["xdots"] = [x*self.config.stepDuration for x in range(len(result.missingVector))]
        conf["path"] = plotPath+"/missingSamples.png"
        maxi = 0
        for v in conf["data"]:
            if max(v) > maxi:
                maxi = max(v)
        conf["yaxismax"] = maxi
        plotData(conf)
        print("Plot %s created." % conf["path"])

    def plotProgress(self, result, plotPath):
        """Plots the percentage of nodes ready in the network"""
        vector1 = result.metrics["progress"]["nodes ready"]
        vector2 = result.metrics["progress"]["validators ready"]
        vector3 = result.metrics["progress"]["samples received"]
        vector4 = result.metrics["progress"]["DASampling progress (query all)"]
        vector5 = result.metrics["progress"]["DASampling progress (query 3)"]
        vector6 = result.metrics["progress"]["DASampling progress (query 2)"]
        vector7 = result.metrics["progress"]["DASampling progress (query 1)"]
        vector8 = result.metrics["progress"]["DASampling ready (query all)"]
        vector9 = result.metrics["progress"]["DASampling ready (query 3)"]
        vector10 = result.metrics["progress"]["DASampling ready (query 2)"]
        vector11 = result.metrics["progress"]["DASampling ready (query 1)"]
        conf = {}
        attrbs = self.__get_attrbs__(result)
        conf["textBox"] = "Block Size R: "+attrbs['bsrn']+"\nBlock Size C: "+attrbs['bscn']\
        +"\nNumber of nodes: "+attrbs['nn']+"\nFailure rate: "+attrbs['fr']+" \nNetwork degree: "+attrbs['nd']
        conf["title"] = "Nodes/validators ready"
        conf["type"] = "plot"
        conf["legLoc"] = 2
        conf["desLoc"] = 2
        conf["colors"] = ["g-", "b-", "r-", "m-", "m--", "m-.", "m:", "c-", "c--", "c-.", "c:"]
        conf["labels"] = ["Nodes", "Validators", "Custody samples",
                          "DASampling progress (query all)", "DASampling progress (query 3)", "DASampling progress (query 2)", "DASampling progress (query 1)",
                          "DASampling ready (query all)", "DASampling ready (query 3)", "DASampling ready (query 2)", "DASampling ready (query 1)"]
        conf["xlabel"] = "Time (ms)"
        conf["ylabel"] = "Ratio of all (0..1)"
        conf["data"] = [vector1, vector2, vector3, vector4, vector5, vector6, vector7, vector8, vector9, vector10, vector11 ]
        conf["xdots"] = [x*self.config.stepDuration for x in range(len(vector1))]
        conf["path"] = plotPath+"/nodesReady.png"
        maxi = 0
        for v in conf["data"]:
            if max(v) > maxi:
                maxi = max(v)
        conf["yaxismax"] = maxi
        plotData(conf)
        print("Plot %s created." % conf["path"])

    def plotSentData(self, result, plotPath):
        """Plots the percentage of nodes ready in the network"""
        vector1 = result.metrics["progress"]["TX builder mean"]
        vector2 = result.metrics["progress"]["TX class1 mean"]
        vector3 = result.metrics["progress"]["TX class2 mean"]
        for i in range(len(vector1)):
            vector1[i] = (vector1[i] * 8 * (1000/self.config.stepDuration) * self.config.segmentSize) / 1000000
            vector2[i] = (vector2[i] * 8 * (1000/self.config.stepDuration) * self.config.segmentSize) / 1000000
            vector3[i] = (vector3[i] * 8 * (1000/self.config.stepDuration) * self.config.segmentSize) / 1000000
        conf = {}
        attrbs = self.__get_attrbs__(result)
        conf["textBox"] = "Block Size R: "+attrbs['bsrn']+"\nBlock Size C: "+attrbs['bscn']\
        +"\nNumber of nodes: "+attrbs['nn']+"\nFailure rate: "+attrbs['fr']+" \nNetwork degree: "+attrbs['nd']
        conf["title"] = "Sent data"
        conf["type"] = "plot"
        conf["legLoc"] = 2
        conf["desLoc"] = 2
        conf["colors"] = ["y-", "c-", "m-"]
        conf["labels"] = ["Block Builder", "Solo stakers", "Staking pools"]
        conf["xlabel"] = "Time (ms)"
        conf["ylabel"] = "Bandwidth (MBits/s)"
        conf["data"] = [vector1, vector2, vector3]
        conf["xdots"] = [x*self.config.stepDuration for x in range(len(vector1))]
        conf["path"] = plotPath+"/sentData.png"
        maxi = 0
        for v in conf["data"]:
            if max(v) > maxi:
                maxi = max(v)
        conf["yaxismax"] = maxi
        plotData(conf)
        print("Plot %s created." % conf["path"])

    def plotRecvData(self, result, plotPath):
        """Plots the percentage of nodes ready in the network"""
        vector1 = result.metrics["progress"]["RX class1 mean"]
        vector2 = result.metrics["progress"]["RX class2 mean"]
        for i in range(len(vector1)):
            vector1[i] = (vector1[i] * 8 * (1000/self.config.stepDuration) * self.config.segmentSize) / 1000000
            vector2[i] = (vector2[i] * 8 * (1000/self.config.stepDuration) * self.config.segmentSize) / 1000000
        conf = {}
        attrbs = self.__get_attrbs__(result)
        conf["textBox"] = "Block Size R: "+attrbs['bsrn']+"\nBlock Size C: "+attrbs['bscn']\
        +"\nNumber of nodes: "+attrbs['nn']+"\nFailure rate: "+attrbs['fr']+" \nNetwork degree: "+attrbs['nd']
        conf["title"] = "Received data"
        conf["type"] = "plot"
        conf["legLoc"] = 2
        conf["desLoc"] = 2
        conf["colors"] = ["c-", "m-"]
        conf["labels"] = ["Solo stakers", "Staking pools"]
        conf["xlabel"] = "Time (ms)"
        conf["ylabel"] = "Bandwidth (MBits/s)"
        conf["data"] = [vector1, vector2]
        conf["xdots"] = [x*self.config.stepDuration for x in range(len(vector1))]
        conf["path"] = plotPath+"/recvData.png"
        maxi = 0
        for v in conf["data"]:
            if max(v) > maxi:
                maxi = max(v)
        conf["yaxismax"] = maxi
        plotData(conf)
        print("Plot %s created." % conf["path"])

    def plotDupData(self, result, plotPath):
        """Plots the percentage of nodes ready in the network"""
        vector1 = result.metrics["progress"]["Dup class1 mean"]
        vector2 = result.metrics["progress"]["Dup class2 mean"]
        for i in range(len(vector1)):
            vector1[i] = (vector1[i] * 8 * (1000/self.config.stepDuration) * self.config.segmentSize) / 1000000
            vector2[i] = (vector2[i] * 8 * (1000/self.config.stepDuration) * self.config.segmentSize) / 1000000
        conf = {}
        attrbs = self.__get_attrbs__(result)
        conf["textBox"] = "Block Size R: "+attrbs['bsrn']+"\nBlock Size C: "+attrbs['bscn']\
        +"\nNumber of nodes: "+attrbs['nn']+"\nFailure rate: "+attrbs['fr']+" \nNetwork degree: "+attrbs['nd']
        conf["title"] = "Duplicated data"
        conf["type"] = "plot"
        conf["legLoc"] = 2
        conf["desLoc"] = 2
        conf["colors"] = ["c-", "m-"]
        conf["labels"] = ["Solo stakers", "Staking pools"]
        conf["xlabel"] = "Time (ms)"
        conf["ylabel"] = "Bandwidth (MBits/s)"
        conf["data"] = [vector1, vector2]
        conf["xdots"] = [x*self.config.stepDuration for x in range(len(vector1))]
        conf["path"] = plotPath+"/dupData.png"
        maxi = 0
        for v in conf["data"]:
            if max(v) > maxi:
                maxi = max(v)
        conf["yaxismax"] = maxi
        plotData(conf)
        print("Plot %s created." % conf["path"])

    def plotRowCol(self, result, plotPath):
        """Plots the percentage of nodes ready in the network"""
        vector1 = result.metrics["rowDist"]
        vector2 = result.metrics["columnDist"]
        if len(vector1) > len(vector2):
            vector2 += [np.nan] * (len(vector1) - len(vector2))
        elif len(vector1) < len(vector2):
            vector1 += [np.nan] * (len(vector2) - len(vector1))
        conf = {}
        attrbs = self.__get_attrbs__(result)
        conf["textBox"] = "Block Size R: "+attrbs['bsrn']+"\nBlock Size C: "+attrbs['bscn']\
        +"\nNumber of nodes: "+attrbs['nn']+"\nFailure rate: "+attrbs['fr']+" \nNetwork degree: "+attrbs['nd']
        conf["title"] = "Row/Column distribution"
        conf["type"] = "bar"
        conf["legLoc"] = 2
        conf["desLoc"] = 2
        conf["colors"] = ["r+", "b+"]
        conf["labels"] = ["Rows", "Columns"]
        conf["xlabel"] = "Row/Column ID"
        conf["ylabel"] = "Validators subscribed"
        conf["data"] = [vector1, vector2]
        conf["xdots"] = range(len(vector1))
        conf["path"] = plotPath+"/RowColDist.png"
        maxi = 0
        for v in conf["data"]:
            if np.nanmax(v) > maxi:
                maxi = max(v)
        conf["yaxismax"] = maxi
        plotData(conf)
        print("Plot %s created." % conf["path"])

