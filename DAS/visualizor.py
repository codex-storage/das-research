#!/bin/python3

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
import pandas as pd

def plotData(conf):
    plt.clf()
    fig = plt.figure("9, 3")
    plt.grid(True)
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    plt.text(1.05, 0.05, conf["textBox"], fontsize=14, verticalalignment='bottom', transform=plt.gca().transAxes, bbox=props)
    if conf["type"] == "plot" or conf["type"] == "plot_with_1line":
        for i in range(len(conf["data"])):
            # plt.plot(conf["xdots"], conf["data"][i], conf["colors"][i], label=conf["labels"][i])
            plt.plot(conf["xdots"], conf["data"][i], label=conf["labels"][i])
    elif conf["type"] == "individual_bar" or conf["type"] == "individual_bar_with_2line":
        plt.bar(conf["xdots"], conf["data"])
    elif conf["type"] == "grouped_bar":
        for i in range(len(conf["data"])):
            plt.bar(conf["xdots"], conf["data"][i], label=conf["labels"][i])
    if conf["type"] == "individual_bar_with_2line":
        plt.axhline(y = conf["expected_value1"], color='w', linestyle='--', label=conf["line_label1"])
        plt.axhline(y = conf["expected_value2"], color='g', linestyle='--', label=conf["line_label2"]) 
    if conf["type"] == "plot_with_1line":
        plt.axhline(y = conf["expected_value"], color='g', linestyle='--', label=conf["line_label"])
    plt.title(conf["title"], fontsize=14)
    plt.ylabel(conf["ylabel"], fontsize=12)
    plt.xlabel(conf["xlabel"], fontsize=12)
    plt.ylim(0, conf["yaxismax"]*1.1 if conf["yaxismax"] > 0 else 1)
    plt.legend(loc=conf["legLoc"])
    plt.savefig(conf["path"], bbox_inches="tight")

