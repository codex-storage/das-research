import random
import time

class Config:
    def __init__(self):
        self.networkSize = 100
        self.networkDegree = 8
        self.badBoy = 66
        self.builders = [12, 26, 54, 78, 98]
        self.nbSlots = 10

class Node:
    def __init__(self, config):
        self.peers = []
        self.poisoned = 0
        self.speed = random.randint(0, 10)
        self.networkDegree = config.networkDegree
        self.networkSize = config.networkSize
        for i in range(self.networkDegree):
            self.peers.append(random.randint(0, self.networkSize-1))


def pickBuilder(config):
    nbBuilders = len(config.builders)
    builder = random.randint(0, nbBuilders-1)
    return builder

def executeSlot(config, nodes):
    pastBorder = []
    currentBorder = []
    currentBorder.append(pickBuilder(config))
    while(True):
        #print("Current border size: " + str(len(currentBorder)))
        #print("Past border size: " + str(len(pastBorder)))
        #print("Nodes size: " + str(len(nodes)))
        for nodeID in currentBorder:
            if nodeID == config.badBoy:
                nodes[nodeID].poisoned = 1
            for peer in nodes[nodeID].peers:
                if peer not in pastBorder and peer not in currentBorder:
                    currentBorder.append(peer)
                    if nodeID == config.badBoy:
                        print("Badboy")
                    if nodes[nodeID].poisoned == 1:
                        nodes[peer].poisoned = 1
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

    for slot in range(config.nbSlots):
        # Slot starts with noone poisoned
        for n in range(config.networkSize):
            nodes[n].poisoned = 0

        # Execute slot
        executeSlot(config, nodes)

        # Coubnt poisoned nodes
        pois = 0
        for n in range(config.networkSize):
            pois += nodes[n].poisoned

        # Print results
        print("Slot finished: "+ str(slot)+" posoned: "+ str(pois))

    for i in range(config.networkSize):
        print("Node ID " + str(i), end="")
        print(" spped "+ str(nodes[i].speed), end="")
        print(" poison: "+ str(nodes[i].poisoned), end="")
        print(" My peers are "+ str(nodes[i].peers))


sim()
