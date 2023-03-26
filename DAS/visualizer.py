#!/bin/python3
import os, sys
import time
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from itertools import combinations

class Visualizer:

    def __init__(self, execID):
        self.execID = execID
        self.folderPath = "results/"+self.execID
        self.parameters = ['run', 'blockSize', 'failureRate', 'numberNodes', 'netDegree',
                           'chi', 'vpn1', 'vpn2', 'bwUplinkProd', 'bwUplink1', 'bwUplink2']
        self.minimumDataPoints = 2

    def plottingData(self):
        """Store data with a unique key for each params combination"""
        data = {}
        """Loop over the xml files in the folder"""
        for filename in os.listdir(self.folderPath):
            """Loop over the xmls and store the data in variables"""
            if filename.endswith('.xml'):
                tree = ET.parse(os.path.join(self.folderPath, filename))
                root = tree.getroot()
                run = int(root.find('run').text)
                blockSize = int(root.find('blockSize').text)
                failureRate = int(root.find('failureRate').text)
                numberNodes = int(root.find('numberNodes').text)
                netDegree = int(root.find('netDegree').text)
                chi = int(root.find('chi').text)
                vpn1 = int(root.find('vpn1').text)
                vpn2 = int(root.find('vpn2').text)
                bwUplinkProd = int(root.find('bwUplinkProd').text)
                bwUplink1 = int(root.find('bwUplink1').text)
                bwUplink2 = int(root.find('bwUplink2').text)
                tta = int(root.find('tta').text)

                """Loop over all possible combinations of length 4 of the parameters"""
                for combination in combinations(self.parameters, len(self.parameters)-2):
                    # Get the indices and values of the parameters in the combination

                    indices = [self.parameters.index(element) for element in combination]
                    selectedValues = [run, blockSize, failureRate, numberNodes, netDegree, chi, vpn1, vpn2, bwUplinkProd, bwUplink1, bwUplink2]
                    values = [selectedValues[index] for index in indices]
                    names = [self.parameters[i] for i in indices]
                    keyComponents = [f"{name}_{value}" for name, value in zip(names, values)]
                    key = tuple(keyComponents[:len(self.parameters)-2])
                    """Get the names of the other 2 parameters that are not included in the key"""
                    otherParams = [self.parameters[i] for i in range(len(self.parameters)) if i not in indices]
                    """Append the values of the other 2 parameters and the ttas to the lists for the key"""
                    otherIndices = [i for i in range(len(self.parameters)) if i not in indices]

                    """Initialize the dictionary for the key if it doesn't exist yet"""
                    if key not in data:
                        data[key] = {}
                        """Initialize lists for the other 2 parameters and the ttas with the key"""
                        data[key][otherParams[0]] = []
                        data[key][otherParams[1]] = []
                        data[key]['ttas'] = []

                    if otherParams[0] in data[key]:
                        data[key][otherParams[0]].append(selectedValues[otherIndices[0]])
                    else:
                        data[key][otherParams[0]] = [selectedValues[otherIndices[0]]]
                    if otherParams[1] in data[key]:
                        data[key][otherParams[1]].append(selectedValues[otherIndices[1]])
                    else:
                        data[key][otherParams[1]] = [selectedValues[otherIndices[1]]]
                    data[key]['ttas'].append(tta)
        print("Getting data from the folder...")
        return data
    
    def averageRuns(self, data):
        """Get the average of run 0 and run 1 for each key"""
        newData = {}
        for key, value in data.items():
            runExists = False
            """Check if the key contains 'run_' with a numerical value"""
            for item in key:
                if item.startswith('run_0'):
                    runExists = True
                    break
            if runExists:
                for item in key:
                    """Create a new key with the other items in the tuple"""
                    if item.startswith('run_'):
                        newKey = tuple([x for x in key if x != item])
                        key0 = ('run_0',) + newKey
                        data0 = data[key0]
                        key1 = ('run_1',) + newKey
                        data1 = data[key1]
                        averages = {}
                        for key in data0.keys():
                            if key in data1:
                                values = []
                                for i in range(len(data0[key])):
                                    value = (data0[key][i] + data1[key][i]) / 2.0
                                    if isinstance(data0[key][i], int) and isinstance(data1[key][i], int) and key != 'ttas':
                                        value = int(value)
                                    values.append(value)
                                averages[key] = values
                        newData[newKey] = averages
        print("Getting the average of the runs...")
        return newData

    def similarKeys(self, data):
        """Get the keys for all data with the same x and y labels"""
        filteredKeys = {}
        for key1, value1 in data.items():
            subKeys1 = list(value1.keys())
            filteredKeys[(subKeys1[0], subKeys1[1])] = [key1]
            for key2, value2 in data.items():
                subKeys2 = list(value2.keys())
                if key1 != key2 and subKeys1[0] == subKeys2[0] and subKeys1[1] == subKeys2[1]:
                    try:
                        filteredKeys[(subKeys1[0], subKeys1[1])].append(key2)
                    except KeyError:
                        filteredKeys[(subKeys1[0], subKeys1[1])] = [key2]
        print("Getting filtered keys from data...")
        return filteredKeys

    def formatLabel(self, label):
        """Label formatting for the figures"""
        result = ''.join([f" {char}" if char.isupper() else char for char in label])
        return result.title()

    def formatTitle(self, key):
        """Title formatting for the figures"""
        name = ''.join([f" {char}" if char.isupper() else char for char in key.split('_')[0]])
        number = key.split('_')[1]
        return f"{name.title()}: {number} "

    def plotHeatmaps(self):
        """Plot and store the 2D heatmaps in subfolders"""
        data = self.plottingData()
        data = self.averageRuns(data)
        filteredKeys = self.similarKeys(data)
        print("Plotting heatmaps...")
   
        """Create the directory if it doesn't exist already"""
        heatmapsFolder = self.folderPath + '/heatmaps'
        if not os.path.exists(heatmapsFolder):
            os.makedirs(heatmapsFolder)

        """Plot"""
        for labels, keys in filteredKeys.items():
            for key in keys:
                xlabels = np.sort(np.unique(data[key][labels[0]]))
                ylabels = np.sort(np.unique(data[key][labels[1]]))
                if len(xlabels) < self.minimumDataPoints or len(ylabels) < self.minimumDataPoints:
                    continue
                hist, xedges, yedges = np.histogram2d(data[key][labels[0]], data[key][labels[1]], bins=(len(xlabels), len(ylabels)), weights=data[key]['ttas'])
                hist = hist.T
                fig, ax = plt.subplots(figsize=(10, 6))
                sns.heatmap(hist, xticklabels=xlabels, yticklabels=ylabels, cmap='Purples', cbar_kws={'label': 'Time to block availability'}, linecolor='black', linewidths=0.3, annot=True, fmt=".2f", ax=ax)
                plt.xlabel(self.formatLabel(labels[0]))
                plt.ylabel(self.formatLabel(labels[1]))
                filename = ""
                title = ""
                paramValueCnt = 0
                for param in self.parameters:
                    if param != labels[0] and param != labels[1] and param != 'run':
                        filename += f"{key[paramValueCnt]}"
                        formattedTitle = self.formatTitle(key[paramValueCnt])
                        title += formattedTitle
                        paramValueCnt += 1
                title_obj = plt.title(title)
                font_size = 16 * fig.get_size_inches()[0] / 10
                title_obj.set_fontsize(font_size)
                filename = filename + ".png"
                targetFolder = os.path.join(heatmapsFolder, f"{labels[0]}Vs{labels[1]}")
                if not os.path.exists(targetFolder):
                    os.makedirs(targetFolder)
                plt.savefig(os.path.join(targetFolder, filename))
                plt.close()
                plt.clf()
