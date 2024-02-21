#!/bin/python3

import matplotlib.pyplot as plt
import numpy as np
import os

def plotData(conf):
    plt.clf()
    fig = plt.figure("9, 3")
    plt.grid(True)
    if conf["desLoc"] == 1:
        xDes = 0
    else:
        xDes = conf["xdots"][-1] * 0.6
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    plt.text(xDes, conf["yaxismax"]/3, conf["textBox"], fontsize=10, verticalalignment='top', bbox=props)
    if conf["type"] == "plot" or conf["type"] == "plot_with_1line":
        for i in range(len(conf["data"])):
            plt.plot(conf["xdots"], conf["data"][i], conf["colors"][i], label=conf["labels"][i])
    elif conf["type"] == "individual_bar" or conf["type"] == "individual_bar_with_2line":
        plt.bar(conf["xdots"], conf["data"])
    elif conf["type"] == "grouped_bar":
        for i in range(len(conf["data"])):
            plt.bar(conf["xdots"], conf["data"][i], label=conf["labels"][i])
    if conf["type"] == "individual_bar_with_2line":
        plt.axhline(y = conf["expected_value1"], color='r', linestyle='--', label=conf["line_label1"])
        plt.axhline(y = conf["expected_value2"], color='g', linestyle='--', label=conf["line_label2"]) 
    if conf["type"] == "plot_with_1line":
        plt.axhline(y = conf["expected_value"], color='g', linestyle='--', label=conf["line_label"])
    plt.title(conf["title"])
    plt.ylabel(conf["ylabel"])
    plt.xlabel(conf["xlabel"])
    plt.ylim(0, conf["yaxismax"]*1.1)
    plt.legend(loc=conf["legLoc"])
    plt.savefig(conf["path"], bbox_inches="tight")

def plotBoxData(conf):
    plt.clf()
    plt.grid(True)
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    num_boxes = len(conf["data"])
    positions = np.arange(num_boxes)
    plt.text(0.05, 0.05, conf["textBox"], fontsize=10, verticalalignment='bottom', transform=plt.gca().transAxes, bbox=props)
    plt.boxplot(conf["data"], patch_artist=True, showmeans=True, meanline=True, positions=positions)
    plt.title(conf["title"], fontsize=14)
    plt.ylabel(conf["ylabel"], fontsize=12)
    plt.xlabel(conf["xlabel"], fontsize=12)
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)
    plt.savefig(conf["path"], bbox_inches="tight")

