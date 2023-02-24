#!/bin/python3

import random
import collections
import logging
import sys
from DAS.block import *
from bitarray import bitarray
from bitarray.util import zeros
from collections import deque
from itertools import chain

def shuffled(lis, shuffle=True):
    ''' Generator yielding list in shuffled order
    '''
    # based on https://stackoverflow.com/a/60342323
    if shuffle:
        for index in random.sample(range(len(lis)), len(lis)):
            yield lis[index]
    else:
        for v in lis:
            yield v
def shuffledDict(d, shuffle=True):
    ''' Generator yielding dictionary in shuffled order

        Shuffle, except if not (optional parameter useful for experiment setup)
    '''
    if shuffle:
        lis = list(d.items())
        for index in random.sample(range(len(d)), len(d)):
            yield lis[index]
    else:
        for kv in d.items():
            yield kv

def sampleLine(line, limit):
    """ sample up to 'limit' bits from a bitarray

    Since this is quite expensive, we use a number of heuristics to get it fast.
    """
    if limit == sys.maxsize :
        return line
    else:
        w = line.count(1)
        if limit >= w :
            return line
        else:
            l = len(line)
            r = zeros(l)
            if w < l/10 or limit > l/2 :
                indices = [ i for i in range(l) if line[i] ]
                sample = random.sample(indices, limit)
                for i in sample:
                    r[i] = 1
                return r
            else:
                while limit:
                    i = random.randrange(0, l)
                    if line[i] and not r[i]:
                        r[i] = 1
                        limit -= 1
                return r

class NextToSend:
    def __init__(self, neigh, toSend, id, dim):
        self.neigh = neigh
        self.toSend = toSend
        self.id = id
        self.dim = dim

class SegmentToSend:
    def __init__(self, dim, id, i):
        self.dim = dim
        self.id = id
        self.i = i

class Neighbor:
    """This class implements a node neighbor to monitor sent and received data."""

    def __repr__(self):
        """It returns the amount of sent and received data."""
        return "%d:%d/%d, q:%d" % (self.node.ID, self.sent.count(1), self.received.count(1), len(self.sendQueue))

    def __init__(self, v, dim, blockSize):
        """It initializes the neighbor with the node and sets counters to zero."""
        self.node = v
        self.dim = dim # 0:row 1:col
        self.receiving = zeros(blockSize)
        self.received = zeros(blockSize)
        self.sent = zeros(blockSize)
        self.sendQueue = deque()


