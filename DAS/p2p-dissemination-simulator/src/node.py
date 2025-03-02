import random
import collections
from src.neighbor import Neighbor
from src.tools import shuffled, shuffledDict
from src.block import Block
from collections import deque
from itertools import chain
from bitarray.util import zeros

class Node:
    def __init__(self, ID, nodeID, amIproposer, shape, numValidators, config):
        self.shape = shape
        self.ID = ID
        self.nodeID = nodeID
        self.amIproposer = amIproposer
        self.numValidators = numValidators
        self.config = config

        self.peerConnections = set()
       
        self.block = Block(self.shape.nbCols, self.shape.nbColsK, self.shape.nbRows,  self.shape.nbRowsK)
        self.receivedBlock = Block(self.shape.nbCols, self.shape.nbColsK, self.shape.nbRows,  self.shape.nbRowsK)
        self.receivedQueue = deque()
        self.sendQueue = deque()
        
        if amIproposer:
            self.rowIDs = range(shape.nbRows)
            self.columnIDs = range(shape.nbCols)
        else:
            self.rowIDs = set()
            self.columnIDs = set()

        self.statsTxInSlot = 0
        
        self.rowNeighbors = collections.defaultdict(dict)
        self.columnNeighbors = collections.defaultdict(dict)

        if self.amIproposer:
            self.bwUplink = self.shape.bwUplinkProd
        else:
            self.bwUplink = self.shape.bwUplink
        
        self.bwUplink *= 1e3 / 8 * self.config.stepDuration / self.config.segmentSize
        

    def __repr__(self):
        return f"Node({self.nodeID})"
    

    def setCustodyBlockData(self):
        if self.amIproposer:
            self.block.fill()

        elif self.config.verticalDissemination:
            for rowID in self.rowIDs:
                for colID in range(self.shape.nbCols):
                    self.block.setSegment(rowID, colID)
                    

    def addToSendQueue(self, rID, cID):
        self.sendQueue.append((rID, cID))

        if rID in self.rowIDs:
            for neigh in self.rowNeighbors[rID].values():
                neigh.sendQueue.append(cID)

        if cID in self.columnIDs:
            for neigh in self.columnNeighbors[cID].values():
                neigh.sendQueue.append(rID)


    def checkSegmentToNeigh(self, rID, cID, neigh):
        if (neigh.sent | neigh.received).count(1) >= (self.shape.nbColsK if neigh.dim else self.shape.nbRowsK):
            return False
        i = rID if neigh.dim else cID
        if not neigh.sent[i] and not neigh.received[i] :
            return True

    def sendSegmentToNeigh(self, rID, cID, neigh):
        i = rID if neigh.dim else cID
        neigh.sent[i] = 1
        neigh.node.receiveSegment(rID, cID, self.ID)
        self.statsTxInSlot += 1
        

    def checkSendSegmentToNeigh(self, rID, cID, neigh):
        if self.checkSegmentToNeigh(rID, cID, neigh):
            self.sendSegmentToNeigh(rID, cID, neigh)
            return True
        else:
            return False


    def processSendQueue(self):
        while self.sendQueue:
            (rID, cID) = self.sendQueue[0]

            if rID in self.rowIDs:
                for _, neigh in shuffledDict(self.rowNeighbors[rID]):
                    self.checkSendSegmentToNeigh(rID, cID, neigh)

                if self.statsTxInSlot >= self.bwUplink:
                    return

            if cID in self.columnIDs:
                for _, neigh in shuffledDict(self.columnNeighbors[cID]):
                    self.checkSendSegmentToNeigh(rID, cID, neigh)

                if self.statsTxInSlot >= self.bwUplink:
                    return

            self.sendQueue.popleft()

    def processPerNeighborSendQueue(self):
        progress = True
        while (progress):
            progress = False

            queues = []
            for rID, neighs in self.rowNeighbors.items():
                for neigh in neighs.values():
                    if (neigh.sendQueue):
                        queues.append((0, rID, neigh))

            for cID, neighs in self.columnNeighbors.items():
                for neigh in neighs.values():
                    if (neigh.sendQueue):
                        queues.append((1, cID, neigh))

            for dim, lineID, neigh in shuffled(queues):
                if dim == 0:
                    self.checkSendSegmentToNeigh(lineID, neigh.sendQueue.popleft(), neigh)
                else:
                    self.checkSendSegmentToNeigh(neigh.sendQueue.popleft(), lineID, neigh)
                progress = True
                if self.statsTxInSlot >= self.bwUplink:
                    return


    def receiveRowsColumns(self):
        self.block.merge(self.receivedBlock)

        for neighs in chain (self.rowNeighbors.values(), self.columnNeighbors.values()):
            for neigh in neighs.values():
                neigh.received |= neigh.receiving
                neigh.receiving.setall(0)

        while self.receivedQueue:
            (rID, cID) = self.receivedQueue.popleft()
            self.addToSendQueue(rID, cID)

    def receiveSegment(self, rID, cID, src):
        if rID in self.rowIDs:
            if src in self.rowNeighbors[rID]:
                self.rowNeighbors[rID][src].receiving[cID] = 1
        if cID in self.columnIDs:
            if src in self.columnNeighbors[cID]:
                self.columnNeighbors[cID][src].receiving[rID] = 1
        if not self.receivedBlock.getSegment(rID, cID):
            self.receivedBlock.setSegment(rID, cID)
            self.receivedQueue.append((rID, cID))
        

    def updateStats(self):
        self.statsTxInSlot = 0

    def runSegmentShuffleScheduler(self):
        """ Schedule chunks for sending.

        This scheduler check which owned segments needs sending (at least
        one neighbor needing it). Then it sends each segment that's worth sending
        once, in shuffled order. This is repeated until bw limit.
        """

        def collectSegmentsToSend():
            # yields list of segments to send as (dim, lineID, id)
            segmentsToSend = []
            for rID, neighs in self.rowNeighbors.items():
                line = self.getRow(rID)
                needed = zeros(self.shape.nbCols)
                for neigh in neighs.values():
                    sentOrReceived = neigh.received | neigh.sent
                    if sentOrReceived.count(1) < self.shape.nbColsK:
                        needed |= ~sentOrReceived
                needed &= line
                if (needed).any():
                    for i in range(len(needed)):
                        if needed[i]:
                            segmentsToSend.append((0, rID, i))

            for cID, neighs in self.columnNeighbors.items():
                line = self.getColumn(cID)
                needed = zeros(self.shape.nbRows)
                for neigh in neighs.values():
                    sentOrReceived = neigh.received | neigh.sent
                    if sentOrReceived.count(1) < self.shape.nbRowsK:
                        needed |= ~sentOrReceived
                needed &= line
                if (needed).any():
                    for i in range(len(needed)):
                        if needed[i]:
                            segmentsToSend.append((1, cID, i))
            return segmentsToSend

        def nextSegment():
            while True:
                # send each collected segment once
                if hasattr(self, 'segmentShuffleGen') and self.segmentShuffleGen is not None:
                    for dim, lineID, id in self.segmentShuffleGen:
                        if dim == 0:
                            for _, neigh in shuffledDict(self.rowNeighbors[lineID]):
                                if self.checkSegmentToNeigh(lineID, id, neigh):
                                    yield((lineID, id, neigh))
                                    break
                        else:
                            for _, neigh in shuffledDict(self.columnNeighbors[lineID]):
                                if self.checkSegmentToNeigh(id, lineID, neigh):
                                    yield((id, lineID, neigh))
                                    break

                # collect segments for next round
                segmentsToSend = collectSegmentsToSend()

                # finish if empty  or set up shuffled generator based on collected segments
                if not segmentsToSend:
                    break
                else:
                    self.segmentShuffleGen = shuffled(segmentsToSend)

        for rid, cid, neigh in nextSegment():
            # segments are checked just before yield, so we can send directly
            self.sendSegmentToNeigh(rid, cid, neigh)

            if self.statsTxInSlot >= self.bwUplink:
                if not self.segmentShuffleSchedulerPersist:
                    # remove scheduler state before leaving
                    self.segmentShuffleGen = None
                return


    def send(self):
        self.processSendQueue()
        if self.statsTxInSlot >= self.bwUplink:
            return

        self.processPerNeighborSendQueue()
        if self.statsTxInSlot >= self.bwUplink:
            return
        
        self.runSegmentShuffleScheduler()
        if self.statsTxInSlot >= self.bwUplink:
            return

    
    def restoreRowsColumns(self):
        self.restoreRows()
        self.restoreColumns()


    def restoreRows(self):
        for id in self.rowIDs:
            self.restoreRow(id)

    def restoreRow(self, id):
        rep = self.block.repairRow(id)
        if (rep.any()):
            for i in range(len(rep)):
                if rep[i]:
                    self.addToSendQueue(id, i)
           
    def restoreColumns(self):
        for id in self.columnIDs:
            self.restoreColumn(id)

    def restoreColumn(self, id):
        rep = self.block.repairColumn(id)
        if (rep.any()):
            for i in range(len(rep)):
                if rep[i]:
                    self.addToSendQueue(i, id)

    def getColumn(self, index):
        return self.block.getColumn(index)

    def getRow(self, index):
        return self.block.getRow(index)
    
    def checkStatus(self):
        def checkStatus(columnIDs, rowIDs):
            arrived = 0
            expected = 0
            for id in columnIDs:
                line = self.getColumn(id)
                arrived += line.count(1)
                expected += len(line)
            for id in rowIDs:
                line = self.getRow(id)
                arrived += line.count(1)
                expected += len(line)
            return arrived, expected

        arrived, expected = checkStatus(self.columnIDs, self.rowIDs)
        
        return arrived, expected