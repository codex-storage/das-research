import networkx as nx
import random
import matplotlib.pyplot as plt
import sys
import numpy as np
from datetime import datetime
import os
from joblib import Parallel, delayed


def plotData(conf):
    for key, value in conf['y'].items():
        plt.plot(conf['x'], value, label=f"{conf['label']}: {key}")
    plt.xlabel(conf['xlabel'])
    plt.ylabel(conf['ylabel'])
    plt.title(conf['title'])
    plt.legend()
    plt.grid(True)
    plt.savefig(conf['plotPath'])
    plt.clf()

def isGConnected(deg, nodes, mal):
    G = nx.random_regular_graph(deg, nodes)
    malNodes = random.sample(list(G.nodes()), k=mal * nodes // 100)
    for mn in malNodes:
        G.remove_node(mn)
    
    return nx.is_connected(G)

def getValidatorCountPerColumn(numberOfCols, numOfValidators, chiC):
    validatorCountPerColumn = dict()
    for _ in range(numOfValidators):
        colsSelected = random.sample(list(range(1, numberOfCols + 1)), chiC)
        for col in colsSelected:
            if col in validatorCountPerColumn.keys():
                validatorCountPerColumn[col] += 1
            else:
                validatorCountPerColumn[col] = 0
    
    return validatorCountPerColumn

def runOnce(deg, validatorCountPerCol, malNodesPercentage):
    isParted = False
    partCount = 0
    isPartedCount = 0
    for col in validatorCountPerCol.keys():
        nodes = validatorCountPerCol[col]
        if not isGConnected(deg, nodes, malNodesPercentage):
            if not isParted: isParted = True
            partCount += 1
    
    if isParted: isPartedCount += 1
    
    return isPartedCount, partCount

def study():
    nnPartPercentages = dict()
    nnAvgDisconnectedCols = dict()
    
    for nn, nv in zip(numberOfNodes, numberOfValidators):
        print(f"\nNumber of Nodes: {nn}")
        
        partPercentages = list()
        avgDisconnectedCols = list()
        for mal in mals:
            isPartedCount = partCount = 0
            validatorCountPerColumn = getValidatorCountPerColumn(numberOfColumns, nv, custody)
            results = Parallel(-1)(delayed(runOnce)(deg, validatorCountPerColumn, mal) for _run in range(runs))
            isPartedCount = sum([res[0] for res in results])
            partCount = sum([res[1] for res in results])
            partPercentages.append(isPartedCount * 100 / runs)
            avgDisconnectedCols.append(partCount / runs)
            print(f"Malicious Nodes: {mal}%, Partition Percentage: {partPercentages[-1]}, Avg. Partitions: {avgDisconnectedCols[-1]}")
        
        nnPartPercentages[nn] = partPercentages
        nnAvgDisconnectedCols[nn] = avgDisconnectedCols
    
    now = datetime.now()
    execID = now.strftime("%Y-%m-%d_%H-%M-%S_")+str(random.randint(100,999))
    newpath = f"ConnectivityTest/MaliciousNodesVsNumberOfNodes/results/{execID}/"
    if not os.path.exists(newpath): os.makedirs(newpath)
    
    conf1 = {
        'x': mals,
        'y': nnPartPercentages,
        'label': "Nodes",
        'xlabel': "Malicious Node (%)",
        'ylabel': "Partition Possibility (%)",
        "title": "Possibility of Network Graph Get Partitioned for Malicious Nodes",
        "plotPath": f"{newpath}prob.png"
    }
    
    conf2 = {
        'x': mals,
        'y': nnAvgDisconnectedCols,
        'label': "Nodes",
        'xlabel': "Malicious Node (%)",
        'ylabel': "Avg. Disconnected Columns",
        "title": "Malicious Nodes (%) vs. Disconnected Columns",
        "plotPath": f"{newpath}num.png"
    }
    
    plotData(conf1)
    plotData(conf2)


# Configuration
runs = 10
deg = 8
mals = range(5, 100, 5)
numberOfColumns = 128
custody = 4
numberOfNodes = [int(_) for _ in (np.logspace(2, 4, 5, endpoint=True, base=10) * 5)]
numberOfValidators = [int(nn * 2.4) for nn in numberOfNodes] # (0.8 * 1 + 0.2 * 8 = 2.4)

if __name__ == "__main__":
    study()