class Validator:
    """This class implements a validator/node in the network."""

    def __repr__(self):
        """It returns the validator ID."""
        return str(self.ID)

    def __init__(self, ID, amIproposer, logger, shape, rows, columns):
        """It initializes the validator with the logger, shape and assigned rows/columns."""
        self.shape = shape
        FORMAT = "%(levelname)s : %(entity)s : %(message)s"
        self.ID = ID
        self.format = {"entity": "Val "+str(self.ID)}
        self.block = Block(self.shape.blockSize)
        self.receivedBlock = Block(self.shape.blockSize)
        self.receivedQueue = deque()
        self.sendQueue = deque()
        self.amIproposer = amIproposer
        self.logger = logger
        if self.shape.chi < 1:
            self.logger.error("Chi has to be greater than 0", extra=self.format)
        elif self.shape.chi > self.shape.blockSize:
            self.logger.error("Chi has to be smaller than %d" % blockSize, extra=self.format)
        else:
            if amIproposer:
                self.rowIDs = range(shape.blockSize)
                self.columnIDs = range(shape.blockSize)
            else:
                self.rowIDs = rows[(self.ID*self.shape.chi):(self.ID*self.shape.chi + self.shape.chi)]
                self.columnIDs = columns[(self.ID*self.shape.chi):(self.ID*self.shape.chi + self.shape.chi)]
                #if shape.deterministic:
                #    random.seed(self.ID)
                #self.rowIDs = random.sample(range(self.shape.blockSize), self.shape.chi)
                #self.columnIDs = random.sample(range(self.shape.blockSize), self.shape.chi)
        self.rowNeighbors = collections.defaultdict(dict)
        self.columnNeighbors = collections.defaultdict(dict)

        #statistics
        self.statsTxInSlot = 0
        self.statsTxPerSlot = []
        self.statsRxInSlot = 0
        self.statsRxPerSlot = []

        # Set uplink bandwidth. In segments (~560 bytes) per timestep (50ms?)
        # 1 Mbps ~= 1e6 / 20 / 8 / 560 ~= 11
        # TODO: this should be a parameter
        self.bwUplink = 110 if not self.amIproposer else 2200 # approx. 10Mbps and 200Mbps

        self.repairOnTheFly = True
        self.sendLineUntil = (self.shape.blockSize + 1) // 2 # stop sending on a p2p link if at least this amount of samples passed
        self.perNeighborQueue = True # queue incoming messages to outgoing connections on arrival (as typical GossipSub impl)
        self.perNodeQueue = False # keep a global queue of incoming messages for later sequential dispatch
        self.shuffleLines = True # shuffle the order of rows/columns in each iteration while trying to send
        self.shuffleNeighbors = True # shuffle the order of neighbors when sending the same segment to each neighbor
        self.dumbRandomScheduler = False # dumb random scheduler
        self.segmentShuffleScheduler = True # send each segment that's worth sending once in shuffled order, then repeat
        self.segmentShuffleSchedulerPersist = True # Persist scheduler state between timesteps

    def logIDs(self):
        """It logs the assigned rows and columns."""
        if self.amIproposer == 1:
            self.logger.warning("I am a block proposer."% self.ID)
        else:
            self.logger.debug("Selected rows: "+str(self.rowIDs), extra=self.format)
            self.logger.debug("Selected columns: "+str(self.columnIDs), extra=self.format)

    def initBlock(self):
        """It initializes the block for the proposer."""
        if self.amIproposer == 1:
            self.logger.debug("I am a block proposer.", extra=self.format)
            self.block = Block(self.shape.blockSize)
            self.block.fill()
            #self.block.print()
        else:
            self.logger.warning("I am not a block proposer."% self.ID)

    def broadcastBlock(self):
        """The block proposer broadcasts the block to all validators."""
        if self.amIproposer == 0:
            self.logger.warning("I am not a block proposer", extra=self.format)
        else:
            self.logger.debug("Broadcasting my block...", extra=self.format)
            order = [i for i in range(self.shape.blockSize * self.shape.blockSize)]
            random.shuffle(order)
            while(order):
                i = order.pop()
                if (random.randint(0,99) >= self.shape.failureRate):
                    self.block.data[i] = 1
                else:
                    self.block.data[i] = 0

            nbFailures = self.block.data.count(0)
            measuredFailureRate = nbFailures * 100 / (self.shape.blockSize * self.shape.blockSize)
            self.logger.debug("Number of failures: %d (%0.02f %%)", nbFailures, measuredFailureRate, extra=self.format)
            #broadcasted.print()

    def getColumn(self, index):
        """It returns a given column."""
        return self.block.getColumn(index)

    def getRow(self, index):
        """It returns a given row."""
        return self.block.getRow(index)

    def receiveSegment(self, rID, cID, src):
        # register receive so that we are not sending back
        if rID in self.rowIDs:
            if src in self.rowNeighbors[rID]:
                self.rowNeighbors[rID][src].receiving[cID] = 1
        if cID in self.columnIDs:
            if src in self.columnNeighbors[cID]:
                self.columnNeighbors[cID][src].receiving[rID] = 1
        if not self.receivedBlock.getSegment(rID, cID):
            self.logger.debug("Recv new: %d->%d: %d,%d", src, self.ID, rID, cID, extra=self.format)
            self.receivedBlock.setSegment(rID, cID)
            if self.perNodeQueue or self.perNeighborQueue:
                self.receivedQueue.append((rID, cID))
        else:
            self.logger.debug("Recv DUP: %d->%d: %d,%d", src, self.ID, rID, cID, extra=self.format)
        #     self.statsRxDuplicateInSlot += 1
        self.statsRxInSlot += 1

    def addToSendQueue(self, rID, cID):
        if self.perNodeQueue:
            self.sendQueue.append((rID, cID))

        if self.perNeighborQueue:
            if rID in self.rowIDs:
                for neigh in self.rowNeighbors[rID].values():
                    neigh.sendQueue.append(cID)

            if cID in self.columnIDs:
                for neigh in self.columnNeighbors[cID].values():
                    neigh.sendQueue.append(rID)

    def receiveRowsColumns(self):
        """It receives rows and columns."""
        if self.amIproposer == 1:
            self.logger.error("I am a block proposer", extra=self.format)
        else:
            self.logger.debug("Receiving the data...", extra=self.format)
            #self.logger.debug("%s -> %s", self.block.data, self.receivedBlock.data, extra=self.format)

            self.block.merge(self.receivedBlock)

            for neighs in chain (self.rowNeighbors.values(), self.columnNeighbors.values()):
                for neigh in neighs.values():
                    neigh.received |= neigh.receiving
                    neigh.receiving.setall(0)

            # add newly received segments to the send queue
            if self.perNodeQueue or self.perNeighborQueue:
                while self.receivedQueue:
                    (rID, cID) = self.receivedQueue.popleft()
                    self.addToSendQueue(rID, cID)

    def updateStats(self):
        """It updates the stats related to sent and received data."""
        self.logger.debug("Stats: tx %d, rx %d", self.statsTxInSlot, self.statsRxInSlot, extra=self.format)
        self.statsRxPerSlot.append(self.statsRxInSlot)
        self.statsTxPerSlot.append(self.statsTxInSlot)
        self.statsRxInSlot = 0
        self.statsTxInSlot = 0

    def sendSegmentToNeigh(self, rID, cID, neigh):
        if (neigh.sent | neigh.received).count(1) >= self.sendLineUntil:
            return False # sent enough, other side can restore
        if neigh.dim == 0: #row
            i = cID
        else:
            i = rID
        if not neigh.sent[i] and not neigh.received[i] :
            neigh.sent[i] = 1
            neigh.node.receiveSegment(rID, cID, self.ID)
            self.statsTxInSlot += 1
            return True
        else:
            return False # received or already sent

    def processSendQueue(self):
        while self.sendQueue:
            (rID, cID) = self.sendQueue[0]

            if rID in self.rowIDs:
                for _, neigh in shuffledDict(self.rowNeighbors[rID], self.shuffleNeighbors):
                    self.sendSegmentToNeigh(rID, cID, neigh)

                if self.statsTxInSlot >= self.bwUplink:
                    return

            if cID in self.columnIDs:
                for _, neigh in shuffledDict(self.columnNeighbors[cID], self.shuffleNeighbors):
                    self.sendSegmentToNeigh(rID, cID, neigh)

                if self.statsTxInSlot >= self.bwUplink:
                    return

            self.sendQueue.popleft()

    def processPerNeighborSendQueue(self):
        progress = True
        while (progress):
            progress = False
            for rID, neighs in shuffledDict(self.rowNeighbors, self.shuffleLines):
                for _, neigh in shuffledDict(neighs, self.shuffleNeighbors):
                    if (neigh.sendQueue):
                        self.sendSegmentToNeigh(rID, neigh.sendQueue.popleft(), neigh)
                        progress = True
                    if self.statsTxInSlot >= self.bwUplink:
                        return

            for cID, neighs in shuffledDict(self.columnNeighbors, self.shuffleLines):
                for _, neigh in shuffledDict(neighs, self.shuffleNeighbors):
                    if (neigh.sendQueue):
                        self.sendSegmentToNeigh(neigh.sendQueue.popleft(), cID, neigh)
                        progress = True
                    if self.statsTxInSlot >= self.bwUplink:
                        return

    def runSegmentShuffleScheduler(self):
            # This scheduler check which owned segments needs sending (at least
            # one neighbor needing it). Then it sends each segment that's worth sending
            # once, in shuffled order. This is repeated until bw limit.
            while True:
                if hasattr(self, 'segmentShuffleGen') and self.segmentShuffleGen is not None:
                    #self.logger.debug("TX:%d queue:%d", self.statsTxInSlot, len(self.segmentsToSend), extra=self.format)
                    for s in self.segmentShuffleGen:
                        self.logger.debug("%d:%d/%d", s.dim, s.id, s.i, extra=self.format)
                        if s.dim == 0:
                            for _, neigh in shuffledDict(self.rowNeighbors[s.id], self.shuffleNeighbors):
                                self.logger.debug("%d or %d", neigh.sent[s.i], neigh.received[s.i], extra=self.format)
                                if self.sendSegmentToNeigh(s.id, s.i, neigh):
                                    self.logger.debug("sending to %d", neigh.node.ID, extra=self.format)
                                    break
                        else:
                            for _, neigh in shuffledDict(self.columnNeighbors[s.id], self.shuffleNeighbors):
                                self.logger.debug("%d or %d", neigh.sent[s.i], neigh.received[s.i], extra=self.format)
                                if self.sendSegmentToNeigh(s.i, s.id, neigh):
                                    self.logger.debug("sending to %d", neigh.node.ID, extra=self.format)
                                    break

                        if self.statsTxInSlot >= self.bwUplink:
                            if not self.segmentShuffleSchedulerPersist:
                                # remove scheduler state before leaving
                                self.segmentsToSend = []
                                self.segmentShuffleGen = None
                            return

                self.segmentsToSend = []
                for rID, neighs in self.rowNeighbors.items():
                    line = self.getRow(rID)
                    needed = zeros(self.shape.blockSize)
                    for neigh in neighs.values():
                        sentOrReceived = neigh.received | neigh.sent
                        if sentOrReceived.count(1) < self.sendLineUntil:
                            needed |= ~sentOrReceived
                    needed &= line
                    if (needed).any():
                        for i in range(len(needed)):
                            if needed[i]:
                                self.segmentsToSend.append(SegmentToSend(0, rID, i))

                for cID, neighs in self.columnNeighbors.items():
                    line = self.getColumn(cID)
                    needed = zeros(self.shape.blockSize)
                    for neigh in neighs.values():
                        sentOrReceived = neigh.received | neigh.sent
                        if sentOrReceived.count(1) < self.sendLineUntil:
                            needed |= ~sentOrReceived
                    needed &= line
                    if (needed).any():
                        for i in range(len(needed)):
                            if needed[i]:
                                self.segmentsToSend.append(SegmentToSend(1, cID, i))

                if not self.segmentsToSend:
                    break
                else:
                    self.segmentShuffleGen = shuffled(self.segmentsToSend, self.shuffleLines)

    def runDumbRandomScheduler(self, tries = 100):
            # dumb random scheduler picking segments at random and trying to send it
            t = tries
            while t:
                if self.rowIDs:
                    rID = random.choice(self.rowIDs)
                    cID = random.randrange(0, self.shape.blockSize)
                    if self.block.getSegment(rID, cID) :
                        neigh = random.choice(list(self.rowNeighbors[rID].values()))
                        if not neigh.sent[cID] and not neigh.received[cID] :
                            neigh.sent[cID] = 1
                            neigh.node.receiveSegment(rID, cID, self.ID)
                            self.statsTxInSlot += 1
                            t = tries
                if self.statsTxInSlot >= self.bwUplink:
                    return
                if self.columnIDs:
                    cID = random.choice(self.columnIDs)
                    rID = random.randrange(0, self.shape.blockSize)
                    if self.block.getSegment(rID, cID) :
                        neigh = random.choice(list(self.columnNeighbors[cID].values()))
                        if not neigh.sent[rID] and not neigh.received[rID] :
                            neigh.sent[rID] = 1
                            neigh.node.receiveSegment(rID, cID, self.ID)
                            self.statsTxInSlot += 1
                            t = tries
                t -= 1
                if self.statsTxInSlot >= self.bwUplink:
                    return
            return

    def send(self):
        """ Send as much as we can in the timeslot, limited by bwUplink
        """

        # process node level send queue
        self.processSendQueue()

        # process neighbor level send queues in shuffled breadth-first order
        self.processPerNeighborSendQueue()

        # process possible segments to send in shuffled breadth-first order
        if self.segmentShuffleScheduler:
            self.runSegmentShuffleScheduler()

        if self.dumbRandomScheduler:
            self.runDumbRandomScheduler()

    def logRows(self):
        """It logs the rows assigned to the validator."""
        if self.logger.isEnabledFor(logging.DEBUG):
            for id in self.rowIDs:
                self.logger.debug("Row %d: %s", id, self.getRow(id), extra=self.format)

    def logColumns(self):
        """It logs the columns assigned to the validator."""
        if self.logger.isEnabledFor(logging.DEBUG):
            for id in self.columnIDs:
                self.logger.debug("Column %d: %s", id, self.getColumn(id), extra=self.format)

    def restoreRows(self):
        """It restores the rows assigned to the validator, that can be repaired."""
        if self.repairOnTheFly:
            for id in self.rowIDs:
                rep = self.block.repairRow(id)
                if (rep.any()):
                    # If operation is based on send queues, segments should
                    # be queued after successful repair.
                    for i in range(len(rep)):
                        if rep[i]:
                            self.logger.debug("Rep: %d,%d", id, i, extra=self.format)
                            self.addToSendQueue(id, i)
                    # self.statsRepairInSlot += rep.count(1)

    def restoreColumns(self):
        """It restores the columns assigned to the validator, that can be repaired."""
        if self.repairOnTheFly:
            for id in self.columnIDs:
                rep = self.block.repairColumn(id)
                if (rep.any()):
                    # If operation is based on send queues, segments should
                    # be queued after successful repair.
                    for i in range(len(rep)):
                        if rep[i]:
                            self.logger.debug("Rep: %d,%d", i, id, extra=self.format)
                            self.addToSendQueue(i, id)
                    # self.statsRepairInSlot += rep.count(1)

    def checkStatus(self):
        """It checks how many expected/arrived samples are for each assigned row/column."""
        arrived = 0
        expected = 0
        for id in self.columnIDs:
            line = self.getColumn(id)
            arrived += line.count(1)
            expected += len(line)
        for id in self.rowIDs:
            line = self.getRow(id)
            arrived += line.count(1)
            expected += len(line)
        self.logger.debug("status: %d / %d", arrived, expected, extra=self.format)

        return (arrived, expected)
