import networkx as nx
import hashlib
from src.results import *
import random
import csv
import pandas as pd
from src.node import Node
from src.neighbor import Neighbor
from src.observer import Observer
import concurrent.futures
from concurrent.futures import ProcessPoolExecutor, as_completed

class Simulator:
    def __init__(self, shape, config, execID):
        self.shape = shape
        self.config = config
        self.format = {"entity": "Simulator"}
        self.execID = execID
        self.result = Result(self.shape, self.execID)
        self.numberNodes = 0
        self.nodeData = []
        self.distR = []
        self.distC = []

        # debug text file path
        directory = os.path.join("results", execID)
        self.debugFile = os.path.join(directory, "debug.txt")



    def loadNodesData(self):
        with open('src/data/transformed_node_data.csv', mode='r') as file:
            csv_reader = csv.reader(file)
            self.nodeData = [row for row in csv_reader]
            # to test with a smaller number of nodes
            # self.nodeData = random.sample([row for row in csv_reader], 500)


    def initNodes(self):
        self.nodes = [Node(0, "", 1, self.shape, self.shape.nbRows, self.config)]
        self.nodes.extend(
            Node(ID, row[0], 0, self.shape, int(row[3]), self.config)
            for ID, row in enumerate(self.nodeData, start=1)
        )
        self.numberNodes = len(self.nodes)
            

    def hashPeer(self, peerID, iteration):
        sha256 = hashlib.sha256(f"{peerID}{iteration}".encode()).hexdigest()
        return bin(int(sha256, 16))[-10:]


    def assignCustody(self):
        print("Starting to assign rows and columns to peers...")

        for node in self.nodes:
            if node.amIproposer:
                node.rowIDs, node.columnIDs = set(range(self.shape.nbRows)), set(range(self.shape.nbCols))
                continue
            
            total_custody = min(self.shape.minCustody + node.numValidators * self.shape.valCustody, self.shape.nbRows)
            # to test with a fixed number of rows and columns for all nodes
            # total_custody = self.shape.minCustody
            iteration = 0

            while len(node.rowIDs) < total_custody or len(node.columnIDs) < total_custody:
                binary_hash = self.hashPeer(node.nodeID, iteration)
                bit_type, index = int(binary_hash[-1]), int(binary_hash[:-1], 2)

                if bit_type == 0 and index < self.shape.nbRows and len(node.rowIDs) < total_custody:
                    node.rowIDs.add(index)
                elif bit_type == 1 and index < self.shape.nbCols and len(node.columnIDs) < total_custody:
                    node.columnIDs.add(index)

                iteration += 1

            with open(self.debugFile, "a") as file:
                file.write(f"Peer {node.ID} custody: rows {sorted(node.rowIDs)}, cols {sorted(node.columnIDs)}\n")

        print("Finished assigning rows and columns to peers.")


    def setCustodyBlockData(self):
        for node in self.nodes:
            node.setCustodyBlockData()
        print("Custody block data set.")


    def initNetwork(self):
        rowChannels = [[] for _ in range(self.shape.nbRows)]
        columnChannels = [[] for _ in range(self.shape.nbCols)]

        for node in self.nodes:
            if not node.amIproposer:
                for id in node.rowIDs:
                    rowChannels[id].append(node)
                for id in node.columnIDs:
                    columnChannels[id].append(node)

        with open(self.debugFile, "a") as file:
            for rowID, nodes in enumerate(rowChannels):
                node_ids = [node.ID for node in nodes]
                file.write(f"Row {rowID} nodes: {sorted(node_ids)}\n")
            for colID, nodes in enumerate(columnChannels):
                node_ids = [node.ID for node in nodes]
                file.write(f"Column {colID} nodes: {sorted(node_ids)}\n")

        self.distR = [len(channel) for channel in rowChannels]
        self.distC = [len(channel) for channel in columnChannels]

        def process_channels(channels, is_row=True):
            """Helper function to process row and column channels."""
            dim_size = self.shape.nbCols if is_row else self.shape.nbRows

            for idx, channel in enumerate(channels):
                if not channel:
                    if not is_row:
                        print(f"No nodes for column {idx}!")
                    continue

                degree = min(len(channel) - 1, self.shape.netDegree)
                G = nx.complete_graph(len(channel)) if degree >= len(channel) else nx.random_regular_graph(degree, len(channel))

                if not nx.is_connected(G):
                    print(f"Graph not connected for {'row' if is_row else 'column'} {idx}!")

                for u, v in G.edges:
                    node1, node2 = channel[u], channel[v]
                    neighbor_type = 0 if is_row else 1
                    node1_neighbors = node1.rowNeighbors if is_row else node1.columnNeighbors
                    node2_neighbors = node2.rowNeighbors if is_row else node2.columnNeighbors
                    
                    if idx not in node1_neighbors:
                        node1_neighbors[idx] = {}
                    if idx not in node2_neighbors:
                        node2_neighbors[idx] = {}

                    node1_neighbors[idx][node2.ID] = Neighbor(node2, neighbor_type, dim_size)
                    node2_neighbors[idx][node1.ID] = Neighbor(node1, neighbor_type, dim_size)

        process_channels(rowChannels, is_row=True)
        process_channels(columnChannels, is_row=False)

        for node in self.nodes:
            if node.amIproposer:
                for id in node.rowIDs:
                    count = min(self.shape.netDegree, len(rowChannels[id]))
                    publishTo = random.sample(rowChannels[id], count)
                    for vi in publishTo:
                        node.rowNeighbors[id].update({vi.ID : Neighbor(vi, 0, self.shape.nbCols)})
                for id in node.columnIDs:
                    count = min(self.shape.netDegree, len(columnChannels[id]))
                    publishTo = random.sample(columnChannels[id], count)
                    for vi in publishTo:
                        node.columnNeighbors[id].update({vi.ID : Neighbor(vi, 1, self.shape.nbRows)})

        with open(self.debugFile, "a") as file:
            for node in self.nodes:
                for rowID, neighbors in node.rowNeighbors.items():
                    neighbor_ids = [neighbor.node.ID for neighbor in neighbors.values()]
                    file.write(f"Node {node.ID} row {rowID} neighbors: {sorted(neighbor_ids)}\n")
                for colID, neighbors in node.columnNeighbors.items():
                    neighbor_ids = [neighbor.node.ID for neighbor in neighbors.values()]
                    file.write(f"Node {node.ID} column {colID} neighbors: {sorted(neighbor_ids)}\n")

        print("Network initialized.")


      
    def connectPeers(self):
        connections_range = self.shape.numPeers
        
        for peer in self.nodes:
            num_connections = random.randint(connections_range[0], connections_range[1])
            available_peers = [i for i in range(self.numberNodes)]
            
            for neighbor_dict in [peer.rowNeighbors, peer.columnNeighbors]:
                for inner_dict in neighbor_dict.values():
                    for peers in inner_dict.values():
                        peer.peerConnections.add(peers.node.ID)
            
            available_peers = list(set(available_peers) - peer.peerConnections)
            random.shuffle(available_peers)

            while len(peer.peerConnections) < num_connections and available_peers:
                other_peer = available_peers.pop()
                if other_peer != peer.ID and len(self.nodes[other_peer].peerConnections) < num_connections:
                    peer.peerConnections.add(other_peer)
                    self.nodes[other_peer].peerConnections.add(peer.ID)

            print(f"Node {peer.ID} peerConnections: {sorted(peer.peerConnections)}")

    
    def run(self):
        self.loadNodesData()
        self.initNodes()
        self.assignCustody()
        self.setCustodyBlockData()
        
        self.initNetwork()
        self.connectPeers()
     
        self.glob = Observer(self.shape)
        
        arrived, expected, ready = self.glob.checkStatus(self.nodes)
        missingSamples = expected - arrived
        missingVector = []
        progressVector = []
        steps = 0

        selectedRowID = random.randint(0, self.shape.nbRows-1)

        cnS = "samples received"
        cnN = "nodes ready"
        rcnS = "selected row samples received"
        rcnN = "selected row nodes ready"
        
        missingSamples, sampleProgress, nodeProgress = self.glob.getProgress(self.nodes)
        # for the nodes that have custody of the row, how many samples have they received for that row
        rowChannelMissingSamples, rowChannelSampleProgress, rowChannelNodeProgress = self.glob.getRowChannelProgress(self.nodes, selectedRowID)
        print("Start, arrived %0.02f %%, ready %0.02f %%"
                            % (sampleProgress*100, nodeProgress*100))
        print("Start, row channel %d, arrived %0.02f %%, ready %0.02f %%"
                            % (selectedRowID, rowChannelSampleProgress*100, rowChannelNodeProgress*100))

        with open(self.debugFile, "a") as file:
            file.write("Start, arrived %0.02f %%, ready %0.02f %%\n" % (sampleProgress*100, nodeProgress*100))

        
        progressDict = {
            cnS: sampleProgress,
            cnN: nodeProgress,
            rcnS: rowChannelSampleProgress,
            rcnN: rowChannelNodeProgress
        }
        
        progressVector.append(progressDict)

        while(True):
            missingVector.append(missingSamples)
            print("Expected Samples: %d" % expected)
            print("Missing Samples: %d" % missingSamples)
            with open(self.debugFile, "a") as file:
                file.write("Expected Samples: %d\n" % expected)
                file.write("Missing Samples: %d\n" % missingSamples)
            oldMissingSamples = missingSamples

            print("PHASE SEND %d" % steps)
            for node in self.nodes:
                node.send()

            print("PHASE RECEIVE %d" % steps)
            for node in self.nodes[1:]:
                node.receiveRowsColumns()
            
            print("PHASE RESTORE %d" % steps)
            for node in self.nodes[1:]:
                node.restoreRowsColumns()
            
            for node in self.nodes:
                node.updateStats()


            missingSamples, sampleProgress, nodeProgress = self.glob.getProgress(self.nodes)
            # for the nodes that have custody of the row, how many samples have they received for that row
            rowChannelMissingSamples, rowChannelSampleProgress, rowChannelNodeProgress = self.glob.getRowChannelProgress(self.nodes, selectedRowID)
            print("step %d, arrived %0.02f %%, ready %0.02f %%"
                              % (steps, sampleProgress*100, nodeProgress*100))
            print("step %d, row channel %d, arrived %0.02f %%, ready %0.02f %%"
                                % (steps, selectedRowID, rowChannelSampleProgress*100, rowChannelNodeProgress*100))

            with open(self.debugFile, "a") as file:
                file.write("step %d, arrived %0.02f %%, ready %0.02f %%\n" % (steps, sampleProgress*100, nodeProgress*100))

            
            progressDict = {
                cnS: sampleProgress,
                cnN: nodeProgress,
                rcnS: rowChannelSampleProgress,
                rcnN: rowChannelNodeProgress
            }
            
            progressVector.append(progressDict)

            if missingSamples == 0:
                print("The entire block is available at step %d !" % (steps))
                missingVector.append(missingSamples)
                break

            steps += 1
        


        progress = pd.DataFrame(progressVector)
        self.result.addMetric("rowDist", self.distR)
        self.result.addMetric("columnDist", self.distC)
        self.result.addMetric("progress", progress.to_dict(orient='list'))
        self.result.populate(self.shape, self.config, missingVector)
        self.result.copyNodes(self.nodes)
        return self.result

