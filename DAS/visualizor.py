#!/bin/python3

import matplotlib.pyplot as plt
import os

def plotData(conf):
    plt.clf()
    fig = plt.figure("6, 3")
    if conf["desLoc"] == 1:
        xDes = 0
    else:
        xDes = conf["xdots"][-1] * 0.6
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    plt.text(xDes, max(conf["data"][0])/4, conf["textBox"], fontsize=10, verticalalignment='top', bbox=props)
    for i in range(len(conf["data"])):
        plt.plot(conf["xdots"], conf["data"][i], conf["colors"][i], label=conf["labels"][i])
    plt.title(conf["title"])
    plt.ylabel(conf["ylabel"])
    plt.xlabel(conf["xlabel"])
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

    def plotAll(self):
        """Plot all the important elements of each result"""
        for result in self.results:
            self.plotMissingSamples(result)
            self.plotProgress(result)

    def plotMissingSamples(self, result):
        """Plots the missing samples in the network"""
        conf = {}
        text = str(result.shape).split("-")
        conf["textBox"] = "Block Size: "+text[1]+"\nNumber of nodes: "+text[3]\
        +"\nFailure rate: "+text[7]+" \nNetwork degree: "+text[23]+"\nX: "+text[11]+" rows/columns"
        conf["title"] = "Missing Samples"
        conf["legLoc"] = 1
        conf["desLoc"] = 1
        conf["colors"] = ["m-"]
        conf["labels"] = ["Missing Samples"]
        conf["xlabel"] = "Time (ms)"
        conf["ylabel"] = "Number of Missing Samples"
        conf["data"] = [result.missingVector]
        conf["xdots"] = [x*self.config.stepDuration for x in range(len(result.missingVector))]
        conf["path"] = "results/"+self.execID+"/plots/missingSamples-"+str(result.shape)+".png"
        plotData(conf)
        print("Plot %s created." % conf["path"])

    def plotProgress(self, result):
        """Plots the percentage of nodes ready in the network"""
        vector1 = result.metrics["progress"]["nodes ready"]
        vector2 = result.metrics["progress"]["validators ready"]
        vector3 = result.metrics["progress"]["samples received"]
        conf = {}
        text = str(result.shape).split("-")
        conf["textBox"] = "Block Size: "+text[1]+"\nNumber of nodes: "+text[3]\
        +"\nFailure rate: "+text[7]+" \nNetwork degree: "+text[23]+"\nX: "+text[11]+" rows/columns"
        conf["title"] = "Nodes/validators ready"
        conf["legLoc"] = 2
        conf["desLoc"] = 2
        conf["colors"] = ["g-", "b-", "r-"]
        conf["labels"] = ["Nodes", "Validators", "Samples"]
        conf["xlabel"] = "Time (ms)"
        conf["ylabel"] = "Percentage (%)"
        conf["data"] = [vector1, vector2, vector3]
        conf["xdots"] = [x*self.config.stepDuration for x in range(len(vector1))]
        conf["path"] = "results/"+self.execID+"/plots/nodesReady-"+str(result.shape)+".png"
        plotData(conf)
        print("Plot %s created." % conf["path"])

