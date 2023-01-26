#!/bin/python3

import random
import collections
import logging
from DAS.block import *
from bitarray import bitarray
from bitarray.util import zeros

def shuffled(lis):
    # based on https://stackoverflow.com/a/60342323
    for index in random.sample(range(len(lis)), len(lis)):
        yield lis[index]

class NextToSend:
    def __init__(self, neigh, toSend, id, dim):
        self.neigh = neigh
        self.toSend = toSend
        self.id = id
        self.dim = dim

class Neighbor:
    """This class implements a node neighbor to monitor sent and received data."""

    def __repr__(self):
        """It returns the amount of sent and received data."""
        return "%d:%d/%d" % (self.node.ID, self.sent.count(1), self.received.count(1))

    def __init__(self, v, blockSize):
        """It initializes the neighbor with the node and sets counters to zero."""
        self.node = v
        self.receiving = zeros(blockSize)
        self.received = zeros(blockSize)
        self.sent = zeros(blockSize)


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
        self.bwUplink = 1100 if not self.amIproposer else 22000 # approx. 100Mbps and 2Gbps

        self.sched = self.nextToSend()

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

    def receiveColumn(self, id, column, src):
        """It receives the given column if it has been assigned to it."""
        if id in self.columnIDs:
            # register receive so that we are not sending back
            self.columnNeighbors[id][src].receiving |= column
            self.receivedBlock.mergeColumn(id, column)
            self.statsRxInSlot += column.count(1)
        else:
            pass

    def receiveRow(self, id, row, src):
        """It receives the given row if it has been assigned to it."""
        if id in self.rowIDs:
            # register receive so that we are not sending back
            self.rowNeighbors[id][src].receiving |= row
            self.receivedBlock.mergeRow(id, row)
            self.statsRxInSlot += row.count(1)
        else:
            pass


    def receiveRowsColumns(self):
        """It receives rows and columns."""
        if self.amIproposer == 1:
            self.logger.error("I am a block proposer", extra=self.format)
        else:
            self.logger.debug("Receiving the data...", extra=self.format)
            #self.logger.debug("%s -> %s", self.block.data, self.receivedBlock.data, extra=self.format)

            self.block.merge(self.receivedBlock)

            for neighs in self.rowNeighbors.values():
                for neigh in neighs.values():
                    neigh.received |= neigh.receiving
                    neigh.receiving.setall(0)

            for neighs in self.columnNeighbors.values():
                for neigh in neighs.values():
                    neigh.received |= neigh.receiving
                    neigh.receiving.setall(0)

    def updateStats(self):
        """It updates the stats related to sent and received data."""
        self.logger.debug("Stats: tx %d, rx %d", self.statsTxInSlot, self.statsRxInSlot, extra=self.format)
        self.statsRxPerSlot.append(self.statsRxInSlot)
        self.statsTxPerSlot.append(self.statsTxInSlot)
        self.statsRxInSlot = 0
        self.statsTxInSlot = 0


    def nextColumnToSend(self, columnID):
        line = self.getColumn(columnID)
        if line.any():
            self.logger.debug("col %d -> %s", columnID, self.columnNeighbors[columnID] , extra=self.format)
            for n in shuffled(list(self.columnNeighbors[columnID].values())):

                # if there is anything new to send, send it
                toSend = line & ~n.sent & ~n.received
                if (toSend).any():
                    yield NextToSend(n, toSend, columnID, 1)

    def nextRowToSend(self, rowID):
        line = self.getRow(rowID)
        if line.any():
            self.logger.debug("row %d -> %s", rowID, self.rowNeighbors[rowID], extra=self.format)
            for n in shuffled(list(self.rowNeighbors[rowID].values())):

                # if there is anything new to send, send it
                toSend = line & ~n.sent & ~n.received
                if (toSend).any():
                    yield NextToSend(n, toSend, rowID, 0)

    def nextToSend(self):
        """ Send scheduler as a generator function
        
        Yields next segment(s) to send when asked for it.
        Generates an infinite flow, returning with exit only when
        there is nothing more to send.

        Generates a randomized order of columns and rows, sending to one neighbor
        at each before sending to another neighbor.
        Generates a new randomized ordering once all columns, rows, and neighbors
        are processed once.
        """

        while True:
            perLine = []
            for c in self.columnIDs:
                perLine.append(self.nextColumnToSend(c))

            for r in self.rowIDs:
                perLine.append(self.nextRowToSend(r))

            count = 0
            random.shuffle(perLine)
            while (perLine):
                for g in perLine.copy(): # we need a shallow copy to allow remove
                    n = next(g, None)
                    if not n:
                        perLine.remove(g)
                        continue
                    count += 1
                    yield n

            # return if there is nothing more to send
            if not count:
                return

    def send(self):
        """ Send as much as we can in the timeslot, limited by bwUplink
        """

        for n in self.sched:
            neigh = n.neigh
            toSend = n.toSend
            id = n.id
            dim = n.dim

            neigh.sent |= toSend;
            if dim == 0:
                neigh.node.receiveRow(id, toSend, self.ID)
            else:
                neigh.node.receiveColumn(id, toSend, self.ID)

            sent = toSend.count(1)
            self.statsTxInSlot += sent
            self.logger.debug("sending %s %d to %d (%d)",
                              "col" if dim else "row", id, neigh.node.ID, sent, extra=self.format)

            # until we exhaust capacity
            # TODO: use exact limit
            if self.statsTxInSlot >self.bwUplink:
                return

        # Scheduler exited, nothing to send. Create new one for next round.
        self.sched = self.nextToSend()

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
        for id in self.rowIDs:
            self.block.repairRow(id)

    def restoreColumns(self):
        """It restores the columns assigned to the validator, that can be repaired."""
        for id in self.columnIDs:
            self.block.repairColumn(id)

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
