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
    plt.grid(True)
    plt.savefig(conf['plotPath'])
    plt.clf()

def isGConnected(deg, nodes, mal):
    G = nx.random_regular_graph(deg, nodes)
    malNodes = random.sample(list(G.nodes()), k=mal * nodes // 100)
    for mn in malNodes:
        G.remove_node(mn)
    
    return nx.is_connected(G)

def getNodeCountPerColumn(config):
    numberOfCols = config['numberOfColumns']
    numOfNodes = config['numberOfNodes']
    chiC1 = config['custodyC'] * config['validatorPerNode1']
    chiC2 = config['custodyC'] * config['validatorPerNode2']
    node1Count = int(numOfNodes * config['class1ratio'])
    nodeCountPerColumn = dict()
    for _ in range(numOfNodes):
        colsSelected = random.sample(list(range(1, numberOfCols + 1)), chiC1 if _ < node1Count else chiC2)
        for col in colsSelected:
            if col in nodeCountPerColumn.keys():
                nodeCountPerColumn[col] += 1
            else:
                nodeCountPerColumn[col] = 0
    
    return nodeCountPerColumn

def runOnce(deg, nodeCountPerCol, malNodesPercentage):
    isParted = False
    partCount = 0
    isPartedCount = 0
    for col in nodeCountPerCol.keys():
        nodes = nodeCountPerCol[col]
        if not isGConnected(deg, nodes, malNodesPercentage):
            if not isParted: isParted = True
            partCount += 1
    
    if isParted: isPartedCount += 1
    
    return isPartedCount, partCount

def study(config):
    degPartPercentages = dict()
    degAvgDisconnectedCols = dict()
    
    for deg in config['degs']:
        print(f"\nNetwork Degree: {deg}")
        
        partPercentages = list()
        avgDisconnectedCols = list()
        for mal in config['mals']:
            isPartedCount = partCount = 0
            nodeCountPerColumn = getNodeCountPerColumn(config)
            results = Parallel(-1)(delayed(runOnce)(deg, nodeCountPerColumn, mal) for _run in range(config['runs']))
            isPartedCount = sum([res[0] for res in results])
            partCount = sum([res[1] for res in results])
            partPercentages.append(isPartedCount * 100 / config['runs'])
            avgDisconnectedCols.append(partCount / config['runs'])
            print(f"Malicious Nodes: {mal}%, Partition Percentage: {partPercentages[-1]}, Avg. Partitions: {avgDisconnectedCols[-1]}")
        
        degPartPercentages[deg] = partPercentages
        degAvgDisconnectedCols[deg] = avgDisconnectedCols
    
    now = datetime.now()
    execID = now.strftime("%Y-%m-%d_%H-%M-%S_")+str(random.randint(100,999))
    newpath = f"ConnectivityTest/MaliciousNodesVsNetDegree/results/{execID}/"
    if not os.path.exists(newpath): os.makedirs(newpath)
    
    conf1 = {
        'x': config['mals'],
        'y': degPartPercentages,
        'label': "NW Deg",
        'xlabel': "Malicious Node (%)",
        'ylabel': "Partition Possibility (%)",
        "title": "Possibility of Network Graph Get Partitioned for Malicious Nodes",
        "plotPath": f"{newpath}prob.png"
    }
    
    conf2 = {
        'x': config['mals'],
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
config = {
    'runs': 50,
    'degs': range(6, 15, 2),
    'mals': range(5, 100, 5),
    'numberOfColumns': 128,
    'custodyC': 4,
    'class1ratio': 0.8,
    'validatorPerNode1': 1,
    'validatorPerNode2': 8,
    'numberOfNodes': 5000
}

if __name__ == "__main__":
    study(config)