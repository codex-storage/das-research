import os
import time
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from itertools import combinations

results_folder = os.getcwd()

#Get all folders and store their time info and sort
directories = [d for d in os.listdir(results_folder) if os.path.isdir(os.path.join(results_folder, d))]
directories_ctime = [(d, os.path.getctime(os.path.join(results_folder, d))) for d in directories]
directories_ctime.sort(key=lambda x: x[1], reverse=True)

#Get the path of the latest created folder
latest_directory = directories_ctime[0][0]
folder_path = os.path.join(results_folder, latest_directory)

#Store data with a unique key for each params combination
data = {}
plotInfo = {}

parameters = ['run', 'blockSize', 'failureRate', 'numberValidators', 'netDegree', 'chi']

#Loop over the xml files in the folder
for filename in os.listdir(folder_path):
    #Loop over the xmls and store the data in variables
    if filename.endswith('.xml'):
        tree = ET.parse(os.path.join(folder_path, filename))
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
            selected_values = [run, blockSize, failureRate, numberValidators, netDegree, chi]
            values = [selected_values[index] for index in indices]
            names = [parameters[i] for i in indices]
            keyComponents = [f"{name}_{value}" for name, value in zip(names, values)]
            key = tuple(keyComponents[:4])
            #Get the names of the other 2 parameters that are not included in the key
            other_params = [parameters[i] for i in range(6) if i not in indices]
            #Append the values of the other 2 parameters and the ttas to the lists for the key
            other_indices = [i for i in range(len(parameters)) if i not in indices]

            #Initialize the dictionary for the key if it doesn't exist yet
            if key not in data:
                data[key] = {}
                #Initialize lists for the other 2 parameters and the ttas with the key
                data[key][other_params[0]] = []
                data[key][other_params[1]] = []
                data[key]['ttas'] = []

            if other_params[0] in data[key]:
                data[key][other_params[0]].append(selected_values[other_indices[0]])
            else:
                data[key][other_params[0]] = [selected_values[other_indices[0]]]
            if other_params[1] in data[key]:
                data[key][other_params[1]].append(selected_values[other_indices[1]])
            else:
                data[key][other_params[1]] = [selected_values[other_indices[1]]]
            data[key]['ttas'].append(tta)


#Get the keys for all data with the same x and y labels
filtered_keys = {}
for key1, value1 in data.items():
    sub_keys1 = list(value1.keys())
    filtered_keys[(sub_keys1[0], sub_keys1[1])] = [key1]
    for key2, value2 in data.items():
        sub_keys2 = list(value2.keys())
        if key1 != key2 and sub_keys1[0] == sub_keys2[0] and sub_keys1[1] == sub_keys2[1]:
            try:
                filtered_keys[(sub_keys1[0], sub_keys1[1])].append(key2)
            except KeyError:
                filtered_keys[(sub_keys1[0], sub_keys1[1])] = [key2]

#Store the 2D heatmaps in a folder
heatmaps_folder = 'heatmaps'
if not os.path.exists(heatmaps_folder):
    os.makedirs(heatmaps_folder)

#Plot the heatmaps and store them in subfolders
for labels, keys in filtered_keys.items():
    for key in keys:
        hist, xedges, yedges = np.histogram2d(data[key][labels[0]], data[key][labels[1]], bins=(3, 3), weights=data[key]['ttas'])
        hist = hist.T
        sns.heatmap(hist, xticklabels=False, yticklabels=False, cmap='Purples', cbar_kws={'label': 'Time to block availability'}, linecolor='black', linewidths=0.3, annot=True, fmt=".2f")
        plt.xlabel(labels[0])
        plt.ylabel(labels[1])
        title = ""
        paramValueCnt = 0
        for param in parameters:
            if param != labels[0] and param != labels[1]:
                title += f"{key[paramValueCnt]}"
                paramValueCnt += 1
        plt.title(title)
        filename = title + ".png"
        target_folder = os.path.join(heatmaps_folder, f"{labels[0]}Vs{labels[1]}")
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)
        plt.savefig(os.path.join(target_folder, filename))
        plt.clf()
