#!/bin/python3

import random
import collections
import logging
from DAS.block import *
from bitarray import bitarray
from bitarray.util import zeros

class Validator:

    ID = 0
    amIproposer = 0
    config = []
    format = {}
    logger = []

    def __init__(self, ID, amIproposer, logger, config):
        self.config = config
        FORMAT = "%(levelname)s : %(entity)s : %(message)s"
        self.ID = ID
        self.format = {"entity": "Val "+str(self.ID)}
        self.block = Block(self.config.blockSize)
        self.receivedBlock = Block(self.config.blockSize)
        self.amIproposer = amIproposer
        self.logger = logger
        if self.config.chi < 1:
            self.logger.error("Chi has to be greater than 0", extra=self.format)
        elif self.config.chi > self.config.blockSize:
            self.logger.error("Chi has to be smaller than %d" % blockSize, extra=self.format)
        else:
            if amIproposer:
                self.rowIDs = range(config.blockSize)
                self.columnIDs = range(config.blockSize)
            else:
                self.rowIDs = []
                self.columnIDs = []
                if config.deterministic:
                    random.seed(self.ID)
                self.rowIDs = random.sample(range(self.config.blockSize), self.config.chi)
                self.columnIDs = random.sample(range(self.config.blockSize), self.config.chi)
        self.rowNeighbors = collections.defaultdict(list)
        self.columnNeighbors = collections.defaultdict(list)

    def logIDs(self):
        if self.amIproposer == 1:
            self.logger.warning("I am a block proposer."% self.ID)
        else:
            self.logger.debug("Selected rows: "+str(self.rowIDs), extra=self.format)
            self.logger.debug("Selected columns: "+str(self.columnIDs), extra=self.format)

    def initBlock(self):
        self.logger.debug("I am a block proposer.", extra=self.format)
        self.block = Block(self.config.blockSize)
        self.block.fill()
        #self.block.print()

    def broadcastBlock(self):
        if self.amIproposer == 0:
            self.logger.error("I am NOT a block proposer", extra=self.format)
        else:
            self.logger.debug("Broadcasting my block...", extra=self.format)
            order = [i for i in range(self.config.blockSize * self.config.blockSize)]
            random.shuffle(order)
            while(order):
                i = order.pop()
                if (random.randint(0,99) >= self.config.failureRate):
                    self.block.data[i] = 1
                else:
                    self.block.data[i] = 0
            nbFailures = self.block.data.count(0)
            measuredFailureRate = nbFailures * 100 / (self.config.blockSize * self.config.blockSize)
            self.logger.debug("Number of failures: %d (%0.02f %%)", nbFailures, measuredFailureRate, extra=self.format)
            #broadcasted.print()
            for id in range(self.config.blockSize):
                self.sendColumn(id)
            for id in range(self.config.blockSize):
                self.sendRow(id)

    def getColumn(self, index):
        return self.block.getColumn(index)

    def getRow(self, index):
        return self.block.getRow(index)

    def receiveColumn(self, id, column):
        if id in self.columnIDs:
            self.receivedBlock.mergeColumn(id, column)
        else:
            pass

    def receiveRow(self, id, row):
        if id in self.rowIDs:
            self.receivedBlock.mergeRow(id, row)
        else:
            pass


    def receiveRowsColumns(self):
        if self.amIproposer == 1:
            self.logger.error("I am a block proposer", extra=self.format)
        else:
            self.logger.debug("Receiving the data...", extra=self.format)
            #self.logger.debug("%s -> %s", self.block.data, self.receivedBlock.data, extra=self.format)

            self.block.merge(self.receivedBlock)

    def sendColumn(self, columnID):
        line = self.getColumn(columnID)
        if line.any():
            self.logger.debug("col %d -> %s", columnID, self.columnNeighbors[columnID] , extra=self.format)
            for n in self.columnNeighbors[columnID]:
                n.receiveColumn(columnID, line)

    def sendRow(self, rowID):
        line = self.getRow(rowID)
        if line.any():
            self.logger.debug("row %d -> %s", rowID, self.rowNeighbors[rowID], extra=self.format)
            for n in self.rowNeighbors[rowID]:
                n.receiveRow(rowID, line)

    def sendRows(self):
        if self.amIproposer == 1:
            self.logger.error("I am a block proposer", extra=self.format)
        else:
            self.logger.debug("Sending restored rows...", extra=self.format)
            for r in self.rowIDs:
                self.sendRow(r)

    def sendColumns(self):
        if self.amIproposer == 1:
            self.logger.error("I am a block proposer", extra=self.format)
        else:
            self.logger.debug("Sending restored columns...", extra=self.format)
            for c in self.columnIDs:
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
