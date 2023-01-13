#!/bin/python3

from DAS.block import *

class Observer:

    block = []
    rows = []
    columns = []
    goldenData = []
    broadcasted = []
    config = []
    logger = []

    def __init__(self, logger, config):
        self.config = config
        self.format = {"entity": "Observer"}
        self.logger = logger

    def reset(self):
        self.block = [0] * self.config.blockSize * self.config.blockSize
        self.goldenData = [0] * self.config.blockSize * self.config.blockSize
        self.rows = [0] * self.config.blockSize
        self.columns = [0] * self.config.blockSize
        self.broadcasted = Block(self.config.blockSize)

    def checkRowsColumns(self, validators):
        for val in validators:
            if val.amIproposer == 0:
                for r in val.rowIDs:
                    self.rows[r] += 1
                for c in val.columnIDs:
                    self.columns[c] += 1

        for i in range(self.config.blockSize):
            self.logger.debug("Row/Column %d have %d and %d validators assigned." % (i, self.rows[i], self.columns[i]), extra=self.format)
            if self.rows[i] == 0 or self.columns[i] == 0:
                self.logger.warning("There is a row/column that has not been assigned", extra=self.format)

    def setGoldenData(self, block):
        for i in range(self.config.blockSize*self.config.blockSize):
            self.goldenData[i] = block.data[i]

    def checkBroadcasted(self):
        zeros = 0
        for i in range(self.blockSize * self.blockSize):
            if self.broadcasted.data[i] == 0:
                zeros += 1
        if zeros > 0:
            self.logger.debug("There are %d missing samples in the network" % zeros, extra=self.format)
        return zeros

    def checkStatus(self, validators):
        arrived = 0
        expected = 0
        for val in validators:
            if val.amIproposer == 0:
                (a, e) = val.checkStatus()
                arrived += a
                expected += e
        return (arrived, expected)
