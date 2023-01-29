import os
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import numpy as np

#Yet to update with the execID format
folder_path = 'results/2023-01-26_10-41-29_912'

#Store data with a unique key for each (run, numberValidators, netDegree, chi) combination
data = {}

for filename in os.listdir(folder_path):
    #Loop over the xmls and store the data in variables
    if filename.endswith('.xml'):
        tree = ET.parse(os.path.join(folder_path, filename))
        root = tree.getroot()
        run = int(root.find('run').text)
        numberValidators = int(root.find('numberValidators').text)
        netDegree = int(root.find('netDegree').text)
        chi = int(root.find('chi').text)
        blockSize = int(root.find('blockSize').text)
        failureRate = int(root.find('failureRate').text)
        tta = int(root.find('tta').text)

        #Create a key for this combination of run, numberValidators, netDegree, and chi if it does not exist yet
        key = (run, numberValidators, netDegree, chi)
        if key not in data:
            data[key] = {'blockSizes': [], 'failureRates': [], 'ttas': []}

        #Append the data used for the plot
        data[key]['blockSizes'].append(blockSize)
        data[key]['failureRates'].append(failureRate)
        data[key]['ttas'].append(tta)

#Store the 2D heatmaps in a folder
heatmaps_folder = 'heatmaps'
if not os.path.exists(heatmaps_folder):
    os.makedirs(heatmaps_folder)

#Plot the heatmaps
for key, values in data.items():
    hist, xedges, yedges = np.histogram2d(values['blockSizes'], values['failureRates'], bins=(10, 10), weights=values['ttas'])
    plt.imshow(hist, extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]])
    plt.xlabel('blockSize')
    plt.ylabel('failureRate')
    plt.colorbar().set_label('tta')
    title = f"run={key[0]}, numberValidators={key[1]}, netDegree={key[2]}, chi={key[3]}"
    plt.title(title)
    filename = f"run={key[0]}_numberValidators={key[1]}_netDegree={key[2]}_chi={key[3]}.png"
    plt.savefig(os.path.join(heatmaps_folder, filename))
    plt.clf()
