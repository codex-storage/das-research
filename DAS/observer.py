#!/bin/python3

from DAS.block import *

class Observer:

    block = []
    blockSize = 0
    rows = []
    columns = []
    goldenData = []
    broadcasted = []
    logger = []

    def __init__(self, blockSize, logger):
        self.format = {"entity": "Observer"}
        self.blockSize = blockSize
        self.logger = logger

    def reset(self):
        self.block = [0] * self.blockSize * self.blockSize
        self.goldenData = [0] * self.blockSize * self.blockSize
        self.rows = [0] * self.blockSize
        self.columns = [0] * self.blockSize
        self.broadcasted = Block(self.blockSize)

    def checkRowsColumns(self, validators):
        for val in validators:
            if val.proposer == 0:
                for r in val.rowIDs:
                    self.rows[r] += 1
                for c in val.columnIDs:
                    self.columns[c] += 1

        for i in range(self.blockSize):
            self.logger.debug("Row/Column %d have %d and %d validators assigned." % (i, self.rows[i], self.columns[i]), extra=self.format)
            if self.rows[i] == 0 or self.columns[i] == 0:
                self.logger.warning("There is a row/column that has not been assigned", extra=self.format)

    def setGoldenData(self, block):
        for i in range(self.blockSize*self.blockSize):
            self.goldenData[i] = block.data[i]

    def checkBroadcasted(self):
        zeros = 0
        for i in range(self.blockSize * self.blockSize):
            if self.broadcasted.data[i] == 0:
                zeros += 1
        if zeros > 0:
            self.logger.debug("There are %d missing samples in the network" % zeros, extra=self.format)
        return zeros