def plotBoxData(conf):
    plt.clf()
    plt.grid(True)
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    num_boxes = len(conf["data"])
    positions = np.arange(num_boxes)
    plt.text(1.05, 0.05, conf["textBox"], fontsize=14, verticalalignment='bottom', transform=plt.gca().transAxes, bbox=props)
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
    
    def __get_attrbs__(self, result):
        text = str(result.shape).split("-")
        d = dict()
        for i in range(0, len(text), 2):
            d[text[i]] = text[i + 1]
        return d
    
    def __getNodeTypes__(self, group):
        theGroup = dict()
        for nt in self.config.nodeTypesGroup:
            if nt['group'] == group:
                for _k, _v in nt["classes"].items():
                    theGroup[_k] = {
                        "vpn": _v["def"]["validatorsPerNode"],
                        "bw": _v["def"]["bwUplinks"],
                        "w": _v["weight"]
                    }
                break
        
        return theGroup
    
    def __getNodeRanges(self, shape):
        nodeClasses, nodeRatios = [], []
        for _k, _v in shape.nodeTypes["classes"].items():
            nodeClasses.append(_k)
            nodeRatios.append(_v['weight'])
        nodeCounts = [int(shape.numberNodes * ratio / sum(nodeRatios)) for ratio in nodeRatios]
        commulativeSum = [sum(nodeCounts[:i+1]) for i in range(len(nodeCounts))]
        commulativeSum[-1] = shape.numberNodes
        
        return nodeClasses, commulativeSum
    
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
            self.plotMissingSegments(result, plotPath)
            self.plotProgress(result, plotPath)
            self.plotSentData(result, plotPath)
            self.plotRecvData(result, plotPath)
            self.plotDupData(result, plotPath)

            # self.plotSamplesRepaired(result, plotPath)
            # self.plotMessagesSent(result, plotPath)
            # self.plotMessagesRecv(result, plotPath)
            # self.plotSampleRecv(result, plotPath)
            # self.plotRestoreRowCount(result, plotPath)
            # self.plotRestoreColumnCount(result, plotPath)
            if self.config.saveRCdist:
                self.plotRowCol(result, plotPath)

            # self.plotBoxSamplesRepaired(result, plotPath)
            # self.plotBoxMessagesSent(result, plotPath)
            # self.plotBoxMessagesRecv(result, plotPath)
            # self.plotBoxSampleRecv(result, plotPath)
            # self.plotBoxRestoreColumnCount(result, plotPath)
            # self.plotBoxRestoreRowCount(result, plotPath)
            # if self.config.saveRCdist:
            #     self.plotBoxRowCol(result, plotPath)

            self.plotBoxenSamplesRepaired(result, plotPath)
            self.plotBoxenMessagesSent(result, plotPath)
            self.plotBoxenMessagesRecv(result, plotPath)
            self.plotBoxenSamplesRecv(result, plotPath)
            self.plotBoxenRestoreRowCount(result, plotPath)
            self.plotBoxenRestoreColumnCount(result, plotPath)
            if self.config.saveRCdist:
                self.plotBoxenRowColDist(result, plotPath)

            self.plotECDFSamplesRepaired(result, plotPath)
            self.plotECDFMessagesSent(result, plotPath)
            self.plotECDFMessagesRecv(result, plotPath)
            self.plotECDFSamplesReceived(result, plotPath)
            self.plotECDFRestoreRowCount(result, plotPath)
            self.plotECDFRestoreColumnCount(result, plotPath)
            if self.config.saveRCdist:
                self.plotECDFRowColDist(result, plotPath)        


    def plotBoxRestoreRowCount(self, result, plotPath):
        """Box Plot of restoreRowCount for all nodes"""
        plt.clf()
        conf = {}
        attrbs = self.__get_attrbs__(result)
        nodeTypes = self.__getNodeTypes__(attrbs['ntypes'])
        nodeTypesTxt = ""
        for _k, _v in nodeTypes.items():
            nodeTypesTxt += f"Type ({_k}): " + str(_v) + "\n"
        if nodeTypesTxt != "": nodeTypesTxt = nodeTypesTxt[: -1]
        conf["textBox"] = "Row Size (N, K): "+attrbs['bsrn']+ ", "+attrbs['bsrk']\
        +"\nColumn Size: (N, K): "+attrbs['bscn']+ ", "+attrbs['bsck']\
        +"\nNumber of nodes: "+attrbs['nn']+"\nFailure rate: "+attrbs['fr']+"%"+"\nMalicious Node: "+attrbs['mn']+"%"+"\nNetwork degree: "+attrbs['nd']\
        +"\nCustody Rows: "+attrbs['cusr']+" (Min: "+attrbs['mcusr']+")"+"\nCustody Cols: "+attrbs['cusc']+" (Min: "+attrbs['mcusc']+")"+"\n"+nodeTypesTxt\
        +"\nSegment Size: "+str(self.config.segmentSize)
        conf["title"] = "Box Plot of Restore Row Count by Nodes"
        conf["xlabel"] = "Node Type"
        conf["ylabel"] = "Restore Row Count"
        n1 = int(result.numberNodes * result.class1ratio)
        class1_data = result.restoreRowCount[1: n1]
        class2_data = result.restoreRowCount[n1+1: ]
        data = [class1_data, class2_data]
        plt.boxplot(data)
        plt.xticks([1, 2], ['Class 1 Nodes', 'Class 2 Nodes'])
        plt.xlabel(conf["xlabel"], fontsize=12)
        plt.ylabel(conf["ylabel"], fontsize=12)
        plt.title(conf["title"], fontsize=14)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        plt.text(1.05, 0.05, conf["textBox"], fontsize=14, verticalalignment='bottom', transform=plt.gca().transAxes, bbox=props)
        plt.savefig(plotPath + "/box_restoreRowCount.png", bbox_inches="tight")
        print("Plot %s created." % (plotPath + "/box_restoreRowCount.png"))

    def plotBoxRestoreColumnCount(self, result, plotPath):
        """Box Plot of restoreColumnCount for all nodes"""
        plt.clf()
        conf = {}
        attrbs = self.__get_attrbs__(result)
        nodeTypes = self.__getNodeTypes__(attrbs['ntypes'])
        nodeTypesTxt = ""
        for _k, _v in nodeTypes.items():
            nodeTypesTxt += f"Type ({_k}): " + str(_v) + "\n"
        if nodeTypesTxt != "": nodeTypesTxt = nodeTypesTxt[: -1]
        conf["textBox"] = "Row Size (N, K): "+attrbs['bsrn']+ ", "+attrbs['bsrk']\
        +"\nColumn Size: (N, K): "+attrbs['bscn']+ ", "+attrbs['bsck']\
        +"\nNumber of nodes: "+attrbs['nn']+"\nFailure rate: "+attrbs['fr']+"%"+"\nMalicious Node: "+attrbs['mn']+"%"+"\nNetwork degree: "+attrbs['nd']\
        +"\nCustody Rows: "+attrbs['cusr']+" (Min: "+attrbs['mcusr']+")"+"\nCustody Cols: "+attrbs['cusc']+" (Min: "+attrbs['mcusc']+")"+"\n"+nodeTypesTxt\
        +"\nSegment Size: "+str(self.config.segmentSize)
        conf["title"] = "Box Plot of Restore Column Count by Nodes"
        conf["xlabel"] = "Node Type"
        conf["ylabel"] = "Restore Column Count"
        n1 = int(result.numberNodes * result.class1ratio)
        class1_data = result.restoreColumnCount[1: n1]
        class2_data = result.restoreColumnCount[n1+1: ]
        data = [class1_data, class2_data]
        plt.boxplot(data)
        plt.xticks([1, 2], ['Class 1 Nodes', 'Class 2 Nodes'])
        plt.xlabel(conf["xlabel"], fontsize=12)
        plt.ylabel(conf["ylabel"], fontsize=12)
        plt.title(conf["title"], fontsize=14)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        plt.text(1.05, 0.05, conf["textBox"], fontsize=14, verticalalignment='bottom', transform=plt.gca().transAxes, bbox=props)
        plt.savefig(plotPath + "/box_restoreColumnCount.png", bbox_inches="tight")
        print("Plot %s created." % (plotPath + "/box_restoreColumnCount.png"))
    
    def plotBoxenRestoreRowCount(self, result, plotPath):
        """Plots the Boxen plot of restoreRowCount for all nodes"""
        plt.clf()
        conf = {}
        attrbs = self.__get_attrbs__(result)
        nodeTypes = self.__getNodeTypes__(attrbs['ntypes'])
        nodeTypesTxt = ""
        for _k, _v in nodeTypes.items():
            nodeTypesTxt += f"Type ({_k}): " + str(_v) + "\n"
        if nodeTypesTxt != "": nodeTypesTxt = nodeTypesTxt[: -1]
        conf["textBox"] = "Row Size (N, K): "+attrbs['bsrn']+ ", "+attrbs['bsrk']\
        +"\nColumn Size: (N, K): "+attrbs['bscn']+ ", "+attrbs['bsck']\
        +"\nNumber of nodes: "+attrbs['nn']+"\nFailure rate: "+attrbs['fr']+"%"+"\nMalicious Node: "+attrbs['mn']+"%"+"\nNetwork degree: "+attrbs['nd']\
        +"\nCustody Rows: "+attrbs['cusr']+" (Min: "+attrbs['mcusr']+")"+"\nCustody Cols: "+attrbs['cusc']+" (Min: "+attrbs['mcusc']+")"+"\n"+nodeTypesTxt\
        +"\nSegment Size: "+str(self.config.segmentSize)
        conf["title"] = "Boxen Plot of Restore Row Count by Nodes"
        conf["xlabel"] = "Restore Row Count"
        conf["ylabel"] = "Nodes"
        data = []
        nodeClasses, nodeRanges = self.__getNodeRanges(result.shape)
        _start = 1
        for _range in nodeRanges:
            data.append(result.restoreRowCount[_start: _range])
            _start = _range
        _values, _categories = [], []
        for _d, _nc in zip(data, nodeClasses):
            _values += _d
            _categories += [f'Class {_nc}'] * len(_d)
        data = pd.DataFrame({
            'values': _values,
            'category': _categories
        })
        plt.figure(figsize=(8, 6))
        sns.boxenplot(x='category', y='values', hue='category', data=data, palette="Set2", ax=plt.gca(), width=0.8)
        plt.xlabel(conf["xlabel"], fontsize=12)
        plt.ylabel(conf["ylabel"], fontsize=12)
        plt.title(conf["title"], fontsize=14)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        plt.text(1.05, 0.05, conf["textBox"], fontsize=14, verticalalignment='bottom', transform=plt.gca().transAxes, bbox=props)
        plt.savefig(plotPath + "/boxen_restoreRowCount.png", bbox_inches="tight")
        print("Plot %s created." % (plotPath + "/boxen_restoreRowCount.png"))

    def plotBoxenRestoreColumnCount(self, result, plotPath):
        """Plots the Boxen plot of restoreColumnCount for all nodes"""
        plt.clf()
        conf = {}
        attrbs = self.__get_attrbs__(result)
        nodeTypes = self.__getNodeTypes__(attrbs['ntypes'])
        nodeTypesTxt = ""
        for _k, _v in nodeTypes.items():
            nodeTypesTxt += f"Type ({_k}): " + str(_v) + "\n"
        if nodeTypesTxt != "": nodeTypesTxt = nodeTypesTxt[: -1]
        conf["textBox"] = "Row Size (N, K): "+attrbs['bsrn']+ ", "+attrbs['bsrk']\
        +"\nColumn Size: (N, K): "+attrbs['bscn']+ ", "+attrbs['bsck']\
        +"\nNumber of nodes: "+attrbs['nn']+"\nFailure rate: "+attrbs['fr']+"%"+"\nMalicious Node: "+attrbs['mn']+"%"+"\nNetwork degree: "+attrbs['nd']\
        +"\nCustody Rows: "+attrbs['cusr']+" (Min: "+attrbs['mcusr']+")"+"\nCustody Cols: "+attrbs['cusc']+" (Min: "+attrbs['mcusc']+")"+"\n"+nodeTypesTxt\
        +"\nSegment Size: "+str(self.config.segmentSize)
        conf["title"] = "Boxen Plot of Restore Column Count by Nodes"
        conf["xlabel"] = "Restore Column Count"
        conf["ylabel"] = "Nodes"
        data = []
        nodeClasses, nodeRanges = self.__getNodeRanges(result.shape)
        _start = 1
        for _range in nodeRanges:
            data.append(result.restoreColumnCount[_start: _range])
            _start = _range
        _values, _categories = [], []
        for _d, _nc in zip(data, nodeClasses):
            _values += _d
            _categories += [f'Class {_nc}'] * len(_d)
        data = pd.DataFrame({
            'values': _values,
            'category': _categories
        })
        plt.figure(figsize=(8, 6))
        sns.boxenplot(x='category', y='values', hue='category', data=data, palette="Set2", ax=plt.gca(), width=0.8)
        plt.xlabel(conf["xlabel"], fontsize=12)
        plt.ylabel(conf["ylabel"], fontsize=12)
        plt.title(conf["title"], fontsize=14)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        plt.text(1.05, 0.05, conf["textBox"], fontsize=14, verticalalignment='bottom', transform=plt.gca().transAxes, bbox=props)
        plt.savefig(plotPath + "/boxen_restoreColumnCount.png", bbox_inches="tight")
        print("Plot %s created." % (plotPath + "/boxen_restoreColumnCount.png"))

    def plotECDFRestoreRowCount(self, result, plotPath):
        """Plots the ECDF of restoreRowCount for all nodes using seaborn's ecdfplot"""
        plt.clf()
        conf = {}
        attrbs = self.__get_attrbs__(result)
        nodeTypes = self.__getNodeTypes__(attrbs['ntypes'])
        nodeTypesTxt = ""
        for _k, _v in nodeTypes.items():
            nodeTypesTxt += f"Type ({_k}): " + str(_v) + "\n"
        if nodeTypesTxt != "": nodeTypesTxt = nodeTypesTxt[: -1]
        conf["textBox"] = "Row Size (N, K): "+attrbs['bsrn']+ ", "+attrbs['bsrk']\
        +"\nColumn Size: (N, K): "+attrbs['bscn']+ ", "+attrbs['bsck']\
        +"\nNumber of nodes: "+attrbs['nn']+"\nFailure rate: "+attrbs['fr']+"%"+"\nMalicious Node: "+attrbs['mn']+"%"+"\nNetwork degree: "+attrbs['nd']\
        +"\nCustody Rows: "+attrbs['cusr']+" (Min: "+attrbs['mcusr']+")"+"\nCustody Cols: "+attrbs['cusc']+" (Min: "+attrbs['mcusc']+")"+"\n"+nodeTypesTxt\
        +"\nSegment Size: "+str(self.config.segmentSize)
        conf["title"] = "ECDF of Restore Row Count by Nodes"
        conf["xlabel"] = "Restore Row Count"
        conf["ylabel"] = "ECDF"
        nodeClasses, nodeRanges = self.__getNodeRanges(result.shape)
        start = 1
        labels = []
        for i, rng in enumerate(nodeRanges):
            class_data = result.repairedSampleCount[start: rng + 1]
            label = f"Class {nodeClasses[i]} Nodes"
            labels.append(label)
            start = rng + 1
            sns.ecdfplot(data=class_data, label=label)
        plt.xlabel(conf["xlabel"], fontsize=12)
        plt.ylabel(conf["ylabel"], fontsize=12)
        plt.title(conf["title"], fontsize=14)
        max_val = max(result.restoreRowCount) * 1.1
        plt.xlim(left=0, right=max_val if max_val > 0 else 1)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        plt.text(1.05, 0.05, conf["textBox"], fontsize=14, verticalalignment='bottom', transform=plt.gca().transAxes, bbox=props)
        plt.legend(title='Node Class', labels=labels, loc=1)
        plt.savefig(plotPath + "/ecdf_restoreRowCount.png", bbox_inches="tight")
        print("Plot %s created." % (plotPath + "/ecdf_restoreRowCount.png"))

    def plotECDFRestoreColumnCount(self, result, plotPath):
        """Plots the ECDF of restoreColumnCount for all nodes using seaborn's ecdfplot"""
        plt.clf()
        conf = {}
        attrbs = self.__get_attrbs__(result)
        nodeTypes = self.__getNodeTypes__(attrbs['ntypes'])
        nodeTypesTxt = ""
        for _k, _v in nodeTypes.items():
            nodeTypesTxt += f"Type ({_k}): " + str(_v) + "\n"
        if nodeTypesTxt != "": nodeTypesTxt = nodeTypesTxt[: -1]
        conf["textBox"] = "Row Size (N, K): "+attrbs['bsrn']+ ", "+attrbs['bsrk']\
        +"\nColumn Size: (N, K): "+attrbs['bscn']+ ", "+attrbs['bsck']\
        +"\nNumber of nodes: "+attrbs['nn']+"\nFailure rate: "+attrbs['fr']+"%"+"\nMalicious Node: "+attrbs['mn']+"%"+"\nNetwork degree: "+attrbs['nd']\
        +"\nCustody Rows: "+attrbs['cusr']+" (Min: "+attrbs['mcusr']+")"+"\nCustody Cols: "+attrbs['cusc']+" (Min: "+attrbs['mcusc']+")"+"\n"+nodeTypesTxt\
        +"\nSegment Size: "+str(self.config.segmentSize)
        conf["title"] = "ECDF of Restore Column Count by Nodes"
        conf["xlabel"] = "Restore Column Count"
        conf["ylabel"] = "ECDF"
        nodeClasses, nodeRanges = self.__getNodeRanges(result.shape)
        start = 1
        labels = []
        for i, rng in enumerate(nodeRanges):
            class_data = result.repairedSampleCount[start: rng + 1]
            label = f"Class {nodeClasses[i]} Nodes"
            labels.append(label)
            start = rng + 1
            sns.ecdfplot(data=class_data, label=label)
        plt.xlabel(conf["xlabel"], fontsize=12)
        plt.ylabel(conf["ylabel"], fontsize=12)
        plt.title(conf["title"], fontsize=14)
        max_val = max(result.restoreColumnCount) * 1.1
        plt.xlim(left=0, right=max_val if max_val > 0 else 1) 
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        plt.text(1.05, 0.05, conf["textBox"], fontsize=14, verticalalignment='bottom', transform=plt.gca().transAxes, bbox=props)
        plt.legend(title='Node Class', labels=labels, loc=1)
        plt.savefig(plotPath + "/ecdf_restoreColumnCount.png", bbox_inches="tight")
        print("Plot %s created." % (plotPath + "/ecdf_restoreColumnCount.png"))
    
    def plotECDFMessagesSent(self, result, plotPath):
        """Plots the ECDF of messages sent by all nodes using seaborn's ecdfplot"""
        plt.clf()
        conf = {}
        attrbs = self.__get_attrbs__(result)
        nodeTypes = self.__getNodeTypes__(attrbs['ntypes'])
        nodeTypesTxt = ""
        for _k, _v in nodeTypes.items():
            nodeTypesTxt += f"Type ({_k}): " + str(_v) + "\n"
        if nodeTypesTxt != "": nodeTypesTxt = nodeTypesTxt[: -1]
        conf["textBox"] = "Row Size (N, K): "+attrbs['bsrn']+ ", "+attrbs['bsrk']\
        +"\nColumn Size: (N, K): "+attrbs['bscn']+ ", "+attrbs['bsck']\
        +"\nNumber of nodes: "+attrbs['nn']+"\nFailure rate: "+attrbs['fr']+"%"+"\nMalicious Node: "+attrbs['mn']+"%"+"\nNetwork degree: "+attrbs['nd']\
        +"\nCustody Rows: "+attrbs['cusr']+" (Min: "+attrbs['mcusr']+")"+"\nCustody Cols: "+attrbs['cusc']+" (Min: "+attrbs['mcusc']+")"+"\n"+nodeTypesTxt\
        +"\nSegment Size: "+str(self.config.segmentSize)
        conf["title"] = "ECDF of Messages Sent by Nodes"
        conf["xlabel"] = "Number of Messages Sent"
        conf["ylabel"] = "ECDF"
        nodeClasses, nodeRanges = self.__getNodeRanges(result.shape)
        start = 1
        labels = []
        for i, rng in enumerate(nodeRanges):
            class_data = result.msgSentCount[start: rng + 1]
            label = f"Class {nodeClasses[i]} Nodes"
            labels.append(label)
            start = rng + 1
            sns.ecdfplot(data=class_data, label=label)
        plt.legend(title='Node Class', labels=labels)
        plt.xlabel(conf["xlabel"], fontsize=12)
        plt.ylabel(conf["ylabel"], fontsize=12)
        plt.title(conf["title"], fontsize=14)
        plt.xlim(left=0, right=max(result.msgSentCount) * 1.1)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        plt.text(1.05, 0.05, conf["textBox"], fontsize=14, verticalalignment='bottom', transform=plt.gca().transAxes, bbox=props)
        plt.savefig(plotPath + "/ecdf_messagesSent.png", bbox_inches="tight")
        print("Plot %s created." % (plotPath + "/ecdf_messagesSent.png"))

    def plotECDFMessagesRecv(self, result, plotPath):
        """Plots the ECDF of messages received by all nodes using seaborn's ecdfplot"""
        plt.clf()
        conf = {}
        attrbs = self.__get_attrbs__(result)
        nodeTypes = self.__getNodeTypes__(attrbs['ntypes'])
        nodeTypesTxt = ""
        for _k, _v in nodeTypes.items():
            nodeTypesTxt += f"Type ({_k}): " + str(_v) + "\n"
        if nodeTypesTxt != "": nodeTypesTxt = nodeTypesTxt[: -1]
        conf["textBox"] = "Row Size (N, K): "+attrbs['bsrn']+ ", "+attrbs['bsrk']\
        +"\nColumn Size: (N, K): "+attrbs['bscn']+ ", "+attrbs['bsck']\
        +"\nNumber of nodes: "+attrbs['nn']+"\nFailure rate: "+attrbs['fr']+"%"+"\nMalicious Node: "+attrbs['mn']+"%"+"\nNetwork degree: "+attrbs['nd']\
        +"\nCustody Rows: "+attrbs['cusr']+" (Min: "+attrbs['mcusr']+")"+"\nCustody Cols: "+attrbs['cusc']+" (Min: "+attrbs['mcusc']+")"+"\n"+nodeTypesTxt\
        +"\nSegment Size: "+str(self.config.segmentSize)
        conf["title"] = "ECDF of Messages Received by Nodes"
        conf["xlabel"] = "Number of Messages Received"
        conf["ylabel"] = "ECDF"
        nodeClasses, nodeRanges = self.__getNodeRanges(result.shape)
        start = 1
        labels = []
        for i, rng in enumerate(nodeRanges):
            class_data = result.msgRecvCount[start: rng + 1]
            label = f"Class {nodeClasses[i]} Nodes"
            labels.append(label)
            start = rng + 1
            sns.ecdfplot(data=class_data, label=label)
        plt.legend(title='Node Class', labels=labels)
        plt.xlabel(conf["xlabel"], fontsize=12)
        plt.ylabel(conf["ylabel"], fontsize=12)
        plt.title(conf["title"], fontsize=14)
        plt.xlim(left=0, right=max(result.msgRecvCount) * 1.1)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        plt.text(1.05, 0.05, conf["textBox"], fontsize=14, verticalalignment='bottom', transform=plt.gca().transAxes, bbox=props)
        plt.savefig(plotPath + "/ecdf_messagesRecv.png", bbox_inches="tight")
        print("Plot %s created." % (plotPath + "/ecdf_messagesRecv.png"))

    def plotECDFSamplesReceived(self, result, plotPath):
        """Plots the ECDF of samples received by all nodes using seaborn's ecdfplot"""
        plt.clf()
        conf = {}
        attrbs = self.__get_attrbs__(result)
        nodeTypes = self.__getNodeTypes__(attrbs['ntypes'])
        nodeTypesTxt = ""
        for _k, _v in nodeTypes.items():
            nodeTypesTxt += f"Type ({_k}): " + str(_v) + "\n"
        if nodeTypesTxt != "": nodeTypesTxt = nodeTypesTxt[: -1]
        conf["textBox"] = "Row Size (N, K): "+attrbs['bsrn']+ ", "+attrbs['bsrk']\
        +"\nColumn Size: (N, K): "+attrbs['bscn']+ ", "+attrbs['bsck']\
        +"\nNumber of nodes: "+attrbs['nn']+"\nFailure rate: "+attrbs['fr']+"%"+"\nMalicious Node: "+attrbs['mn']+"%"+"\nNetwork degree: "+attrbs['nd']\
        +"\nCustody Rows: "+attrbs['cusr']+" (Min: "+attrbs['mcusr']+")"+"\nCustody Cols: "+attrbs['cusc']+" (Min: "+attrbs['mcusc']+")"+"\n"+nodeTypesTxt\
        +"\nSegment Size: "+str(self.config.segmentSize)
        conf["title"] = "ECDF of Samples Received by Nodes"
        conf["xlabel"] = "Number of Samples Received"
        conf["ylabel"] = "ECDF"
        nodeClasses, nodeRanges = self.__getNodeRanges(result.shape)
        start = 1
        labels = []
        for i, rng in enumerate(nodeRanges):
            class_data = result.sampleRecvCount[start: rng + 1]
            label = f"Class {nodeClasses[i]} Nodes"
            labels.append(label)
            start = rng + 1
            sns.ecdfplot(data=class_data, label=label)
        plt.legend(title='Node Class', labels=labels)
        plt.xlabel(conf["xlabel"], fontsize=12)
        plt.ylabel(conf["ylabel"], fontsize=12)
        plt.title(conf["title"], fontsize=14)
        plt.xlim(left=0, right=max(result.sampleRecvCount) * 1.1)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        plt.text(1.05, 0.05, conf["textBox"], fontsize=14, verticalalignment='bottom', transform=plt.gca().transAxes, bbox=props)
        plt.savefig(plotPath + "/ecdf_samplesReceived.png", bbox_inches="tight")
        print("Plot %s created." % (plotPath + "/ecdf_samplesReceived.png"))

    def plotECDFRowColDist(self, result, plotPath):
        """Plots the ECDF of row col distribution by all nodes using seaborn's ecdfplot"""
        plt.clf()
        conf = {}
        attrbs = self.__get_attrbs__(result)
        nodeTypes = self.__getNodeTypes__(attrbs['ntypes'])
        nodeTypesTxt = ""
        for _k, _v in nodeTypes.items():
            nodeTypesTxt += f"Type ({_k}): " + str(_v) + "\n"
        if nodeTypesTxt != "": nodeTypesTxt = nodeTypesTxt[: -1]
        conf["textBox"] = "Row Size (N, K): "+attrbs['bsrn']+ ", "+attrbs['bsrk']\
        +"\nColumn Size: (N, K): "+attrbs['bscn']+ ", "+attrbs['bsck']\
        +"\nNumber of nodes: "+attrbs['nn']+"\nFailure rate: "+attrbs['fr']+"%"+"\nMalicious Node: "+attrbs['mn']+"%"+"\nNetwork degree: "+attrbs['nd']\
        +"\nCustody Rows: "+attrbs['cusr']+" (Min: "+attrbs['mcusr']+")"+"\nCustody Cols: "+attrbs['cusc']+" (Min: "+attrbs['mcusc']+")"+"\n"+nodeTypesTxt\
        +"\nSegment Size: "+str(self.config.segmentSize)
        conf["title"] = "ECDF of Row-Col Distribution by Nodes"
        conf["xlabel"] = "Row-Col Distribution"
        conf["ylabel"] = "ECDF"
        vector1 = result.metrics["rowDist"]
        vector2 = result.metrics["columnDist"]
        sns.ecdfplot(data=vector1, label='Rows')
        sns.ecdfplot(data=vector2, label='Columns')
        plt.xlabel(conf["xlabel"], fontsize=12)
        plt.ylabel(conf["ylabel"], fontsize=12)
        plt.title(conf["title"], fontsize=14)
        plt.xlim(left=0, right=max(max(vector1), max(vector2)) * 1.1)
        plt.legend(labels=['Row Dist', 'Column Dist'], loc=1)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        plt.text(1.05, 0.05, conf["textBox"], fontsize=14, verticalalignment='bottom', transform=plt.gca().transAxes, bbox=props)
        plt.savefig(plotPath + "/ecdf_rowColDist.png", bbox_inches="tight")
        print("Plot %s created." % (plotPath + "/ecdf_rowColDist.png"))

    def plotECDFSamplesRepaired(self, result, plotPath):
        """Plots the ECDF of samples repaired by all nodes using seaborn's ecdfplot"""
        plt.clf()
        conf = {}
        attrbs = self.__get_attrbs__(result)
        nodeTypes = self.__getNodeTypes__(attrbs['ntypes'])
        nodeTypesTxt = ""
        for _k, _v in nodeTypes.items():
            nodeTypesTxt += f"Type ({_k}): " + str(_v) + "\n"
        if nodeTypesTxt != "": nodeTypesTxt = nodeTypesTxt[: -1]
        conf["textBox"] = "Row Size (N, K): "+attrbs['bsrn']+ ", "+attrbs['bsrk']\
        +"\nColumn Size: (N, K): "+attrbs['bscn']+ ", "+attrbs['bsck']\
        +"\nNumber of nodes: "+attrbs['nn']+"\nFailure rate: "+attrbs['fr']+"%"+"\nMalicious Node: "+attrbs['mn']+"%"+"\nNetwork degree: "+attrbs['nd']\
        +"\nCustody Rows: "+attrbs['cusr']+" (Min: "+attrbs['mcusr']+")"+"\nCustody Cols: "+attrbs['cusc']+" (Min: "+attrbs['mcusc']+")"+"\n"+nodeTypesTxt\
        +"\nSegment Size: "+str(self.config.segmentSize)
        conf["title"] = "ECDF of Samples Repaired by Nodes"
        conf["xlabel"] = "Number of Samples Repaired"
        conf["ylabel"] = "ECDF"
        nodeClasses, nodeRanges = self.__getNodeRanges(result.shape)
        start = 1
        labels = []
        for i, rng in enumerate(nodeRanges):
            class_data = result.repairedSampleCount[start: rng + 1]
            label = f"Class {nodeClasses[i]} Nodes"
            labels.append(label)
            start = rng + 1
            sns.ecdfplot(data=class_data, label=label)
        plt.legend(title='Node Class', labels=labels)
        plt.xlabel(conf["xlabel"], fontsize=12)
        plt.ylabel(conf["ylabel"], fontsize=12)
        plt.title(conf["title"], fontsize=14)
        plt.xlim(left=0, right=max(result.repairedSampleCount) * 1.1)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        plt.text(1.05, 0.05, conf["textBox"], fontsize=14, verticalalignment='bottom', transform=plt.gca().transAxes, bbox=props)
        plt.savefig(plotPath + "/ecdf_samplesRepaired.png", bbox_inches="tight")
        print("Plot %s created." % (plotPath + "/ecdf_samplesRepaired.png"))
    
    def plotBoxenSamplesRecv(self, result, plotPath):
        """Boxen Plot of the number of samples received by all nodes"""
        plt.clf()
        conf = {}
        attrbs = self.__get_attrbs__(result)
        nodeTypes = self.__getNodeTypes__(attrbs['ntypes'])
        nodeTypesTxt = ""
        for _k, _v in nodeTypes.items():
            nodeTypesTxt += f"Type ({_k}): " + str(_v) + "\n"
        if nodeTypesTxt != "": nodeTypesTxt = nodeTypesTxt[: -1]
        conf["textBox"] = "Row Size (N, K): "+attrbs['bsrn']+ ", "+attrbs['bsrk']\
        +"\nColumn Size: (N, K): "+attrbs['bscn']+ ", "+attrbs['bsck']\
        +"\nNumber of nodes: "+attrbs['nn']+"\nFailure rate: "+attrbs['fr']+"%"+"\nMalicious Node: "+attrbs['mn']+"%"+"\nNetwork degree: "+attrbs['nd']\
        +"\nCustody Rows: "+attrbs['cusr']+" (Min: "+attrbs['mcusr']+")"+"\nCustody Cols: "+attrbs['cusc']+" (Min: "+attrbs['mcusc']+")"+"\n"+nodeTypesTxt\
        +"\nSegment Size: "+str(self.config.segmentSize)
        conf["title"] = "Number of Samples Received by Nodes"
        conf["xlabel"] = "Node Type"
        conf["ylabel"] = "Number of Samples Received"
        data = []
        nodeClasses, nodeRanges = self.__getNodeRanges(result.shape)
        _start = 1
        for _range in nodeRanges:
            data.append(result.sampleRecvCount[_start: _range])
            _start = _range
        _values, _categories = [], []
        for _d, _nc in zip(data, nodeClasses):
            _values += _d
            _categories += [f'Class {_nc}'] * len(_d)
        data = pd.DataFrame({
            'values': _values,
            'category': _categories
        })
        plt.figure(figsize=(8, 6))
        sns.boxenplot(x='category', y='values', hue='category', data=data, palette="Set2", ax=plt.gca(), width=0.8)
        plt.xlabel(conf["xlabel"], fontsize=12)
        plt.ylabel(conf["ylabel"], fontsize=12)
        plt.title(conf["title"], fontsize=14)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        plt.text(1.05, 0.05, conf["textBox"], fontsize=14, verticalalignment='bottom', transform=plt.gca().transAxes, bbox=props)
        plt.tight_layout()
        plt.savefig(plotPath + "/boxen_samplesRecv.png")
        plt.close()
        print("Plot %s created." % (plotPath + "/boxen_samplesRecv.png"))

    def plotBoxenSamplesRepaired(self, result, plotPath):
        """Boxen Plot of the number of samples repaired by all nodes"""
        plt.clf()
        conf = {}
        attrbs = self.__get_attrbs__(result)
        nodeTypes = self.__getNodeTypes__(attrbs['ntypes'])
        nodeTypesTxt = ""
        for _k, _v in nodeTypes.items():
            nodeTypesTxt += f"Type ({_k}): " + str(_v) + "\n"
        if nodeTypesTxt != "": nodeTypesTxt = nodeTypesTxt[: -1]
        conf["textBox"] = "Row Size (N, K): "+attrbs['bsrn']+ ", "+attrbs['bsrk']\
        +"\nColumn Size: (N, K): "+attrbs['bscn']+ ", "+attrbs['bsck']\
        +"\nNumber of nodes: "+attrbs['nn']+"\nFailure rate: "+attrbs['fr']+"%"+"\nMalicious Node: "+attrbs['mn']+"%"+"\nNetwork degree: "+attrbs['nd']\
        +"\nCustody Rows: "+attrbs['cusr']+" (Min: "+attrbs['mcusr']+")"+"\nCustody Cols: "+attrbs['cusc']+" (Min: "+attrbs['mcusc']+")"+"\n"+nodeTypesTxt\
        +"\nSegment Size: "+str(self.config.segmentSize)
        conf["title"] = "Number of Samples Repaired by Nodes"
        conf["xlabel"] = "Node Type"
        conf["ylabel"] = "Number of Samples Repaired"
        data = []
        nodeClasses, nodeRanges = self.__getNodeRanges(result.shape)
        _start = 1
        for _range in nodeRanges:
            data.append(result.repairedSampleCount[_start: _range])
            _start = _range
        _values, _categories = [], []
        for _d, _nc in zip(data, nodeClasses):
            _values += _d
            _categories += [f'Class {_nc}'] * len(_d)
        data = pd.DataFrame({
            'values': _values,
            'category': _categories
        })
        plt.figure(figsize=(8, 6))
        sns.boxenplot(x='category', y='values', hue='category', data=data, width=0.8, palette="Set2", ax=plt.gca())
        plt.xlabel(conf["xlabel"], fontsize=12)
        plt.ylabel(conf["ylabel"], fontsize=12)
        plt.title(conf["title"], fontsize=14)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        plt.text(1.05, 0.05, conf["textBox"], fontsize=14, verticalalignment='bottom', transform=plt.gca().transAxes, bbox=props)
        plt.tight_layout()
        plt.savefig(plotPath + "/boxen_samplesRepaired.png")
        plt.close()
        print("Plot %s created." % (plotPath + "/boxen_samplesRepaired.png"))

    def plotBoxenRowColDist(self, result, plotPath):
        """Boxen Plot of the Row/Column distribution"""
        plt.clf()
        conf = {}
        attrbs = self.__get_attrbs__(result)
        nodeTypes = self.__getNodeTypes__(attrbs['ntypes'])
        nodeTypesTxt = ""
        for _k, _v in nodeTypes.items():
            nodeTypesTxt += f"Type ({_k}): " + str(_v) + "\n"
        if nodeTypesTxt != "": nodeTypesTxt = nodeTypesTxt[: -1]
        conf["textBox"] = "Row Size (N, K): "+attrbs['bsrn']+ ", "+attrbs['bsrk']\
        +"\nColumn Size: (N, K): "+attrbs['bscn']+ ", "+attrbs['bsck']\
        +"\nNumber of nodes: "+attrbs['nn']+"\nFailure rate: "+attrbs['fr']+"%"+"\nMalicious Node: "+attrbs['mn']+"%"+"\nNetwork degree: "+attrbs['nd']\
        +"\nCustody Rows: "+attrbs['cusr']+" (Min: "+attrbs['mcusr']+")"+"\nCustody Cols: "+attrbs['cusc']+" (Min: "+attrbs['mcusc']+")"+"\n"+nodeTypesTxt\
        +"\nSegment Size: "+str(self.config.segmentSize)
        conf["title"] = "Row/Column Distribution"
        conf["xlabel"] = "Row/Column Type"
        conf["ylabel"] = "Validators Subscribed"
        vector1 = result.metrics["rowDist"]
        vector2 = result.metrics["columnDist"]
        if len(vector1) > len(vector2):
            vector2 += [np.nan] * (len(vector1) - len(vector2))
        elif len(vector1) < len(vector2):
            vector1 += [np.nan] * (len(vector2) - len(vector1))
        data = [vector1, vector2]
        plt.figure(figsize=(8, 6))
        sns.boxenplot(data=data, width=0.8)
        plt.xlabel(conf["xlabel"], fontsize=12)
        plt.ylabel(conf["ylabel"], fontsize=12)
        plt.title(conf["title"], fontsize=14)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        plt.text(1.05, 0.05, conf["textBox"], fontsize=14, verticalalignment='bottom', transform=plt.gca().transAxes, bbox=props)
        plt.tight_layout()
        plt.savefig(plotPath + "/boxen_rowColDist.png")
        plt.close()
        print("Plot %s created." % (plotPath + "/boxen_rowColDist.png"))
        
    def plotBoxenMessagesSent(self, result, plotPath):
        """Plots the number of messages sent by all nodes using seaborn's boxenplot"""
        plt.clf()
        conf = {}
        attrbs = self.__get_attrbs__(result)
        nodeTypes = self.__getNodeTypes__(attrbs['ntypes'])
        nodeTypesTxt = ""
        for _k, _v in nodeTypes.items():
            nodeTypesTxt += f"Type ({_k}): " + str(_v) + "\n"
        if nodeTypesTxt != "": nodeTypesTxt = nodeTypesTxt[: -1]
        conf["textBox"] = "Row Size (N, K): "+attrbs['bsrn']+ ", "+attrbs['bsrk']\
        +"\nColumn Size: (N, K): "+attrbs['bscn']+ ", "+attrbs['bsck']\
        +"\nNumber of nodes: "+attrbs['nn']+"\nFailure rate: "+attrbs['fr']+"%"+"\nMalicious Node: "+attrbs['mn']+"%"+"\nNetwork degree: "+attrbs['nd']\
        +"\nCustody Rows: "+attrbs['cusr']+" (Min: "+attrbs['mcusr']+")"+"\nCustody Cols: "+attrbs['cusc']+" (Min: "+attrbs['mcusc']+")"+"\n"+nodeTypesTxt\
        +"\nSegment Size: "+str(self.config.segmentSize)
        conf["title"] = "Number of Messages Sent by Nodes"
        conf["xlabel"] = "Node Type"
        conf["ylabel"] = "Number of Messages Sent"
        data = []
        nodeClasses, nodeRanges = self.__getNodeRanges(result.shape)
        _start = 1
        for _range in nodeRanges:
            data.append(result.msgSentCount[_start: _range])
            _start = _range
        _values, _categories = [], []
        for _d, _nc in zip(data, nodeClasses):
            _values += _d
            _categories += [f'Class {_nc}'] * len(_d)
        data = pd.DataFrame({
            'values': _values,
            'category': _categories
        })
        sns.boxenplot(x='category', y='values', hue='category', data=data, width=0.8, palette="Set2", ax=plt.gca())
        plt.xlabel(conf["xlabel"], fontsize=12)
        plt.ylabel(conf["ylabel"], fontsize=12)
        plt.title(conf["title"], fontsize=14)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        plt.text(1.05, 0.05, conf["textBox"], fontsize=14, verticalalignment='bottom', transform=plt.gca().transAxes, bbox=props)
        plt.savefig(plotPath + "/boxen_messagesSent.png", bbox_inches="tight")
        print("Plot %s created." % (plotPath + "/boxen_messagesSent.png"))

    def plotBoxenMessagesRecv(self, result, plotPath):
        """Plots the number of messages received by all nodes using seaborn's boxenplot"""
        plt.clf()
        conf = {}
        attrbs = self.__get_attrbs__(result)
        nodeTypes = self.__getNodeTypes__(attrbs['ntypes'])
        nodeTypesTxt = ""
        for _k, _v in nodeTypes.items():
            nodeTypesTxt += f"Type ({_k}): " + str(_v) + "\n"
        if nodeTypesTxt != "": nodeTypesTxt = nodeTypesTxt[: -1]
        conf["textBox"] = "Row Size (N, K): "+attrbs['bsrn']+ ", "+attrbs['bsrk']\
        +"\nColumn Size: (N, K): "+attrbs['bscn']+ ", "+attrbs['bsck']\
        +"\nNumber of nodes: "+attrbs['nn']+"\nFailure rate: "+attrbs['fr']+"%"+"\nMalicious Node: "+attrbs['mn']+"%"+"\nNetwork degree: "+attrbs['nd']\
        +"\nCustody Rows: "+attrbs['cusr']+" (Min: "+attrbs['mcusr']+")"+"\nCustody Cols: "+attrbs['cusc']+" (Min: "+attrbs['mcusc']+")"+"\n"+nodeTypesTxt\
        +"\nSegment Size: "+str(self.config.segmentSize)
        conf["title"] = "Number of Messages Received by Nodes"
        conf["xlabel"] = "Node Type"
        conf["ylabel"] = "Number of Messages Received"
        data = []
        nodeClasses, nodeRanges = self.__getNodeRanges(result.shape)
        _start = 1
        for _range in nodeRanges:
            data.append(result.msgRecvCount[_start: _range])
            _start = _range
        _values, _categories = [], []
        for _d, _nc in zip(data, nodeClasses):
            _values += _d
            _categories += [f'Class {_nc}'] * len(_d)
        data = pd.DataFrame({
            'values': _values,
            'category': _categories
        })
        sns.boxenplot(x='category', y='values', hue='category', data=data, palette="Set2", ax=plt.gca())
        plt.xlabel(conf["xlabel"], fontsize=12)
        plt.ylabel(conf["ylabel"], fontsize=12)
        plt.title(conf["title"], fontsize=14)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        plt.text(1.05, 0.05, conf["textBox"], fontsize=14, verticalalignment='bottom', transform=plt.gca().transAxes, bbox=props)
        plt.savefig(plotPath + "/boxen_messagesRecv.png", bbox_inches="tight")
        print("Plot %s created." % (plotPath + "/boxen_messagesRecv.png"))
    
    def plotBoxSamplesRepaired(self, result, plotPath):
        """Box Plot of the number of samples repaired by all nodes"""
        plt.clf()
        conf = {}
        attrbs = self.__get_attrbs__(result)
        nodeTypes = self.__getNodeTypes__(attrbs['ntypes'])
        nodeTypesTxt = ""
        for _k, _v in nodeTypes.items():
            nodeTypesTxt += f"Type ({_k}): " + str(_v) + "\n"
        if nodeTypesTxt != "": nodeTypesTxt = nodeTypesTxt[: -1]
        conf["textBox"] = "Row Size (N, K): "+attrbs['bsrn']+ ", "+attrbs['bsrk']\
        +"\nColumn Size: (N, K): "+attrbs['bscn']+ ", "+attrbs['bsck']\
        +"\nNumber of nodes: "+attrbs['nn']+"\nFailure rate: "+attrbs['fr']+"%"+"\nMalicious Node: "+attrbs['mn']+"%"+"\nNetwork degree: "+attrbs['nd']\
        +"\nCustody Rows: "+attrbs['cusr']+" (Min: "+attrbs['mcusr']+")"+"\nCustody Cols: "+attrbs['cusc']+" (Min: "+attrbs['mcusc']+")"+"\n"+nodeTypesTxt\
        +"\nSegment Size: "+str(self.config.segmentSize)
        conf["title"] = "Number of Samples Repaired by Nodes"
        conf["type"] = "individual_bar"
        conf["legLoc"] = 1
        conf["desLoc"] = 1
        conf["xlabel"] = "Node Type"
        conf["ylabel"] = "Number of Samples Repaired"
        n1 = int(result.numberNodes * result.class1ratio)
        conf["data"] = [result.repairedSampleCount[1: n1], result.repairedSampleCount[n1+1: ]]
        conf["path"] = plotPath + "/box_samplesRepaired.png"
        plotBoxData(conf)
        print("Plot %s created." % conf["path"])
    
    def plotBoxRowCol(self, result, plotPath):
        """Box Plot of the Row/Column distribution"""
        plt.clf()
        conf = {}
        attrbs = self.__get_attrbs__(result)
        nodeTypes = self.__getNodeTypes__(attrbs['ntypes'])
        nodeTypesTxt = ""
        for _k, _v in nodeTypes.items():
            nodeTypesTxt += f"Type ({_k}): " + str(_v) + "\n"
        if nodeTypesTxt != "": nodeTypesTxt = nodeTypesTxt[: -1]
        conf["textBox"] = "Row Size (N, K): "+attrbs['bsrn']+ ", "+attrbs['bsrk']\
        +"\nColumn Size: (N, K): "+attrbs['bscn']+ ", "+attrbs['bsck']\
        +"\nNumber of nodes: "+attrbs['nn']+"\nFailure rate: "+attrbs['fr']+"%"+"\nMalicious Node: "+attrbs['mn']+"%"+"\nNetwork degree: "+attrbs['nd']\
        +"\nCustody Rows: "+attrbs['cusr']+" (Min: "+attrbs['mcusr']+")"+"\nCustody Cols: "+attrbs['cusc']+" (Min: "+attrbs['mcusc']+")"+"\n"+nodeTypesTxt\
        +"\nSegment Size: "+str(self.config.segmentSize)
        conf["title"] = "Row/Column Distribution"
        conf["xlabel"] = ""
        conf["ylabel"] = "Validators Subscribed"
        vector1 = result.metrics["rowDist"]
        vector2 = result.metrics["columnDist"]
        if len(vector1) > len(vector2):
            vector2 += [np.nan] * (len(vector1) - len(vector2))
        elif len(vector1) < len(vector2):
            vector1 += [np.nan] * (len(vector2) - len(vector1))
        n1 = int(result.numberNodes * result.class1ratio)
        conf["data"] = [vector1, vector2]
        conf["path"] = plotPath + "/box_rowColDist.png"
        plotBoxData(conf)
        print("Plot %s created." % conf["path"])

    def plotRestoreRowCount(self, result, plotPath):
        """Plots the restoreRowCount for each node"""
        conf = {}
        attrbs = self.__get_attrbs__(result)
        nodeTypes = self.__getNodeTypes__(attrbs['ntypes'])
        nodeTypesTxt = ""
        for _k, _v in nodeTypes.items():
            nodeTypesTxt += f"Type ({_k}): " + str(_v) + "\n"
        if nodeTypesTxt != "": nodeTypesTxt = nodeTypesTxt[: -1]
        conf["textBox"] = "Row Size (N, K): "+attrbs['bsrn']+ ", "+attrbs['bsrk']\
        +"\nColumn Size: (N, K): "+attrbs['bscn']+ ", "+attrbs['bsck']\
        +"\nNumber of nodes: "+attrbs['nn']+"\nFailure rate: "+attrbs['fr']+"%"+"\nMalicious Node: "+attrbs['mn']+"%"+"\nNetwork degree: "+attrbs['nd']\
        +"\nCustody Rows: "+attrbs['cusr']+" (Min: "+attrbs['mcusr']+")"+"\nCustody Cols: "+attrbs['cusc']+" (Min: "+attrbs['mcusc']+")"+"\n"+nodeTypesTxt\
        +"\nSegment Size: "+str(self.config.segmentSize)
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
        attrbs = self.__get_attrbs__(result)
        nodeTypes = self.__getNodeTypes__(attrbs['ntypes'])
        nodeTypesTxt = ""
        for _k, _v in nodeTypes.items():
            nodeTypesTxt += f"Type ({_k}): " + str(_v) + "\n"
        if nodeTypesTxt != "": nodeTypesTxt = nodeTypesTxt[: -1]
        conf["textBox"] = "Row Size (N, K): "+attrbs['bsrn']+ ", "+attrbs['bsrk']\
        +"\nColumn Size: (N, K): "+attrbs['bscn']+ ", "+attrbs['bsck']\
        +"\nNumber of nodes: "+attrbs['nn']+"\nFailure rate: "+attrbs['fr']+"%"+"\nMalicious Node: "+attrbs['mn']+"%"+"\nNetwork degree: "+attrbs['nd']\
        +"\nCustody Rows: "+attrbs['cusr']+" (Min: "+attrbs['mcusr']+")"+"\nCustody Cols: "+attrbs['cusc']+" (Min: "+attrbs['mcusc']+")"+"\n"+nodeTypesTxt\
        +"\nSegment Size: "+str(self.config.segmentSize)
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
        attrbs = self.__get_attrbs__(result)
        nodeTypes = self.__getNodeTypes__(attrbs['ntypes'])
        nodeTypesTxt = ""
        for _k, _v in nodeTypes.items():
            nodeTypesTxt += f"Type ({_k}): " + str(_v) + "\n"
        if nodeTypesTxt != "": nodeTypesTxt = nodeTypesTxt[: -1]
        conf["textBox"] = "Row Size (N, K): "+attrbs['bsrn']+ ", "+attrbs['bsrk']\
        +"\nColumn Size: (N, K): "+attrbs['bscn']+ ", "+attrbs['bsck']\
        +"\nNumber of nodes: "+attrbs['nn']+"\nFailure rate: "+attrbs['fr']+"%"+"\nMalicious Node: "+attrbs['mn']+"%"+"\nNetwork degree: "+attrbs['nd']\
        +"\nCustody Rows: "+attrbs['cusr']+" (Min: "+attrbs['mcusr']+")"+"\nCustody Cols: "+attrbs['cusc']+" (Min: "+attrbs['mcusc']+")"+"\n"+nodeTypesTxt\
        +"\nSegment Size: "+str(self.config.segmentSize)
        conf["title"] = "Percentage of Samples Received by Nodes"
        conf["type"] = "individual_bar_with_2line"
        conf["legLoc"] = 1
        conf["desLoc"] = 1
        conf["xlabel"] = "Nodes"
        conf["ylabel"] = "Percentage of samples received (%)"
        total_samples = result.shape.nbCols * result.shape.nbRows
        percentage_data = [(count / total_samples) * 100 for count in result.sampleRecvCount]
        conf["data"] = percentage_data
        conf["xdots"] = range(result.shape.numberNodes)
        conf["path"] = plotPath + "/sampleRecv.png"
        maxi = max(conf["data"])
        # conf["yaxismax"] = maxi * 1.1
        expected_percentage1 = (result.shape.vpn1 * (result.shape.nbCols * result.shape.custodyRows + result.shape.nbRows * result.shape.custodyCols) * 100)/total_samples
        expected_percentage2 = (result.shape.vpn2 * (result.shape.nbCols * result.shape.custodyRows + result.shape.nbRows * result.shape.custodyCols) * 100)/total_samples
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
        attrbs = self.__get_attrbs__(result)
        nodeTypes = self.__getNodeTypes__(attrbs['ntypes'])
        nodeTypesTxt = ""
        for _k, _v in nodeTypes.items():
            nodeTypesTxt += f"Type ({_k}): " + str(_v) + "\n"
        if nodeTypesTxt != "": nodeTypesTxt = nodeTypesTxt[: -1]
        conf["textBox"] = "Row Size (N, K): "+attrbs['bsrn']+ ", "+attrbs['bsrk']\
        +"\nColumn Size: (N, K): "+attrbs['bscn']+ ", "+attrbs['bsck']\
        +"\nNumber of nodes: "+attrbs['nn']+"\nFailure rate: "+attrbs['fr']+"%"+"\nMalicious Node: "+attrbs['mn']+"%"+"\nNetwork degree: "+attrbs['nd']\
        +"\nCustody Rows: "+attrbs['cusr']+" (Min: "+attrbs['mcusr']+")"+"\nCustody Cols: "+attrbs['cusc']+" (Min: "+attrbs['mcusc']+")"+"\n"+nodeTypesTxt\
        +"\nSegment Size: "+str(self.config.segmentSize)
        conf["title"] = "Number of Samples Received by Nodes"
        conf["type"] = "individual_bar_with_2line"
        conf["legLoc"] = 1
        conf["desLoc"] = 1
        conf["xlabel"] = "Node Type"
        conf["ylabel"] = "Number of samples received (%)"
        n1 = int(result.numberNodes * result.class1ratio)
        conf["data"] = [result.sampleRecvCount[1: n1], result.sampleRecvCount[n1+1: ]]
        conf["xdots"] = range(result.shape.numberNodes)
        conf["path"] = plotPath + "/box_sampleRecv.png"
        plotBoxData(conf)
        print("Plot %s created." % conf["path"])
    
    def plotMissingSegments(self, result, plotPath):
        """Plots the missing segments in the network"""
        conf = {}
        attrbs = self.__get_attrbs__(result)
        nodeTypes = self.__getNodeTypes__(attrbs['ntypes'])
        nodeTypesTxt = ""
        for _k, _v in nodeTypes.items():
            nodeTypesTxt += f"Type ({_k}): " + str(_v) + "\n"
        if nodeTypesTxt != "": nodeTypesTxt = nodeTypesTxt[: -1]
        conf["textBox"] = "Row Size (N, K): "+attrbs['bsrn']+ ", "+attrbs['bsrk']\
        +"\nColumn Size: (N, K): "+attrbs['bscn']+ ", "+attrbs['bsck']\
        +"\nNumber of nodes: "+attrbs['nn']+"\nFailure rate: "+attrbs['fr']+"%"+"\nMalicious Node: "+attrbs['mn']+"%"+"\nNetwork degree: "+attrbs['nd']\
        +"\nCustody Rows: "+attrbs['cusr']+" (Min: "+attrbs['mcusr']+")"+"\nCustody Cols: "+attrbs['cusc']+" (Min: "+attrbs['mcusc']+")"+"\n"+nodeTypesTxt\
        +"\nSegment Size: "+str(self.config.segmentSize)+"\nMissing Segment: "+str(round(min(result.missingVector) * 100 / max(result.missingVector), 3))+"%"\
        +"\nMissing Segments: "+str(result.missingVector[-1])
        conf["title"] = "Missing Segments"
        conf["type"] = "plot_with_1line"
        conf["legLoc"] = 1
        conf["desLoc"] = 1
        conf["colors"] = ["m-"]
        conf["labels"] = ["Missing Segments"]
        conf["xlabel"] = "Time (ms)"
        conf["ylabel"] = "Number of Missing Segments"
        conf["data"] = [result.missingVector]
        conf["xdots"] = [x*self.config.stepDuration for x in range(len(result.missingVector))]
        conf["path"] = plotPath+"/missingSegments.png"
        maxi = 0
        for v in conf["data"]:
            if max(v) > maxi:
                maxi = max(v)
        conf["yaxismax"] = maxi
        x = result.shape.nbCols * result.shape.custodyRows + result.shape.nbRows * result.shape.custodyCols
        conf["expected_value"] = (result.shape.numberNodes - 1) * x * sum([(_v['w'] * _v['vpn']) for _v in nodeTypes.values()]) / sum([_v['w'] for _v in nodeTypes.values()])
        conf["line_label"] = "Total segments to deliver"
        plotData(conf)
        print("Plot %s created." % conf["path"])

    def plotProgress(self, result, plotPath):
        """Plots the percentage of nodes ready in the network"""
        vector1 = [x * 100 for x in result.metrics["progress"]["nodes ready"]]
        vector2 = [x * 100 for x in result.metrics["progress"]["validators ready"]]
        vector3 = [x * 100 for x in result.metrics["progress"]["samples received"]]   
        conf = {}
        attrbs = self.__get_attrbs__(result)
        nodeTypes = self.__getNodeTypes__(attrbs['ntypes'])
        nodeTypesTxt = ""
        for _k, _v in nodeTypes.items():
            nodeTypesTxt += f"Type ({_k}): " + str(_v) + "\n"
        if nodeTypesTxt != "": nodeTypesTxt = nodeTypesTxt[: -1]
        conf["textBox"] = "Row Size (N, K): "+attrbs['bsrn']+ ", "+attrbs['bsrk']\
        +"\nColumn Size: (N, K): "+attrbs['bscn']+ ", "+attrbs['bsck']\
        +"\nNumber of nodes: "+attrbs['nn']+"\nFailure rate: "+attrbs['fr']+"%"+"\nMalicious Node: "+attrbs['mn']+"%"+"\nNetwork degree: "+attrbs['nd']\
        +"\nCustody Rows: "+attrbs['cusr']+" (Min: "+attrbs['mcusr']+")"+"\nCustody Cols: "+attrbs['cusc']+" (Min: "+attrbs['mcusc']+")"+"\n"+nodeTypesTxt\
        +"\nSegment Size: "+str(self.config.segmentSize)
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
        conf["yaxismax"] = 1
        plotData(conf)
        print("Plot %s created." % conf["path"])

    def plotSentData(self, result, plotPath):
        """Plots the percentage of nodes ready in the network"""
        vectors = { 0: result.metrics["progress"]["TX builder mean"] }
        for nc in result.shape.nodeClasses:
            if nc != 0: vectors[nc] = result.metrics["progress"][f"TX class{nc} mean"]
        for _k in vectors.keys():
            for i in range(len(list(vectors.values())[0])):
                vectors[_k][i] = (vectors[_k][i] * 8 * (1000/self.config.stepDuration) * self.config.segmentSize) / 1000000
        conf = {}
        attrbs = self.__get_attrbs__(result)
        nodeTypes = self.__getNodeTypes__(attrbs['ntypes'])
        nodeTypesTxt = ""
        for _k, _v in nodeTypes.items():
            nodeTypesTxt += f"Type ({_k}): " + str(_v) + "\n"
        if nodeTypesTxt != "": nodeTypesTxt = nodeTypesTxt[: -1]
        conf["textBox"] = "Row Size (N, K): "+attrbs['bsrn']+ ", "+attrbs['bsrk']\
        +"\nColumn Size: (N, K): "+attrbs['bscn']+ ", "+attrbs['bsck']\
        +"\nNumber of nodes: "+attrbs['nn']+"\nFailure rate: "+attrbs['fr']+"%"+"\nMalicious Node: "+attrbs['mn']+"%"+"\nNetwork degree: "+attrbs['nd']\
        +"\nCustody Rows: "+attrbs['cusr']+" (Min: "+attrbs['mcusr']+")"+"\nCustody Cols: "+attrbs['cusc']+" (Min: "+attrbs['mcusc']+")"+"\n"+nodeTypesTxt\
        +"\nSegment Size: "+str(self.config.segmentSize)
        conf["title"] = "Sent data"
        conf["type"] = "plot"
        conf["legLoc"] = 2
        conf["desLoc"] = 2
        # conf["colors"] = ["y-", "c-", "m-"]
        conf["labels"] = ["Block Builder"]
        conf["data"] = [vectors[0]]
        for _k, _v in vectors.items():
            if _k != 0:
                conf["labels"].append(f"Node Class: {_k}")
                conf["data"].append(_v)
        conf["xlabel"] = "Time (ms)"
        conf["ylabel"] = "Bandwidth (MBits/s)"
        conf["xdots"] = [x*self.config.stepDuration for x in range(len(list(vectors.values())[0]))]
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
        vectors = {}
        for nc in result.shape.nodeClasses:
            if nc != 0: vectors[nc] = result.metrics["progress"][f"RX class{nc} mean"]
        for _k in vectors.keys():
            for i in range(len(list(vectors.values())[0])):
                vectors[_k][i] = (vectors[_k][i] * 8 * (1000/self.config.stepDuration) * self.config.segmentSize) / 1000000
        conf = {}
        attrbs = self.__get_attrbs__(result)
        nodeTypes = self.__getNodeTypes__(attrbs['ntypes'])
        nodeTypesTxt = ""
        for _k, _v in nodeTypes.items():
            nodeTypesTxt += f"Type ({_k}): " + str(_v) + "\n"
        if nodeTypesTxt != "": nodeTypesTxt = nodeTypesTxt[: -1]
        conf["textBox"] = "Row Size (N, K): "+attrbs['bsrn']+ ", "+attrbs['bsrk']\
        +"\nColumn Size: (N, K): "+attrbs['bscn']+ ", "+attrbs['bsck']\
        +"\nNumber of nodes: "+attrbs['nn']+"\nFailure rate: "+attrbs['fr']+"%"+"\nMalicious Node: "+attrbs['mn']+"%"+"\nNetwork degree: "+attrbs['nd']\
        +"\nCustody Rows: "+attrbs['cusr']+" (Min: "+attrbs['mcusr']+")"+"\nCustody Cols: "+attrbs['cusc']+" (Min: "+attrbs['mcusc']+")"+"\n"+nodeTypesTxt\
        +"\nSegment Size: "+str(self.config.segmentSize)
        conf["title"] = "Received data"
        conf["type"] = "plot"
        conf["legLoc"] = 2
        conf["desLoc"] = 2
        # conf["colors"] = ["c-", "m-"]
        conf["labels"] = []
        conf["data"] = []
        for _k, _v in vectors.items():
            conf["labels"].append(f"Node Class: {_k}")
            conf["data"].append(_v)
        conf["xlabel"] = "Time (ms)"
        conf["ylabel"] = "Bandwidth (MBits/s)"
        conf["xdots"] = [x*self.config.stepDuration for x in range(len(list(vectors.values())[0]))]
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
        vectors = {}
        for nc in result.shape.nodeClasses:
            if nc != 0: vectors[nc] = result.metrics["progress"][f"Dup class{nc} mean"]
        for _k in vectors.keys():
            for i in range(len(list(vectors.values())[0])):
                vectors[_k][i] = (vectors[_k][i] * 8 * (1000/self.config.stepDuration) * self.config.segmentSize) / 1000000
        conf = {}
        attrbs = self.__get_attrbs__(result)
        nodeTypes = self.__getNodeTypes__(attrbs['ntypes'])
        nodeTypesTxt = ""
        for _k, _v in nodeTypes.items():
            nodeTypesTxt += f"Type ({_k}): " + str(_v) + "\n"
        if nodeTypesTxt != "": nodeTypesTxt = nodeTypesTxt[: -1]
        conf["textBox"] = "Row Size (N, K): "+attrbs['bsrn']+ ", "+attrbs['bsrk']\
        +"\nColumn Size: (N, K): "+attrbs['bscn']+ ", "+attrbs['bsck']\
        +"\nNumber of nodes: "+attrbs['nn']+"\nFailure rate: "+attrbs['fr']+"%"+"\nMalicious Node: "+attrbs['mn']+"%"+"\nNetwork degree: "+attrbs['nd']\
        +"\nCustody Rows: "+attrbs['cusr']+" (Min: "+attrbs['mcusr']+")"+"\nCustody Cols: "+attrbs['cusc']+" (Min: "+attrbs['mcusc']+")"+"\n"+nodeTypesTxt\
        +"\nSegment Size: "+str(self.config.segmentSize)
        conf["title"] = "Duplicated data"
        conf["type"] = "plot"
        conf["legLoc"] = 2
        conf["desLoc"] = 2
        # conf["colors"] = ["c-", "m-"]
        conf["labels"] = []
        conf["data"] = []
        for _k, _v in vectors.items():
            conf["labels"].append(f"Node Class: {_k}")
            conf["data"].append(_v)
        conf["xlabel"] = "Time (ms)"
        conf["ylabel"] = "Bandwidth (MBits/s)"
        conf["xdots"] = [x*self.config.stepDuration for x in range(len(list(vectors.values())[0]))]
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
        nodeTypes = self.__getNodeTypes__(attrbs['ntypes'])
        nodeTypesTxt = ""
        for _k, _v in nodeTypes.items():
            nodeTypesTxt += f"Type ({_k}): " + str(_v) + "\n"
        if nodeTypesTxt != "": nodeTypesTxt = nodeTypesTxt[: -1]
        conf["textBox"] = "Row Size (N, K): "+attrbs['bsrn']+ ", "+attrbs['bsrk']\
        +"\nColumn Size: (N, K): "+attrbs['bscn']+ ", "+attrbs['bsck']\
        +"\nNumber of nodes: "+attrbs['nn']+"\nFailure rate: "+attrbs['fr']+"%"+"\nMalicious Node: "+attrbs['mn']+"%"+"\nNetwork degree: "+attrbs['nd']\
        +"\nCustody Rows: "+attrbs['cusr']+" (Min: "+attrbs['mcusr']+")"+"\nCustody Cols: "+attrbs['cusc']+" (Min: "+attrbs['mcusc']+")"+"\n"+nodeTypesTxt\
        +"\nSegment Size: "+str(self.config.segmentSize)
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
        attrbs = self.__get_attrbs__(result)
        nodeTypes = self.__getNodeTypes__(attrbs['ntypes'])
        nodeTypesTxt = ""
        for _k, _v in nodeTypes.items():
            nodeTypesTxt += f"Type ({_k}): " + str(_v) + "\n"
        if nodeTypesTxt != "": nodeTypesTxt = nodeTypesTxt[: -1]
        conf["textBox"] = "Row Size (N, K): "+attrbs['bsrn']+ ", "+attrbs['bsrk']\
        +"\nColumn Size: (N, K): "+attrbs['bscn']+ ", "+attrbs['bsck']\
        +"\nNumber of nodes: "+attrbs['nn']+"\nFailure rate: "+attrbs['fr']+"%"+"\nMalicious Node: "+attrbs['mn']+"%"+"\nNetwork degree: "+attrbs['nd']\
        +"\nCustody Rows: "+attrbs['cusr']+" (Min: "+attrbs['mcusr']+")"+"\nCustody Cols: "+attrbs['cusc']+" (Min: "+attrbs['mcusc']+")"+"\n"+nodeTypesTxt\
        +"\nSegment Size: "+str(self.config.segmentSize)
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
    
    def plotBoxMessagesSent(self, result, plotPath):
        """Box Plot of the number of messages sent by all nodes"""
        conf = {}
        attrbs = self.__get_attrbs__(result)
        nodeTypes = self.__getNodeTypes__(attrbs['ntypes'])
        nodeTypesTxt = ""
        for _k, _v in nodeTypes.items():
            nodeTypesTxt += f"Type ({_k}): " + str(_v) + "\n"
        if nodeTypesTxt != "": nodeTypesTxt = nodeTypesTxt[: -1]
        conf["textBox"] = "Row Size (N, K): "+attrbs['bsrn']+ ", "+attrbs['bsrk']\
        +"\nColumn Size: (N, K): "+attrbs['bscn']+ ", "+attrbs['bsck']\
        +"\nNumber of nodes: "+attrbs['nn']+"\nFailure rate: "+attrbs['fr']+"%"+"\nMalicious Node: "+attrbs['mn']+"%"+"\nNetwork degree: "+attrbs['nd']\
        +"\nCustody Rows: "+attrbs['cusr']+" (Min: "+attrbs['mcusr']+")"+"\nCustody Cols: "+attrbs['cusc']+" (Min: "+attrbs['mcusc']+")"+"\n"+nodeTypesTxt\
        +"\nSegment Size: "+str(self.config.segmentSize)
        conf["title"] = "Number of Messages Sent by Nodes"
        conf["xlabel"] = "Node Type"
        conf["ylabel"] = "Number of Messages Sent"
        n1 = int(result.numberNodes * result.class1ratio)
        conf["data"] = [result.msgSentCount[1: n1], result.msgSentCount[n1+1: ]]
        conf["path"] = plotPath + "/box_messagesSent.png"
        plotBoxData(conf)
        print("Plot %s created." % conf["path"])

    def plotMessagesRecv(self, result, plotPath):
        """Plots the number of messages received by all nodes"""
        conf = {}
        attrbs = self.__get_attrbs__(result)
        nodeTypes = self.__getNodeTypes__(attrbs['ntypes'])
        nodeTypesTxt = ""
        for _k, _v in nodeTypes.items():
            nodeTypesTxt += f"Type ({_k}): " + str(_v) + "\n"
        if nodeTypesTxt != "": nodeTypesTxt = nodeTypesTxt[: -1]
        conf["textBox"] = "Row Size (N, K): "+attrbs['bsrn']+ ", "+attrbs['bsrk']\
        +"\nColumn Size: (N, K): "+attrbs['bscn']+ ", "+attrbs['bsck']\
        +"\nNumber of nodes: "+attrbs['nn']+"\nFailure rate: "+attrbs['fr']+"%"+"\nMalicious Node: "+attrbs['mn']+"%"+"\nNetwork degree: "+attrbs['nd']\
        +"\nCustody Rows: "+attrbs['cusr']+" (Min: "+attrbs['mcusr']+")"+"\nCustody Cols: "+attrbs['cusc']+" (Min: "+attrbs['mcusc']+")"+"\n"+nodeTypesTxt\
        +"\nSegment Size: "+str(self.config.segmentSize)
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
        attrbs = self.__get_attrbs__(result)
        nodeTypes = self.__getNodeTypes__(attrbs['ntypes'])
        nodeTypesTxt = ""
        for _k, _v in nodeTypes.items():
            nodeTypesTxt += f"Type ({_k}): " + str(_v) + "\n"
        if nodeTypesTxt != "": nodeTypesTxt = nodeTypesTxt[: -1]
        conf["textBox"] = "Row Size (N, K): "+attrbs['bsrn']+ ", "+attrbs['bsrk']\
        +"\nColumn Size: (N, K): "+attrbs['bscn']+ ", "+attrbs['bsck']\
        +"\nNumber of nodes: "+attrbs['nn']+"\nFailure rate: "+attrbs['fr']+"%"+"\nMalicious Node: "+attrbs['mn']+"%"+"\nNetwork degree: "+attrbs['nd']\
        +"\nCustody Rows: "+attrbs['cusr']+" (Min: "+attrbs['mcusr']+")"+"\nCustody Cols: "+attrbs['cusc']+" (Min: "+attrbs['mcusc']+")"+"\n"+nodeTypesTxt\
        +"\nSegment Size: "+str(self.config.segmentSize)
        conf["title"] = "Number of Messages Received by Nodes"
        conf["type"] = "individual_bar"
        conf["legLoc"] = 1
        conf["desLoc"] = 1
        conf["xlabel"] = "Node Type"
        conf["ylabel"] = "Number of Messages Received"
        n1 = int(result.numberNodes * result.class1ratio)
        conf["data"] = [result.msgRecvCount[1: n1], result.msgRecvCount[n1+1: ]]
        conf["xdots"] = range(result.shape.numberNodes)
        conf["path"] = plotPath + "/box_messagesRecv.png"
        maxi = max(conf["data"])
        conf["yaxismax"] = maxi
        plotBoxData(conf)
        print("Plot %s created." % conf["path"])

    def plotSamplesRepaired(self, result, plotPath):
        """Plots the number of samples repaired by all nodes"""
        conf = {}
        attrbs = self.__get_attrbs__(result)
        nodeTypes = self.__getNodeTypes__(attrbs['ntypes'])
        nodeTypesTxt = ""
        for _k, _v in nodeTypes.items():
            nodeTypesTxt += f"Type ({_k}): " + str(_v) + "\n"
        if nodeTypesTxt != "": nodeTypesTxt = nodeTypesTxt[: -1]
        conf["textBox"] = "Row Size (N, K): "+attrbs['bsrn']+ ", "+attrbs['bsrk']\
        +"\nColumn Size: (N, K): "+attrbs['bscn']+ ", "+attrbs['bsck']\
        +"\nNumber of nodes: "+attrbs['nn']+"\nFailure rate: "+attrbs['fr']+"%"+"\nMalicious Node: "+attrbs['mn']+"%"+"\nNetwork degree: "+attrbs['nd']\
        +"\nCustody Rows: "+attrbs['cusr']+" (Min: "+attrbs['mcusr']+")"+"\nCustody Cols: "+attrbs['cusc']+" (Min: "+attrbs['mcusc']+")"+"\n"+nodeTypesTxt\
        +"\nSegment Size: "+str(self.config.segmentSize)
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
    
    def plotHeatMapData(self, conf):
        data = {'x': conf['x'], 'y': conf['y'], 'weights': conf['weights']}
        df = pd.DataFrame(data)
        pivot_df = df.pivot_table(index='y', columns='x', values='weights', aggfunc="sum")
        
        # Create subplots
        fig, (ax_heatmap, ax_textbox) = plt.subplots(1, 2, figsize=(18, 6))
        
        # Plot heatmap
        sns.heatmap(pivot_df, annot=True, cmap='viridis', fmt='.0f', ax=ax_heatmap)
        ax_heatmap.set_xlabel(conf['xlabel'])
        ax_heatmap.set_ylabel(conf['ylabel'])
        ax_heatmap.set_title(conf['title'])
        
        # Plot textbox
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax_textbox.text(0.5, 0.5, conf["textBox"], fontsize=14, verticalalignment='center', transform=ax_textbox.transAxes, bbox=props)
        ax_textbox.axis('off')  # Turn off axis for the textbox subplot
        
        folder = f"results/{self.execID}/heatmaps/{conf['folder']}"
        os.makedirs(folder, exist_ok=True)
        plt.savefig(f"{folder}/{conf['path']}")
        plt.clf()
        plt.close()
    
    # Number of simulation runs with the same parameters for statistical relevance
    def totalRuns(self):
        rs = []
        for result in self.results: 
            attrbs = self.__get_attrbs__(result)
            rs.append(int(attrbs['r']))
        
        return max(rs) - min(rs) + 1
    
    # x -> network degree, y -> number of nodes, weights -> simulation duration
    def plotNWDegVsNodeOnRuntime(self):
        xyS = dict()
        for result in self.results: 
            attrbs = self.__get_attrbs__(result)
            nodeTypes = self.__getNodeTypes__(attrbs['ntypes'])
            nodeTypesTxt = ""
            for _k, _v in nodeTypes.items():
                nodeTypesTxt += f"Type ({_k}): " + str(_v) + "\n"
            if nodeTypesTxt != "": nodeTypesTxt = nodeTypesTxt[: -1]
            textBox = "Row Size (N, K): "+attrbs['bsrn']+ ", "+attrbs['bsrk']\
                +"\nColumn Size: (N, K): "+attrbs['bscn']+ ", "+attrbs['bsck']\
                +"\nFailure rate: "+attrbs['fr']+"%"+"\nMalicious Node: "+attrbs['mn']+"%"\
                +"\nCustody Rows: "+attrbs['cusr']+" (Min: "+attrbs['mcusr']+")"+"\nCustody Cols: "+attrbs['cusc']+" (Min: "+attrbs['mcusc']+")"\
                +"\n"+nodeTypesTxt
            filename = "bsrn_" + attrbs['bsrn'] +\
                "_bsrk_" + attrbs['bsrk'] +\
                "_bscn_" + attrbs['bscn' ] +\
                "_bsck_" + attrbs['bsck'] +\
                "_fr_" + attrbs['fr'] +\
                "_mn_" + attrbs['mn'] +\
                "_cusr_" + attrbs['cusr'] +\
                "_cusc_" + attrbs['cusc'] +\
                "_ntypes_" + attrbs['ntypes']
            identifier = (
                attrbs['bsrn'], attrbs['bsrk'], attrbs['bscn'],
                attrbs['bsck'], attrbs['fr'], attrbs['mn'],
                attrbs['cusr'], attrbs['cusc'], attrbs['ntypes']
            )
            if identifier in xyS.keys():
                xyS[identifier]['x'].append(result.shape.netDegree)
                xyS[identifier]['y'].append(result.shape.numberNodes)
                xyS[identifier]['w'].append(self.config.stepDuration * (len(result.missingVector) - 1))
            else:
                xyS[identifier] = {
                    'x': [result.shape.netDegree],
                    'y': [result.shape.numberNodes],
                    'w': [self.config.stepDuration * (len(result.missingVector) - 1)],
                    'textBox': textBox,
                    'filename': filename
                }
        
        runs = self.totalRuns()
        for v in xyS.values():
            x = v['x']
            y = v['y']
            weights = [(w / runs) for w in v['w']]
            
            if len(set(x)) * len(set(y)) < 2: return # Not enough unique params for heatmap
            
            conf = {
                'x': x,
                'y': y,
                'weights': weights,
                'xlabel': 'Net Degree',
                'ylabel': 'Number of Nodes',
                'title': 'Net Degree vs. Number of Nodes on Simulation Runtime (ms)',
                'folder': 'NWDegVsNodeOnRuntime',
                'textBox': v['textBox'],
                'path': f"{v['filename']}.png"
            }
            
            self.plotHeatMapData(conf)
    
    # x -> network degree, y -> % of malicious nodes, weights -> no of missing samples
    def plotNWDegVsMalNodeOnMissingSamples(self):
        xyS = dict()
        for result in self.results: 
            attrbs = self.__get_attrbs__(result)
            nodeTypes = self.__getNodeTypes__(attrbs['ntypes'])
            nodeTypesTxt = ""
            for _k, _v in nodeTypes.items():
                nodeTypesTxt += f"Type ({_k}): " + str(_v) + "\n"
            if nodeTypesTxt != "": nodeTypesTxt = nodeTypesTxt[: -1]
            textBox = "Row Size (N, K): "+attrbs['bsrn']+ ", "+attrbs['bsrk']\
                +"\nColumn Size: (N, K): "+attrbs['bscn']+ ", "+attrbs['bsck']\
                +"\nFailure rate: "+attrbs['fr']+"%"+"\nNodes: "+attrbs['nn']\
                +"\nCustody Rows: "+attrbs['cusr']+" (Min: "+attrbs['mcusr']+")"+"\nCustody Cols: "+attrbs['cusc']+" (Min: "+attrbs['mcusc']+")"\
                +"\n"+nodeTypesTxt
            filename = "bsrn_" + attrbs['bsrn'] +\
                "_bsrk_" + attrbs['bsrk'] +\
                "_bscn_" + attrbs['bscn' ] +\
                "_bsck_" + attrbs['bsck'] +\
                "-nn-" + attrbs['nn'] +\
                "_fr_" + attrbs['fr'] +\
                "_cusr_" + attrbs['cusr'] +\
                "_cusc_" + attrbs['cusc'] +\
                "_ntypes_" + attrbs['ntypes']
            identifier = (
                attrbs['bsrn'], attrbs['bsrk'], attrbs['bscn'],
                attrbs['bsck'], attrbs['fr'], attrbs['nn'],
                attrbs['cusr'], attrbs['cusc'], attrbs['ntypes']
            )
            if identifier in xyS.keys():
                xyS[identifier]['x'].append(result.shape.netDegree)
                xyS[identifier]['y'].append(result.shape.maliciousNodes)
                xyS[identifier]['w'].append(result.missingVector[-1])
            else:
                xyS[identifier] = {
                    'x': [result.shape.netDegree],
                    'y': [result.shape.maliciousNodes],
                    'w': [result.missingVector[-1]],
                    'textBox': textBox,
                    'filename': filename
                }
        
        runs = self.totalRuns()
        for v in xyS.values():
            x = v['x']
            y = v['y']
            weights = [(w / runs) for w in v['w']]
            
            if len(set(x)) * len(set(y)) < 2: return # Not enough unique params for heatmap
            
            conf = {
                'x': x,
                'y': y,
                'weights': weights,
                'xlabel': 'Net Degree',
                'ylabel': 'Malicious Nodes (%)',
                'title': 'Net Degree vs Malicious Nodes (%) on Missing Samples',
                'folder': 'NWDegVsMalNodeOnMissingSamples',
                'textBox': v['textBox'],
                'path': f"{v['filename']}.png"
            }
            
            self.plotHeatMapData(conf)

    # x -> network degree, y -> failure rate, weights -> no of missing samples
    def plotNWDegVsFailureRateOnMissingSamples(self):
        xyS = dict()
        for result in self.results: 
            attrbs = self.__get_attrbs__(result)
            nodeTypes = self.__getNodeTypes__(attrbs['ntypes'])
            nodeTypesTxt = ""
            for _k, _v in nodeTypes.items():
                nodeTypesTxt += f"Type ({_k}): " + str(_v) + "\n"
            if nodeTypesTxt != "": nodeTypesTxt = nodeTypesTxt[: -1]
            textBox = "Row Size (N, K): "+attrbs['bsrn']+ ", "+attrbs['bsrk']\
                +"\nColumn Size: (N, K): "+attrbs['bscn']+ ", "+attrbs['bsck']\
                +"\nNodes: "+attrbs['nn']+"\nMalicious Node: "+attrbs['mn']+"%"\
                +"\nCustody Rows: "+attrbs['cusr']+" (Min: "+attrbs['mcusr']+")"+"\nCustody Cols: "+attrbs['cusc']+" (Min: "+attrbs['mcusc']+")"\
                +"\n"+nodeTypesTxt
            filename = "bsrn_" + attrbs['bsrn'] +\
                "_bsrk_" + attrbs['bsrk'] +\
                "_bscn_" + attrbs['bscn' ] +\
                "_bsck_" + attrbs['bsck'] +\
                "-nn-" + attrbs['nn'] +\
                "_mn_" + attrbs['mn'] +\
                "_cusr_" + attrbs['cusr'] +\
                "_cusc_" + attrbs['cusc'] +\
                "_ntypes_" + attrbs['ntypes']
            identifier = (
                attrbs['bsrn'], attrbs['bsrk'], attrbs['bscn'],
                attrbs['bsck'], attrbs['mn'], attrbs['nn'],
                attrbs['cusr'], attrbs['cusc'], attrbs['ntypes']
            )
            if identifier in xyS.keys():
                xyS[identifier]['x'].append(result.shape.netDegree)
                xyS[identifier]['y'].append(result.shape.failureRate)
                xyS[identifier]['w'].append(result.missingVector[-1])
            else:
                xyS[identifier] = {
                    'x': [result.shape.netDegree],
                    'y': [result.shape.failureRate],
                    'w': [result.missingVector[-1]],
                    'textBox': textBox,
                    'filename': filename
                }
        
        runs = self.totalRuns()
        for v in xyS.values():
            x = v['x']
            y = v['y']
            weights = [(w / runs) for w in v['w']]
            
            if len(set(x)) * len(set(y)) < 2: return # Not enough unique params for heatmap
            
            conf = {
                'x': x,
                'y': y,
                'weights': weights,
                'xlabel': 'Net Degree',
                'ylabel': 'Failure Rate (%)',
                'title': 'Net Degree vs Failure Rate (%) on Missing Samples',
                'folder': 'NWDegVsFailureRateOnMissingSamples',
                'textBox': v['textBox'],
                'path': f"{v['filename']}.png"
            }
            
            self.plotHeatMapData(conf)
         
    def plotAllHeatMaps(self):
        self.plotNWDegVsNodeOnRuntime()
        self.plotNWDegVsMalNodeOnMissingSamples()
        self.plotNWDegVsFailureRateOnMissingSamples()