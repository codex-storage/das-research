import os
import time
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from itertools import combinations

parameters = ['run', 'blockSize', 'failureRate', 'numberValidators', 'netDegree', 'chi']

#Title formatting for the figures
def formatTitle(key):
    name = ''.join([f" {char}" if char.isupper() else char for char in key.split('_')[0]])
    number = key.split('_')[1]
    return f"{name.title()}: {number} "

def getLatestDirectory():  
    resultsFolder = os.getcwd()

    #Get all folders and store their time info and sort
    directories = [d for d in os.listdir(resultsFolder) if os.path.isdir(os.path.join(resultsFolder, d))]
    directoriesTime = [(d, os.path.getctime(os.path.join(resultsFolder, d))) for d in directories]
    directoriesTime.sort(key=lambda x: x[1], reverse=True)

    #Get the path of the latest created folder
    latestDirectory = directoriesTime[0][0]
    folderPath = os.path.join(resultsFolder, latestDirectory)
    return folderPath

def plottingData(folderPath):
    #Store data with a unique key for each params combination
    data = {}
    plotInfo = {}

    #Loop over the xml files in the folder
    for filename in os.listdir(folderPath):
        #Loop over the xmls and store the data in variables
        if filename.endswith('.xml'):
            tree = ET.parse(os.path.join(folderPath, filename))
            root = tree.getroot()
            run = int(root.find('run').text)
            blockSize = int(root.find('blockSize').text)
            failureRate = int(root.find('failureRate').text)
            numberValidators = int(root.find('numberValidators').text)
            netDegree = int(root.find('netDegree').text)
            chi = int(root.find('chi').text)
            tta = int(root.find('tta').text)

            # Loop over all possible combinations of length 4 of the parameters
            for combination in combinations(parameters, 4):
                # Get the indices and values of the parameters in the combination
                indices = [parameters.index(element) for element in combination]
                selectedValues = [run, blockSize, failureRate, numberValidators, netDegree, chi]
                values = [selectedValues[index] for index in indices]
                names = [parameters[i] for i in indices]
                keyComponents = [f"{name}_{value}" for name, value in zip(names, values)]
                key = tuple(keyComponents[:4])
                #Get the names of the other 2 parameters that are not included in the key
                otherParams = [parameters[i] for i in range(6) if i not in indices]
                #Append the values of the other 2 parameters and the ttas to the lists for the key
                otherIndices = [i for i in range(len(parameters)) if i not in indices]

                #Initialize the dictionary for the key if it doesn't exist yet
                if key not in data:
                    data[key] = {}
                    #Initialize lists for the other 2 parameters and the ttas with the key
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
    return data

def similarKeys(data):
    #Get the keys for all data with the same x and y labels
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
    return filteredKeys

def plotHeatmaps(filteredKeys, data):
    #Store the 2D heatmaps in a folder
    heatmapsFolder = 'heatmaps'
    if not os.path.exists(heatmapsFolder):
        os.makedirs(heatmapsFolder)

    for labels, keys in filteredKeys.items():
        for key in keys:
            xlabels = np.sort(np.unique(data[key][labels[0]]))
            ylabels = np.sort(np.unique(data[key][labels[1]]))
            hist, xedges, yedges = np.histogram2d(data[key][labels[0]], data[key][labels[1]], bins=(len(xlabels), len(ylabels)), weights=data[key]['ttas'])
            hist = hist.T
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.heatmap(hist, xticklabels=xlabels, yticklabels=ylabels, cmap='Purples', cbar_kws={'label': 'Time to block availability'}, linecolor='black', linewidths=0.3, annot=True, fmt=".2f", ax=ax)
            plt.xlabel(labels[0])
            plt.ylabel(labels[1])
            filename = ""
            title = ""
            paramValueCnt = 0
            for param in parameters:
                if param != labels[0] and param != labels[1]:
                    filename += f"{key[paramValueCnt]}"
                    title += formatTitle(key[paramValueCnt])
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

def generateHeatmaps():
    folderPath = getLatestDirectory()
    data = plottingData(folderPath)
    filteredKeys = similarKeys(data)
    plotHeatmaps(filteredKeys, data)

generateHeatmaps()