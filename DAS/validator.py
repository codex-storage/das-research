#!/bin/python3

import random
import collections
import logging
from DAS.block import *
from bitarray import bitarray
from bitarray.util import zeros

class Neighbor:

    def __repr__(self):
        return "%d:%d/%d" % (self.node.ID, self.sent.count(1), self.received.count(1))

    def __init__(self, v, blockSize):
        self.node = v
        self.received = zeros(blockSize)
        self.sent = zeros(blockSize)

class Validator:

    ID = 0
    amIproposer = 0
    shape = []
    format = {}
    logger = []

    def __repr__(self):
        return str(self.ID)

    def __init__(self, ID, amIproposer, logger, shape, rows, columns):
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
                self.columnIDs = rows[(self.ID*self.shape.chi):(self.ID*self.shape.chi + self.shape.chi)]
                #if shape.deterministic:
                #    random.seed(self.ID)
                #self.rowIDs = random.sample(range(self.shape.blockSize), self.shape.chi)
                #self.columnIDs = random.sample(range(self.shape.blockSize), self.shape.chi)
        self.changedRow = {id:False for id in self.rowIDs}
        self.changedColumn = {id:False for id in self.columnIDs}
        self.rowNeighbors = collections.defaultdict(dict)
        self.columnNeighbors = collections.defaultdict(dict)

        #statistics
        self.statsTxInSlot = 0
        self.statsTxPerSlot = []
        self.statsRxInSlot = 0
        self.statsRxPerSlot = []

    def logIDs(self):
        if self.amIproposer == 1:
            self.logger.warning("I am a block proposer."% self.ID)
        else:
            self.logger.debug("Selected rows: "+str(self.rowIDs), extra=self.format)
            self.logger.debug("Selected columns: "+str(self.columnIDs), extra=self.format)

    def initBlock(self):
        self.logger.debug("I am a block proposer.", extra=self.format)
        self.block = Block(self.shape.blockSize)
        self.block.fill()
        #self.block.print()

    def broadcastBlock(self):
        if self.amIproposer == 0:
            self.logger.error("I am NOT a block proposer", extra=self.format)
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
            for id in range(self.shape.blockSize):
                self.sendColumn(id)
            for id in range(self.shape.blockSize):
                self.sendRow(id)

    def getColumn(self, index):
        return self.block.getColumn(index)

    def getRow(self, index):
        return self.block.getRow(index)

    def receiveColumn(self, id, column, src):
        if id in self.columnIDs:
            # register receive so that we are not sending back
            self.columnNeighbors[id][src].received |= column
            self.receivedBlock.mergeColumn(id, column)
            self.statsRxInSlot += column.count(1)
        else:
            pass

    def receiveRow(self, id, row, src):
        if id in self.rowIDs:
            # register receive so that we are not sending back
            self.rowNeighbors[id][src].received |= row
            self.receivedBlock.mergeRow(id, row)
            self.statsRxInSlot += row.count(1)
        else:
            pass


    def receiveRowsColumns(self):
        if self.amIproposer == 1:
            self.logger.error("I am a block proposer", extra=self.format)
        else:
            self.logger.debug("Receiving the data...", extra=self.format)
            #self.logger.debug("%s -> %s", self.block.data, self.receivedBlock.data, extra=self.format)

            self.changedRow = { id:
                self.getRow(id) != self.receivedBlock.getRow(id)
                for id in self.rowIDs
            }

            self.changedColumn = { id:
                self.getColumn(id) != self.receivedBlock.getColumn(id)
                for id in self.columnIDs
            }

            self.block.merge(self.receivedBlock)

    def updateStats(self):
        self.logger.debug("Stats: tx %d, rx %d", self.statsTxInSlot, self.statsRxInSlot, extra=self.format)
        self.statsRxPerSlot.append(self.statsRxInSlot)
        self.statsTxPerSlot.append(self.statsTxInSlot)
        self.statsRxInSlot = 0
        self.statsTxInSlot = 0


    def sendColumn(self, columnID):
        line = self.getColumn(columnID)
        if line.any():
            self.logger.debug("col %d -> %s", columnID, self.columnNeighbors[columnID] , extra=self.format)
            for n in self.columnNeighbors[columnID].values():

                # if there is anything new to send, send it
                toSend = line & ~n.sent & ~n.received
                if (toSend).any():
                    n.sent |= toSend;
                    n.node.receiveColumn(columnID, toSend, self.ID)
                    self.statsTxInSlot += toSend.count(1)

    def sendRow(self, rowID):
        line = self.getRow(rowID)
        if line.any():
            self.logger.debug("row %d -> %s", rowID, self.rowNeighbors[rowID], extra=self.format)
            for n in self.rowNeighbors[rowID].values():

                # if there is anything new to send, send it
                toSend = line & ~n.sent & ~n.received
                if (toSend).any():
                    n.sent |= toSend;
                    n.node.receiveRow(rowID, toSend, self.ID)
                    self.statsTxInSlot += toSend.count(1)

    def sendRows(self):
        if self.amIproposer == 1:
            self.logger.error("I am a block proposer", extra=self.format)
        else:
            self.logger.debug("Sending restored rows...", extra=self.format)
            for r in self.rowIDs:
                if self.changedRow[r]:
                    self.sendRow(r)

    def sendColumns(self):
        if self.amIproposer == 1:
            self.logger.error("I am a block proposer", extra=self.format)
        else:
            self.logger.debug("Sending restored columns...", extra=self.format)
            for c in self.columnIDs:
                if self.changedColumn[c]:
                    self.sendColumn(c)

    def logRows(self):
        if self.logger.isEnabledFor(logging.DEBUG):
            for id in self.rowIDs:
                self.logger.debug("Row %d: %s", id, self.getRow(id), extra=self.format)

    def logColumns(self):
        if self.logger.isEnabledFor(logging.DEBUG):
            for id in self.columnIDs:
                self.logger.debug("Column %d: %s", id, self.getColumn(id), extra=self.format)

    def restoreRows(self):
        for id in self.rowIDs:
            self.block.repairRow(id)

    def restoreColumns(self):
        for id in self.columnIDs:
            self.block.repairColumn(id)

    def checkStatus(self):
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
