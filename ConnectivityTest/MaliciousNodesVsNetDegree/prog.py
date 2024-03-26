import networkx as nx
import random
import matplotlib.pyplot as plt
import sys
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

def runOnce(run_i, runs, deg, validatorCountPerCol, malNodesPercentage):
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
    degPartPercentages = dict()
    degAvgDisconnectedCols = dict()
    
    for deg in degs:
        print(f"\nNetwork Degree: {deg}")
        
        partPercentages = list()
        avgDisconnectedCols = list()
        for mal in mals:
            isPartedCount = partCount = 0
            validatorCountPerColumn = getValidatorCountPerColumn(numberOfColumns, numberOfValidators, custody)
            results = Parallel(-1)(delayed(runOnce)(_run, runs, deg, validatorCountPerColumn, mal) for _run in range(runs))
            isPartedCount = sum([res[0] for res in results])
            partCount = sum([res[1] for res in results])
            partPercentages.append(isPartedCount * 100 / runs)
            avgDisconnectedCols.append(partCount / runs)
            print(f"Malicious Nodes: {mal}%, Partition Percentage: {partPercentages[-1]}, Avg. Partitions: {avgDisconnectedCols[-1]}")
        
        degPartPercentages[deg] = partPercentages
        degAvgDisconnectedCols[deg] = avgDisconnectedCols
    
    now = datetime.now()
    execID = now.strftime("%Y-%m-%d_%H-%M-%S_")+str(random.randint(100,999))
    newpath = f"ConnectivityTest/MaliciousNodesVsNetDegree/results/{execID}/"
    if not os.path.exists(newpath): os.makedirs(newpath)
    
    conf1 = {
        'x': mals,
        'y': degPartPercentages,
        'label': "NW Deg",
        'xlabel': "Malicious Node (%)",
        'ylabel': "Partition Possibility (%)",
        "title": "Possibility of Network Graph Get Partitioned for Malicious Nodes",
        "plotPath": f"{newpath}prob.png"
    }
    
    conf2 = {
        'x': mals,
        'y': degAvgDisconnectedCols,
        'label': "NW Deg",
        'xlabel': "Malicious Node (%)",
        'ylabel': "Avg. Disconnected Columns",
        "title": "Malicious Nodes (%) vs. Disconnected Columns",
        "plotPath": f"{newpath}num.png"
    }
    
    plotData(conf1)
    plotData(conf2)


# Configuration
runs = 10
degs = range(6, 13, 2)
mals = range(5, 100, 5)
numberOfColumns = 128
custody = 4
numberOfNodes = 5000
numberOfValidators = int(numberOfNodes * 2.4) # (0.8 * 1 + 0.2 * 8 = 2.4)

if __name__ == "__main__":
    study()