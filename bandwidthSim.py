import random
import time

class Config:

    def __init__(self):
        self.networkSize = 100
        self.networkDegree = 8
        self.badBoy = 66
        self.builders = [12, 26]
        self.nbSlots = 10

class Node:

    def __init__(self, config):
        self.peers = []
        self.speed = random.randint(0, 10)
        self.networkDegree = config.networkDegree
        self.networkSize = config.networkSize
        for i in range(self.networkDegree):
            self.peers.append(random.randint(0, self.networkSize-1))

def executeSlot(config, nodes):

    pastBorder = []
    currentBorder = []
    for b in config.builders:
        currentBorder.append(b)
    while(True):
        #print("Current border size: " + str(len(currentBorder)))
        #print("Past border size: " + str(len(pastBorder)))
        #print("Nodes size: " + str(len(nodes)))
        for nodeID in currentBorder:
            for peer in nodes[nodeID].peers:
                if peer not in pastBorder and peer not in currentBorder:
                    currentBorder.append(peer)
            pastBorder.append(nodeID)
            currentBorder.remove(nodeID)
        if len(pastBorder) == len(nodes):
            break
        #time.sleep(1)
    return 0

def sim():

    config = Config()
    nodes = []

    for i in range(config.networkSize):
        nodes.append(Node(config))

    for i in range(config.networkSize):
        print("My speed is "+ str(nodes[i].speed))
        print("My peers are "+ str(nodes[i].peers))

    for slot in range(config.nbSlots):
        executeSlot(config, nodes)
        print("Slot finished: "+ str(slot))
sim()
