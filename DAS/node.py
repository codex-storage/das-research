#!/bin/python3

import random
import collections
import logging
from collections import defaultdict
import threading
from DAS.block import *
from DAS.tools import shuffled, shuffledDict, unionOfSamples
from bitarray.util import zeros
from collections import deque
from itertools import chain

class Neighbor:
    """This class implements a node neighbor to monitor sent and received data.

    It represents one side of a P2P link in the overlay. Sent and received
    segments are monitored to avoid sending twice or sending back what was
    received from a link.
    """

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
    def __init__(self, rowIDs, columnIDs):
        self.rowIDs = rowIDs
        self.columnIDs = columnIDs

def initValidator(nbRows, custodyRows, nbCols, custodyCols):
        rowIDs = set(random.sample(range(nbRows), custodyRows))
        columnIDs = set(random.sample(range(nbCols), custodyCols))
        return Validator(rowIDs, columnIDs)

class Node:
    """This class implements a node in the network."""

    def __repr__(self):
        """It returns the node ID."""
        return str(self.ID)

    def __init__(self, ID, amIproposer, amImalicious, logger, shape, config,
                 validators, rows = set(), columns = set()):
        """It initializes the node, and eventual validators, following the simulation configuration in shape and config.

            If rows/columns are specified these are observed, otherwise (default)
            custodyRows rows and custodyCols columns are selected randomly.
        """

        self.shape = shape
        FORMAT = "%(levelname)s : %(entity)s : %(message)s"
        self.ID = ID
        self.format = {"entity": "Val "+str(self.ID)}
        self.block = Block(self.shape.nbCols, self.shape.nbColsK, self.shape.nbRows,  self.shape.nbRowsK)
        self.receivedBlock = Block(self.shape.nbCols, self.shape.nbColsK, self.shape.nbRows,  self.shape.nbRowsK)
        self.receivedQueue = deque()
        self.sendQueue = deque()
        self.amIproposer = amIproposer
        self.amImalicious = amImalicious
        self.amIaddedToQueue = 0
        self.msgSentCount = 0
        self.msgRecvCount = 0
        self.sampleSentCount = 0
        self.sampleRecvCount = 0
        self.restoreRowCount = 0
        self.restoreColumnCount = 0
        self.repairedSampleCount = 0
        self.logger = logger
        self.validators = validators
        self.received_gossip = defaultdict(list)

        if amIproposer:
            self.nodeClass = 0
            self.rowIDs = range(shape.nbRows)
            self.columnIDs = range(shape.nbCols)
        else:
            self.nodeClass = 1 if (self.ID <= shape.numberNodes * shape.class1ratio) else 2
            self.vpn = len(validators)  #TODO: needed by old code, change to fn

            self.rowIDs = set(rows)
            self.columnIDs = set(columns)
            if config.validatorBasedCustody:
                for v in validators:
                    self.rowIDs = self.rowIDs.union(v.rowIDs)
                    self.columnIDs = self.columnIDs.union(v.columnIDs)
            else:
                if (self.vpn * self.shape.custodyRows) > self.shape.nbRows:
                    self.logger.warning("Row custody (*vpn) larger than number of rows!", extra=self.format)
                    self.rowIDs = range(self.shape.nbRows)
                else:
                    self.rowIDs = set(random.sample(range(self.shape.nbRows), self.vpn*self.shape.custodyRows))

                if (self.vpn * self.shape.custodyCols) > self.shape.nbCols:
                    self.logger.warning("Column custody (*vpn) larger than number of columns!", extra=self.format)
                    self.columnIDs = range(self.shape.nbCols)
                else:
                    self.columnIDs = set(random.sample(range(self.shape.nbCols), self.vpn*self.shape.custodyCols))

        self.rowNeighbors = collections.defaultdict(dict)
        self.columnNeighbors = collections.defaultdict(dict)

        #statistics
        self.statsTxInSlot = 0
        self.statsTxPerSlot = []
        self.statsRxInSlot = 0
        self.statsRxPerSlot = []
        self.statsRxDupInSlot = 0
        self.statsRxDupPerSlot = []

        # Set uplink bandwidth.
        # Assuming segments of ~560 bytes and timesteps of 50ms, we get
        # 1 Mbps ~= 1e6 mbps * 0.050 s / (560*8) bits ~= 11 segments/timestep
        if self.amIproposer:
            self.bwUplink = shape.bwUplinkProd
        elif self.nodeClass == 1:
            self.bwUplink = shape.bwUplink1
        else:
            self.bwUplink = shape.bwUplink2
        self.bwUplink *= 1e3 / 8 * config.stepDuration / config.segmentSize

        self.repairOnTheFly = config.evalConf(self, config.repairOnTheFly, shape)
        self.sendLineUntilR = config.evalConf(self, config.sendLineUntilR, shape) # stop sending on a p2p link if at least this amount of samples passed
        self.sendLineUntilC = config.evalConf(self, config.sendLineUntilC, shape) # stop sending on a p2p link if at least this amount of samples passed
        self.perNeighborQueue = config.evalConf(self, config.perNeighborQueue, shape) # queue incoming messages to outgoing connections on arrival (as typical GossipSub impl)
        self.shuffleQueues = config.evalConf(self, config.shuffleQueues, shape) # shuffle the order of picking from active queues of a sender node
        self.perNodeQueue = config.evalConf(self, config.perNodeQueue, shape) # keep a global queue of incoming messages for later sequential dispatch
        self.shuffleLines = config.evalConf(self, config.shuffleLines, shape) # shuffle the order of rows/columns in each iteration while trying to send
        self.shuffleNeighbors = config.evalConf(self, config.shuffleNeighbors, shape) # shuffle the order of neighbors when sending the same segment to each neighbor
        self.dumbRandomScheduler = config.evalConf(self, config.dumbRandomScheduler, shape) # dumb random scheduler
        self.segmentShuffleScheduler = config.evalConf(self, config.segmentShuffleScheduler, shape) # send each segment that's worth sending once in shuffled order, then repeat
        self.segmentShuffleSchedulerPersist = config.evalConf(self, config.segmentShuffleSchedulerPersist, shape) # Persist scheduler state between timesteps
        self.queueAllOnInit = config.evalConf(self, config.queueAllOnInit, shape) # queue up everything in the block producer, without shuffling, at the very beginning 
        self.forwardOnReceive = config.evalConf(self, config.forwardOnReceive, shape) # forward segments as soon as received
        self.forwardWhenLineReceived = config.evalConf(self, config.forwardWhenLineReceived, shape) # forward all segments when full line available (repaired segments are always forwarded)

    def logIDs(self):
        """It logs the assigned rows and columns."""
        if self.amIproposer == 1:
            self.logger.warning("I am a block proposer.", extra=self.format)
        else:
            self.logger.debug("Selected rows: "+str(self.rowIDs), extra=self.format)
            self.logger.debug("Selected columns: "+str(self.columnIDs), extra=self.format)

    def initBlock(self):
        """It initializes the block for the proposer."""
        if self.amIproposer == 0:
            self.logger.warning("I am not a block proposer", extra=self.format)
        else:
            self.logger.debug("Creating block...", extra=self.format)
            if self.shape.failureModel == "random":
                order = [i for i in range(self.shape.nbCols * self.shape.nbRows)]
                order = random.sample(order, int((1 - self.shape.failureRate/100) * len(order)))
                for i in order:
                    self.block.data[i] = 1
            elif self.shape.failureModel == "sequential":
                order = [i for i in range(self.shape.nbCols * self.shape.nbRows)]
                order = order[:int((1 - self.shape.failureRate/100) * len(order))]
                for i in order:
                    self.block.data[i] = 1
            elif self.shape.failureModel == "MEP": # Minimal size non-recoverable Erasure Pattern
                for r in range(self.shape.nbCols):
                    for c in range(self.shape.nbRows):
                        if r > self.shape.nbColsK or c > self.shape.nbRowsK:
                            self.block.setSegment(r,c)
            elif self.shape.failureModel == "MEP+1": # MEP +1 segment to make it recoverable
                for r in range(self.shape.nbCols):
                    for c in range(self.shape.nbRows):
                        if r > self.shape.nbColsK or c > self.shape.nbRowsK:
                            self.block.setSegment(r,c)
                self.block.setSegment(0, 0)
            elif self.shape.failureModel == "DEP":
                assert(self.shape.nbCols == self.shape.nbRows and self.shape.nbColsK == self.shape.nbRowsK)
                for r in range(self.shape.nbCols):
                    for c in range(self.shape.nbRows):
                        if (r+c) % self.shape.nbCols > self.shape.nbColsK:
                            self.block.setSegment(r,c)
            elif self.shape.failureModel == "DEP+1":
                assert(self.shape.nbCols == self.shape.nbRows and self.shape.nbColsK == self.shape.nbRowsK)
                for r in range(self.shape.nbCols):
                    for c in range(self.shape.nbRows):
                        if (r+c) % self.shape.nbCols > self.shape.nbColsK:
                            self.block.setSegment(r,c)
                self.block.setSegment(0, 0)
            elif self.shape.failureModel == "MREP": # Minimum size Recoverable Erasure Pattern
                for r in range(self.shape.nbCols):
                    for c in range(self.shape.nbRows):
                        if r < self.shape.nbColsK or c < self.shape.nbRowsK:
                            self.block.setSegment(r,c)
            elif self.shape.failureModel == "MREP-1": # make MREP non-recoverable
                for r in range(self.shape.nbCols):
                    for c in range(self.shape.nbRows):
                        if r < self.shape.nbColsK or c < self.shape.nbRowsK:
                            self.block.setSegment(r,c)
                self.block.setSegment(0, 0, 0)

            nbFailures = self.block.data.count(0)
            measuredFailureRate = nbFailures * 100 / (self.shape.nbCols * self.shape.nbRows)
            self.logger.debug("Number of failures: %d (%0.02f %%)", nbFailures, measuredFailureRate, extra=self.format)

            if self.queueAllOnInit:
                for r in range(self.shape.nbRows):
                    for c in range(self.shape.nbCols):
                        if self.block.getSegment(r,c):
                            if r in self.rowNeighbors:
                                for n in self.rowNeighbors[r].values():
                                    n.sendQueue.append(c)
                            if c in self.columnNeighbors:
                                for n in self.columnNeighbors[c].values():
                                    n.sendQueue.append(r)

    def getColumn(self, index):
        """It returns a given column."""
        return self.block.getColumn(index)

    def getRow(self, index):
        """It returns a given row."""
        return self.block.getRow(index)

    def receiveSegment(self, rID, cID, src):
        """Receive a segment, register it, and queue for forwarding as needed."""
        # register receive so that we are not sending back
        if rID in self.rowIDs:
            if src in self.rowNeighbors[rID]:
                self.rowNeighbors[rID][src].receiving[cID] = 1
        if cID in self.columnIDs:
            if src in self.columnNeighbors[cID]:
                self.columnNeighbors[cID][src].receiving[rID] = 1
        if not self.receivedBlock.getSegment(rID, cID):
            self.logger.trace("Recv new: %d->%d: %d,%d", src, self.ID, rID, cID, extra=self.format)
            self.receivedBlock.setSegment(rID, cID)
            self.sampleRecvCount += 1
            if self.forwardOnReceive:
                if self.perNodeQueue or self.perNeighborQueue:
                  self.receivedQueue.append((rID, cID))
                  self.msgRecvCount += 1
        else:
            self.logger.trace("Recv DUP: %d->%d: %d,%d", src, self.ID, rID, cID, extra=self.format)
            self.statsRxDupInSlot += 1
        self.statsRxInSlot += 1

    def addToSendQueue(self, rID, cID):
        """Queue a segment for forwarding."""
        if self.perNodeQueue and not self.amImalicious:
            self.sendQueue.append((rID, cID))
            self.amIaddedToQueue = 1
            self.msgSentCount += 1

        if self.perNeighborQueue and not self.amImalicious:
            if rID in self.rowIDs:
                for neigh in self.rowNeighbors[rID].values():
                    neigh.sendQueue.append(cID)
                    self.amIaddedToQueue = 1
                    self.msgSentCount += 1

            if cID in self.columnIDs:
                for neigh in self.columnNeighbors[cID].values():
                    neigh.sendQueue.append(rID)
                    self.amIaddedToQueue = 1
                    self.msgSentCount += 1

    def receiveRowsColumns(self):
        """Finalize time step by merging newly received segments in state."""
        if self.amIproposer == 1:
            self.logger.error("I am a block proposer", extra=self.format)
        else:
            self.logger.trace("Receiving the data...", extra=self.format)
            #self.logger.debug("%s -> %s", self.block.data, self.receivedBlock.data, extra=self.format)

            self.block.merge(self.receivedBlock)

            for neighs in chain (self.rowNeighbors.values(), self.columnNeighbors.values()):
                for neigh in neighs.values():
                    neigh.received |= neigh.receiving
                    neigh.receiving.setall(0)

            for rID, cID in self.receivedQueue:
                self.msgRecvCount += 1
            # add newly received segments to the send queue
            if self.perNodeQueue or self.perNeighborQueue:
                while self.receivedQueue:
                    (rID, cID) = self.receivedQueue.popleft()
                    if not self.amImalicious:
                        self.addToSendQueue(rID, cID)

    def updateStats(self):
        """It updates the stats related to sent and received data."""
        self.logger.debug("Stats: tx %d, rx %d", self.statsTxInSlot, self.statsRxInSlot, extra=self.format)
        self.statsRxPerSlot.append(self.statsRxInSlot)
        self.statsRxDupPerSlot.append(self.statsRxDupInSlot)
        self.statsTxPerSlot.append(self.statsTxInSlot)
        self.statsRxInSlot = 0
        self.statsRxDupInSlot = 0
        self.statsTxInSlot = 0

    def checkSegmentToNeigh(self, rID, cID, neigh):
        """Check if a segment should be sent to a neighbor."""
        if not self.amImalicious:
            if (neigh.sent | neigh.received).count(1) >= (self.sendLineUntilC if neigh.dim else self.sendLineUntilR):
                return False # sent enough, other side can restore
            i = rID if neigh.dim else cID
            if not neigh.sent[i] and not neigh.received[i] :
                return True
        else:
            return False # received or already sent or malicious

    def sendSegmentToNeigh(self, rID, cID, neigh):
        """Send segment to a neighbor (without checks)."""
        if not self.amImalicious:
            self.logger.trace("sending %d/%d to %d", rID, cID, neigh.node.ID, extra=self.format)
            i = rID if neigh.dim else cID
            neigh.sent[i] = 1
            neigh.node.receiveSegment(rID, cID, self.ID)
            self.statsTxInSlot += 1

    def checkSendSegmentToNeigh(self, rID, cID, neigh):
        """Check and send a segment to a neighbor if needed."""
        if self.checkSegmentToNeigh(rID, cID, neigh) and not self.amImalicious:
            self.sendSegmentToNeigh(rID, cID, neigh)
            return True
        else:
            return False

    def processSendQueue(self):
        """Send out segments from queue until bandwidth limit reached.

        SendQueue is a centralized queue from which segments are sent out
        in FIFO order to all interested neighbors.
        """
        while self.sendQueue:
            (rID, cID) = self.sendQueue[0]

            if rID in self.rowIDs and not self.amImalicious:
                for _, neigh in shuffledDict(self.rowNeighbors[rID], self.shuffleNeighbors):
                    if not self.amImalicious: 
                        self.checkSendSegmentToNeigh(rID, cID, neigh)

                if self.statsTxInSlot >= self.bwUplink:
                    return

            if cID in self.columnIDs and not self.amImalicious:
                for _, neigh in shuffledDict(self.columnNeighbors[cID], self.shuffleNeighbors):
                    if not self.amImalicious: 
                        self.checkSendSegmentToNeigh(rID, cID, neigh)

                if self.statsTxInSlot >= self.bwUplink:
                    return

            self.sendQueue.popleft()

    def processPerNeighborSendQueue(self):
        """Send out segments from per-neighbor queues until bandwidth limit reached.

        Segments are dispatched from per-neighbor transmission queues in a shuffled
        round-robin order, emulating a type of fair queuing. Since neighborhood is
        handled at the topic (column or row) level, fair queuing is also at the level
        of flows per topic and per peer. A per-peer model might be closer to the
        reality of libp2p implementations where topics between two nodes are
        multiplexed over the same transport.
        """
        progress = True
        while (progress):
            progress = False

            queues = []
            # collect and shuffle
            for rID, neighs in self.rowNeighbors.items():
                for neigh in neighs.values():
                    if (neigh.sendQueue) and not self.amImalicious:
                        queues.append((0, rID, neigh))

            for cID, neighs in self.columnNeighbors.items():
                for neigh in neighs.values():
                    if (neigh.sendQueue) and not self.amImalicious:
                        queues.append((1, cID, neigh))

            for dim, lineID, neigh in shuffled(queues, self.shuffleQueues):
                if not self.amImalicious:
                    if dim == 0:
                        self.checkSendSegmentToNeigh(lineID, neigh.sendQueue.popleft(), neigh)
                    else:
                        self.checkSendSegmentToNeigh(neigh.sendQueue.popleft(), lineID, neigh)
                progress = True
                if self.statsTxInSlot >= self.bwUplink:
                    return

    def runSegmentShuffleScheduler(self):
        """ Schedule chunks for sending.

        This scheduler check which owned segments needs sending (at least
        one neighbor needing it). Then it sends each segment that's worth sending
        once, in shuffled order. This is repeated until bw limit.
        """

        def collectSegmentsToSend():
                # yields list of segments to send as (dim, lineID, id)
                segmentsToSend = []
                if not self.amImalicious:
                    for rID, neighs in self.rowNeighbors.items():
                        line = self.getRow(rID)
                        needed = zeros(self.shape.nbCols)
                        for neigh in neighs.values():
                            sentOrReceived = neigh.received | neigh.sent
                            if sentOrReceived.count(1) < self.sendLineUntilR:
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
                            if sentOrReceived.count(1) < self.sendLineUntilC:
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
                            for _, neigh in shuffledDict(self.rowNeighbors[lineID], self.shuffleNeighbors):
                                if self.checkSegmentToNeigh(lineID, id, neigh) and not self.amImalicious:
                                    yield((lineID, id, neigh))
                                    break
                        else:
                            for _, neigh in shuffledDict(self.columnNeighbors[lineID], self.shuffleNeighbors):
                                if self.checkSegmentToNeigh(id, lineID, neigh) and not self.amImalicious:
                                    yield((id, lineID, neigh))
                                    break

                # collect segments for next round
                segmentsToSend = collectSegmentsToSend()

                # finish if empty  or set up shuffled generator based on collected segments
                if not segmentsToSend:
                    break
                else:
                    self.segmentShuffleGen = shuffled(segmentsToSend, self.shuffleLines)

        for rid, cid, neigh in nextSegment():
            # segments are checked just before yield, so we can send directly
            if not self.amImalicious:
                self.sendSegmentToNeigh(rid, cid, neigh)

            if self.statsTxInSlot >= self.bwUplink:
                if not self.segmentShuffleSchedulerPersist:
                    # remove scheduler state before leaving
                    self.segmentShuffleGen = None
                return

    def runDumbRandomScheduler(self, tries = 100):
        """Random scheduler picking segments at random.

        This scheduler implements a simple random scheduling order picking
        segments at random and peers potentially interested in that segment
        also at random.
        It serves more as a performance baseline than as a realistic model.
        """

        def nextSegment():
            t = tries
            while t:
                if self.rowIDs:
                    rID = random.choice(self.rowIDs)
                    cID = random.randrange(0, self.shape.nbCols)
                    if self.block.getSegment(rID, cID) :
                        neigh = random.choice(list(self.rowNeighbors[rID].values()))
                        if self.checkSegmentToNeigh(rID, cID, neigh) and not self.amImalicious:
                            yield(rID, cID, neigh)
                            t = tries
                if self.columnIDs:
                    cID = random.choice(self.columnIDs)
                    rID = random.randrange(0, self.shape.nbRows)
                    if self.block.getSegment(rID, cID) :
                        neigh = random.choice(list(self.columnNeighbors[cID].values()))
                        if self.checkSegmentToNeigh(rID, cID, neigh) and not self.amImalicious:
                            yield(rID, cID, neigh)
                            t = tries
                t -= 1

        for rid, cid, neigh in nextSegment():
            # segments are checked just before yield, so we can send directly
            if not self.amImalicious:
                self.sendSegmentToNeigh(rid, cid, neigh)

            if self.statsTxInSlot >= self.bwUplink:
                return

    def sendGossip(self, neigh):
        """Simulate sending row and column IDs to a peer."""
        have_info = {'source': self.ID, 'rowIDs': self.rowIDs, 'columnIDs': self.columnIDs}
        neigh.node.received_gossip[self.ID].append(have_info)
        neigh.node.msgRecvCount += 1
        self.logger.debug(f"Gossip sent to {neigh.node.ID}: {neigh.node.received_gossip}", extra=self.format)

    def process_received_gossip(self, simulator):
        """
        Processes received gossip messages to request and receive data segments.
        For each segment not already received, it simulates requesting the segment,
        logs the request and receipt, and updates the segment status and relevant counters.
        """
        for sender, have_infos in self.received_gossip.items():
            for have_info in have_infos:
                for rowID in have_info['rowIDs']:
                    for columnID in have_info['columnIDs']:
                        if not self.receivedBlock.getSegment(rowID, columnID):
                            # request for the segment
                            self.logger.debug(f"Requesting segment ({rowID}, {columnID}) from {have_info['source']}", extra=self.format)
                            self.msgSentCount += 1
                            # source sends the segment
                            self.logger.debug(f"Sending segment ({rowID}, {columnID}) to {self.ID} from {have_info['source']}", extra=self.format)
                            simulator.validators[have_info['source']].sampleSentCount += 1
                            simulator.validators[have_info['source']].statsTxInSlot += 1
                            # receive the segment
                            self.receivedBlock.setSegment(rowID, columnID)
                            self.sampleRecvCount += 1
                            self.logger.debug(f"Received segment ({rowID}, {columnID}) via gossip from {have_info['source']}", extra=self.format)
        self.received_gossip.clear()

    def gossip(self, simulator):
        """
        Periodically sends gossip messages to a random subset of neighbors to share information 
        about data segments (row and column IDs). The process involves:
        1. Selecting a random subset of row and column neighbors.
        2. Sending the node's current state (row and column IDs) to these neighbors.
        3. Neighbors process the received gossip and update their state accordingly.
        
        This ensures data dissemination across the network with minimal delay, 
        occurring at intervals defined by the HEARTBEAT timer.
        """
        if self.rowIDs:
            rID = random.choice(list(self.rowIDs))
            rowNeighs = list(self.rowNeighbors[rID].values())
            num_row_peers = random.randint(1, len(rowNeighs))
            selected_row_neighs = random.sample(rowNeighs, num_row_peers)
            for rowNeigh in selected_row_neighs:
                self.sendGossip(rowNeigh)
                self.msgSentCount += 1
                rowNeigh.node.process_received_gossip(simulator)
                if self.statsTxInSlot >= self.bwUplink:
                    return

        if self.columnIDs:
            cID = random.choice(list(self.columnIDs))
            columnNeighs = list(self.columnNeighbors[cID].values())
            num_column_peers = random.randint(1, len(columnNeighs))
            selected_column_neighs = random.sample(columnNeighs, num_column_peers)
            for columnNeigh in selected_column_neighs:
                self.sendGossip(columnNeigh)
                self.msgSentCount += 1
                columnNeigh.node.process_received_gossip(simulator)
                if self.statsTxInSlot >= self.bwUplink:
                    return

    def send(self):
        """ Send as much as we can in the timestep, limited by bwUplink."""

        # process node level send queue
        if not self.amImalicious:
            self.processSendQueue()
        if self.statsTxInSlot >= self.bwUplink:
            return

        # process neighbor level send queues in shuffled breadth-first order
        if not self.amImalicious:
            self.processPerNeighborSendQueue()
        if self.statsTxInSlot >= self.bwUplink:
            return

        # process possible segments to send in shuffled breadth-first order
        if self.segmentShuffleScheduler and not self.amImalicious:
            self.runSegmentShuffleScheduler()
        if self.statsTxInSlot >= self.bwUplink:
            return

        if self.dumbRandomScheduler and not self.amImalicious:
            self.runDumbRandomScheduler()
        if self.statsTxInSlot >= self.bwUplink:
            return

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
                self.restoreRow(id)

    def restoreRow(self, id):
        """Restore a given row if repairable.

        The functions checks if the row can be repaired based on the number of segments.
        If at least K segments are available, it repairs all remaining segments.
        It also forwards repaired segments as follows:
         - if forwardWhenLineReceived=False, it is assumed that received segments were
         already forwarded, so it forwards only the new (repaired) segments.
         - if forwardWhenLineReceived=True, none of the received segments were forwarded
         yet. When the line is received (i.e. when repair is possible), it forwards all
         segments of the line.
         Forwarding here also means cross-posting to the respective column topic, if
         subscribed.
        """
        rep, repairedSamples = self.block.repairRow(id)
        self.repairedSampleCount += repairedSamples
        if (rep.any()):
            # If operation is based on send queues, segments should
            # be queued after successful repair.
            self.restoreRowCount += 1
            for i in range(len(rep)):
                if rep[i] or self.forwardWhenLineReceived:
                    self.logger.trace("Rep: %d,%d", id, i, extra=self.format)
                    if not self.amImalicious:
                        self.addToSendQueue(id, i)
            # self.statsRepairInSlot += rep.count(1)

    def restoreColumns(self):
        """It restores the columns assigned to the validator, that can be repaired."""
        if self.repairOnTheFly:
            for id in self.columnIDs:
                self.restoreColumn(id)

    def restoreColumn(self, id):
        """Restore a given column if repairable."""
        rep, repairedSamples = self.block.repairColumn(id)
        self.repairedSampleCount += repairedSamples
        if (rep.any()):
            # If operation is based on send queues, segments should
            # be queued after successful repair.
            self.restoreColumnCount += 1
            for i in range(len(rep)):
                if rep[i] or self.forwardWhenLineReceived:
                    self.logger.trace("Rep: %d,%d", i, id, extra=self.format)
                    if not self.amImalicious:
                        self.addToSendQueue(i, id)
            # self.statsRepairInSlot += rep.count(1)

    def checkStatus(self):
        """It checks how many expected/arrived samples are for each assigned row/column."""

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
        self.logger.debug("status: %d / %d", arrived, expected, extra=self.format)

        validated = 0
        for v in self.validators:
            a, e = checkStatus(v.columnIDs, v.rowIDs)
            if a == e:
                validated+=1

        return arrived, expected, validated