class Visualizor:
    """This class helps the visualization of the results"""

    def __init__(self, execID, config, results):
        """Initialize the visualizer module"""
        self.execID = execID
        self.config = config
        self.results = results
        os.makedirs("results/"+self.execID+"/plots", exist_ok=True)

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
            self.plotRestoreRowCount(result, plotPath)
            self.plotRestoreColumnCount(result, plotPath)
            self.plotMessagesSent(result, plotPath)
            self.plotMessagesRecv(result, plotPath)
            self.plotBoxMessagesRecv(result, plotPath)
            self.plotSampleRecv(result, plotPath)
            self.plotBoxSampleRecv(result, plotPath)
            self.plotMissingSamples(result, plotPath)
            self.plotProgress(result, plotPath)
            self.plotSentData(result, plotPath)
            self.plotRecvData(result, plotPath)
            self.plotDupData(result, plotPath)
            self.plotSamplesRepaired(result, plotPath)
            if self.config.saveRCdist:
                self.plotRowCol(result, plotPath)

    def plotRestoreRowCount(self, result, plotPath):
        """Plots the restoreRowCount for each node"""
        conf = {}
        text = str(result.shape).split("-")
        conf["textBox"] = "Row Size: "+text[2]+"\nColumn Size: "+text[6]+"\nNumber of nodes: "+text[10]\
            +"\nFailure rate: "+text[14]+"%"+"\nNetwork degree: "+text[32]+"\nMalicious Nodes: "+text[36]+"%"
        conf["title"] = "Restore Row Count for Each Node"
        conf["type"] = "individual_bar"
        conf["legLoc"] = 1
        conf["desLoc"] = 1
        conf["xlabel"] = "Nodes"
        conf["ylabel"] = "Restore Row Count"
        conf["data"] = result.restoreRowCount
        conf["xdots"] = range(result.shape.numberNodes)
        conf["path"] = plotPath + "/restoreRowCount.png"
        maxi = max(conf["data"])
        conf["yaxismax"] = maxi
        plotData(conf)
        print("Plot %s created." % conf["path"])

    def plotRestoreColumnCount(self, result, plotPath):
        """Plots the restoreColumnCount for each node"""
        conf = {}
        text = str(result.shape).split("-")
        conf["textBox"] = "Row Size: "+text[2]+"\nColumn Size: "+text[6]+"\nNumber of nodes: "+text[10]\
            +"\nFailure rate: "+text[14]+"%"+"\nNetwork degree: "+text[32]+"\nMalicious Nodes: "+text[36]+"%"
        conf["title"] = "Restore Column Count for Each Node"
        conf["type"] = "individual_bar"
        conf["legLoc"] = 1
        conf["desLoc"] = 1
        conf["xlabel"] = "Nodes"
        conf["ylabel"] = "Restore Column Count"
        conf["data"] = result.restoreColumnCount
        conf["xdots"] = range(result.shape.numberNodes)
        conf["path"] = plotPath + "/restoreColumnCount.png"
        maxi = max(conf["data"])
        conf["yaxismax"] = maxi
        plotData(conf)
        print("Plot %s created." % conf["path"])

    def plotSampleRecv(self, result, plotPath):
        """Plots the percentage sampleRecv for each node"""
        conf = {}
        text = str(result.shape).split("-")
        conf["textBox"] = "Row Size: "+text[2]+"\nColumn Size: "+text[6]+"\nNumber of nodes: "+text[10]\
            +"\nFailure rate: "+text[14]+"%"+"\nNetwork degree: "+text[32]+"\nMalicious Nodes: "+text[36]+"%"
        conf["title"] = "Percentage of Samples Received by Nodes"
        conf["type"] = "individual_bar_with_2line"
        conf["legLoc"] = 1
        conf["desLoc"] = 1
        conf["xlabel"] = "Nodes"
        conf["ylabel"] = "Percentage of samples received (%)"
        total_samples = result.shape.blockSizeR * result.shape.blockSizeC
        percentage_data = [(count / total_samples) * 100 for count in result.sampleRecvCount]
        conf["data"] = percentage_data
        conf["xdots"] = range(result.shape.numberNodes)
        conf["path"] = plotPath + "/sampleRecv.png"
        maxi = max(conf["data"])
        # conf["yaxismax"] = maxi * 1.1
        expected_percentage1 = (result.shape.vpn1 * (result.shape.blockSizeR * result.shape.chiR + result.shape.blockSizeC * result.shape.chiC) * 100)/total_samples
        expected_percentage2 = (result.shape.vpn2 * (result.shape.blockSizeR * result.shape.chiR + result.shape.blockSizeC * result.shape.chiC) * 100)/total_samples
        if expected_percentage1 > 100:
            expected_percentage1 = 100
        if expected_percentage2 > 100:
            expected_percentage2 = 100
        conf["expected_value1"] = expected_percentage1
        conf["expected_value2"] = expected_percentage2
        conf["line_label1"] = "Expected Value for class 1 nodes"
        conf["line_label2"] = "Expected Value for class 2 nodes"
        conf["yaxismax"] = max(expected_percentage1, expected_percentage2) * 1.05
        plotData(conf)
        print("Plot %s created." % conf["path"])
    
    def plotBoxSampleRecv(self, result, plotPath):
        """Box Plot of the sampleRecv for each node"""
        conf = {}
        text = str(result.shape).split("-")
        conf["textBox"] = "Row Size: "+text[2]+"\nColumn Size: "+text[6]+"\nNumber of nodes: "+text[10]\
            +"\nFailure rate: "+text[14]+"%"+"\nNetwork degree: "+text[32]+"\nMalicious Nodes: "+text[36]+"%"
        conf["title"] = "Number of Samples Received by Nodes"
        conf["type"] = "individual_bar_with_2line"
        conf["legLoc"] = 1
        conf["desLoc"] = 1
        conf["xlabel"] = "Node Type"
        conf["ylabel"] = "Number of samples received (%)"
        n1 = int(result.numberNodes * result.class1ratio)
        conf["data"] = [result.sampleRecvCount[1: n1], result.sampleRecvCount[n1: ]]
        conf["xdots"] = range(result.shape.numberNodes)
        conf["path"] = plotPath + "/box_sampleRecv.png"
        plotBoxData(conf)
        print("Plot %s created." % conf["path"])
    
    def plotMissingSamples(self, result, plotPath):
        """Plots the missing samples in the network"""
        conf = {}
        text = str(result.shape).split("-")
        conf["textBox"] = "Row Size: "+text[2]+"\nColumn Size: "+text[6]+"\nNumber of nodes: "+text[10]\
            +"\nFailure rate: "+text[14]+"%"+"\nNetwork degree: "+text[32]+"\nMalicious Nodes: "+text[36]+"%"
        conf["title"] = "Missing Samples"
        conf["type"] = "plot_with_1line"
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
        x = result.shape.blockSizeR * result.shape.chiR + result.shape.blockSizeC * result.shape.chiC
        conf["expected_value"] = (result.shape.numberNodes - 1) * (result.shape.class1ratio * result.shape.vpn1 * x + (1 - result.shape.class1ratio) * result.shape.vpn2 * x)
        conf["line_label"] = "Total samples to deliver"
        plotData(conf)
        print("Plot %s created." % conf["path"])

    def plotProgress(self, result, plotPath):
        """Plots the percentage of nodes ready in the network"""
        vector1 = [x * 100 for x in result.metrics["progress"]["nodes ready"]]
        vector2 = [x * 100 for x in result.metrics["progress"]["validators ready"]]
        vector3 = [x * 100 for x in result.metrics["progress"]["samples received"]]   
        conf = {}
        text = str(result.shape).split("-")
        conf["textBox"] = "Row Size: "+text[2]+"\nColumn Size: "+text[6]+"\nNumber of nodes: "+text[10]\
            +"\nFailure rate: "+text[14]+"%"+"\nNetwork degree: "+text[32]+"\nMalicious Nodes: "+text[36]+"%"
        conf["title"] = "Nodes/validators ready"
        conf["type"] = "plot"
        conf["legLoc"] = 2
        conf["desLoc"] = 2
        conf["colors"] = ["g-", "b-", "r-"]
        conf["labels"] = ["Nodes", "Validators", "Samples"]
        conf["xlabel"] = "Time (ms)"
        conf["ylabel"] = "Percentage (%)"
        conf["data"] = [vector1, vector2, vector3]
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
        text = str(result.shape).split("-")
        conf["textBox"] = "Row Size: "+text[2]+"\nColumn Size: "+text[6]+"\nNumber of nodes: "+text[10]\
            +"\nFailure rate: "+text[14]+"%"+"\nNetwork degree: "+text[32]+"\nMalicious Nodes: "+text[36]+"%"
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
        text = str(result.shape).split("-")
        conf["textBox"] = "Row Size: "+text[2]+"\nColumn Size: "+text[6]+"\nNumber of nodes: "+text[10]\
            +"\nFailure rate: "+text[14]+"%"+" \nNetwork degree: "+text[32]+"\nMalicious Nodes: "+text[36]+"%"
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
        text = str(result.shape).split("-")
        conf["textBox"] = "Row Size: "+text[2]+"\nColumn Size: "+text[6]+"\nNumber of nodes: "+text[10]\
            +"\nFailure rate: "+text[14]+"%"+" \nNetwork degree: "+text[32]+"\nMalicious Nodes: "+text[36]+"%"
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
        text = str(result.shape).split("-")
        conf["textBox"] = "Row Size: "+text[2]+"\nColumn Size: "+text[6]+"\nNumber of nodes: "+text[10]\
            +"\nFailure rate: "+text[14]+"%"+" \nNetwork degree: "+text[32]+"\nMalicious Nodes: "+text[36]+"%"
        conf["title"] = "Row/Column distribution"
        conf["type"] = "grouped_bar"
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

    def plotMessagesSent(self, result, plotPath):
        """Plots the number of messages sent by all nodes"""
        conf = {}
        text = str(result.shape).split("-")
        conf["textBox"] = "Row Size: "+text[2]+"\nColumn Size: "+text[6]+"\nNumber of nodes: "+text[10]\
            +"\nFailure rate: "+text[14]+"%"+" \nNetwork degree: "+text[32]+"\nMalicious Nodes: "+text[36]+"%"
        conf["title"] = "Number of Messages Sent by Nodes"
        conf["type"] = "individual_bar"
        conf["legLoc"] = 1
        conf["desLoc"] = 1
        conf["xlabel"] = "Nodes"
        conf["ylabel"] = "Number of Messages Sent"
        conf["data"] = result.msgSentCount
        conf["xdots"] = range(result.shape.numberNodes)
        conf["path"] = plotPath + "/messagesSent.png"
        maxi = max(conf["data"])
        conf["yaxismax"] = maxi
        plotData(conf)
        print("Plot %s created." % conf["path"])

    def plotMessagesRecv(self, result, plotPath):
        """Plots the number of messages received by all nodes"""
        conf = {}
        text = str(result.shape).split("-")
        conf["textBox"] = "Row Size: "+text[2]+"\nColumn Size: "+text[6]+"\nNumber of nodes: "+text[10]\
            +"\nFailure rate: "+text[14]+"%"+"\nNetwork degree: "+text[32]+"\nMalicious Nodes: "+text[36]+"%"
        conf["title"] = "Number of Messages Received by Nodes"
        conf["type"] = "individual_bar"
        conf["legLoc"] = 1
        conf["desLoc"] = 1
        conf["xlabel"] = "Nodes"
        conf["ylabel"] = "Number of Messages Received"
        conf["data"] = result.msgRecvCount
        conf["xdots"] = range(result.shape.numberNodes)
        conf["path"] = plotPath + "/messagesRecv.png"
        maxi = max(conf["data"])
        conf["yaxismax"] = maxi
        plotData(conf)
        print("Plot %s created." % conf["path"])
    
    def plotBoxMessagesRecv(self, result, plotPath):
        """Plots the number of messages received by all nodes"""
        conf = {}
        text = str(result.shape).split("-")
        conf["textBox"] = "Row Size: "+text[2]+"\nColumn Size: "+text[6]+"\nNumber of nodes: "+text[10]\
            +"\nFailure rate: "+text[14]+"%"+"\nNetwork degree: "+text[32]+"\nMalicious Nodes: "+text[36]+"%"
        conf["title"] = "Number of Messages Received by Nodes"
        conf["type"] = "individual_bar"
        conf["legLoc"] = 1
        conf["desLoc"] = 1
        conf["xlabel"] = "Node Type"
        conf["ylabel"] = "Number of Messages Received"
        n1 = int(result.numberNodes * result.class1ratio)
        conf["data"] = [result.msgRecvCount[1: n1], result.msgRecvCount[n1: ]]
        conf["xdots"] = range(result.shape.numberNodes)
        conf["path"] = plotPath + "/box_messagesRecv.png"
        maxi = max(conf["data"])
        conf["yaxismax"] = maxi
        plotBoxData(conf)
        print("Plot %s created." % conf["path"])

    def plotSamplesRepaired(self, result, plotPath):
        """Plots the number of samples repaired by all nodes"""
        conf = {}
        text = str(result.shape).split("-")
        conf["textBox"] = "Row Size: "+text[2]+"\nColumn Size: "+text[6]+"\nNumber of nodes: "+text[10]\
            +"\nFailure rate: "+text[14]+"%"+"\nNetwork degree: "+text[32]+"\nMalicious Nodes: "+text[36]+"%"
        conf["title"] = "Number of Samples Repaired by Nodes"
        conf["type"] = "individual_bar"
        conf["legLoc"] = 1
        conf["desLoc"] = 1
        conf["xlabel"] = "Nodes"
        conf["ylabel"] = "Number of Samples Repaired"
        conf["data"] = result.repairedSampleCount
        conf["xdots"] = range(result.shape.numberNodes)
        conf["path"] = plotPath + "/repairedSampleCount.png"
        maxi = max(conf["data"])
        conf["yaxismax"] = maxi
        plotData(conf)
        print("Plot %s created." % conf["path"])
