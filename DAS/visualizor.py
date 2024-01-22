#!/bin/python3

import matplotlib.pyplot as plt
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
    if conf["type"] == "plot":
        for i in range(len(conf["data"])):
            plt.plot(conf["xdots"], conf["data"][i], conf["colors"][i], label=conf["labels"][i])
    elif conf["type"] == "individual_bar":
        plt.bar(conf["xdots"], conf["data"])
    elif conf["type"] == "grouped_bar":
        for i in range(len(conf["data"])):
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
            self.plotMessagesSent(result, plotPath)
            self.plotMessagesRecv(result, plotPath)
            self.plotSampleRecv(result, plotPath)
            self.plotMissingSamples(result, plotPath)
            self.plotProgress(result, plotPath)
            self.plotSentData(result, plotPath)
            self.plotRecvData(result, plotPath)
            self.plotDupData(result, plotPath)
            if self.config.saveRCdist:
                self.plotRowCol(result, plotPath)

    def plotSampleRecv(self, result, plotPath):
        """Plots the percentage sampleRecv for each node"""
        conf = {}
        text = str(result.shape).split("-")
        conf["textBox"] = "Block Size: "+text[1]+"\nNumber of nodes: "+text[3]\
            +"\nFailure rate: "+text[7]+" \nNetwork degree: "+text[23]+"\nX: "+text[11]+" rows/columns"+"\nMalicious Nodes: "+text[27]+"%"
        conf["title"] = "Percentage of Samples Received by Nodes"
        conf["type"] = "individual_bar"
        conf["legLoc"] = 1
        conf["desLoc"] = 1
        conf["xlabel"] = "Nodes"
        conf["ylabel"] = "Percentage of samples received (%)"
        total_samples = result.shape.blockSize * result.shape.blockSize
        percentage_data = [(count / total_samples) * 100 for count in result.sampleRecvCount]
        conf["data"] = percentage_data
        conf["xdots"] = range(result.shape.numberNodes)
        conf["path"] = plotPath + "/sampleRecv.png"
        maxi = max(conf["data"])
        conf["yaxismax"] = maxi
        plotData(conf)
        print("Plot %s created." % conf["path"])
    
    def plotMissingSamples(self, result, plotPath):
        """Plots the missing samples in the network"""
        conf = {}
        text = str(result.shape).split("-")
        conf["textBox"] = "Block Size: "+text[1]+"\nNumber of nodes: "+text[3]\
        +"\nFailure rate: "+text[7]+" \nNetwork degree: "+text[23]+"\nX: "+text[11]+" rows/columns"+"\nMalicious Nodes: "+text[27]+"%"
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
        vector1 = [x * 100 for x in result.metrics["progress"]["nodes ready"]]
        vector2 = [x * 100 for x in result.metrics["progress"]["validators ready"]]
        vector3 = [x * 100 for x in result.metrics["progress"]["samples received"]]   
        conf = {}
        text = str(result.shape).split("-")
        conf["textBox"] = "Block Size: "+text[1]+"\nNumber of nodes: "+text[3]\
        +"\nFailure rate: "+text[7]+" \nNetwork degree: "+text[23]+"\nX: "+text[11]+" rows/columns"+"\nMalicious Nodes: "+text[27]+"%"
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
        conf["textBox"] = "Block Size: "+text[1]+"\nNumber of nodes: "+text[3]\
        +"\nFailure rate: "+text[7]+" \nNetwork degree: "+text[23]+"\nX: "+text[11]+" rows/columns"+"\nMalicious Nodes: "+text[27]+"%"
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
        conf["textBox"] = "Block Size: "+text[1]+"\nNumber of nodes: "+text[3]\
        +"\nFailure rate: "+text[7]+" \nNetwork degree: "+text[23]+"\nX: "+text[11]+" rows/columns"+"\nMalicious Nodes: "+text[27]+"%"
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
        conf["textBox"] = "Block Size: "+text[1]+"\nNumber of nodes: "+text[3]\
        +"\nFailure rate: "+text[7]+" \nNetwork degree: "+text[23]+"\nX: "+text[11]+" rows/columns"+"\nMalicious Nodes: "+text[27]+"%"
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
        conf = {}
        text = str(result.shape).split("-")
        conf["textBox"] = "Block Size: "+text[1]+"\nNumber of nodes: "+text[3]\
        +"\nFailure rate: "+text[7]+" \nNetwork degree: "+text[23]+"\nX: "+text[11]+" rows/columns"+"\nMalicious Nodes: "+text[27]+"%"
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
            if max(v) > maxi:
                maxi = max(v)
        conf["yaxismax"] = maxi
        plotData(conf)
        print("Plot %s created." % conf["path"])

    def plotMessagesSent(self, result, plotPath):
        """Plots the number of messages sent by all nodes"""
        conf = {}
        text = str(result.shape).split("-")
        conf["textBox"] = "Block Size: "+text[1]+"\nNumber of nodes: "+text[3]\
            +"\nFailure rate: "+text[7]+" \nNetwork degree: "+text[23]+"\nX: "+text[11]+" rows/columns"+"\nMalicious Nodes: "+text[27]+"%"
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
        conf["textBox"] = "Block Size: "+text[1]+"\nNumber of nodes: "+text[3]\
            +"\nFailure rate: "+text[7]+" \nNetwork degree: "+text[23]+"\nX: "+text[11]+" rows/columns"+"\nMalicious Nodes: "+text[27]+"%"
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

