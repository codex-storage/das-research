#!/bin/python3

import random
from DAS.block import *
from bitarray import bitarray
from bitarray.util import zeros

class Validator:

    ID = 0
    chi = 0
    format = {}
    blocksize = 0
    block = []
    rowIDs = []
    columnIDs = []
    rows = []
    columns = []
    proposer = 0
    failureRate = 0
    logger = []

    def __init__(self, ID, chi, blockSize, proposer, failureRate, deterministic, logger):
        FORMAT = "%(levelname)s : %(entity)s : %(message)s"
        self.ID = ID
        self.format = {"entity": "Val "+str(self.ID)}
        self.blockSize = blockSize
        self.proposer = proposer
        self.failureRate = failureRate
        self.logger = logger
        if chi < 1:
            self.logger.error("Chi has to be greater than 0", extra=self.format)
        elif chi > blockSize:
            self.logger.error("Chi has to be smaller than %d" % blockSize, extra=self.format)
        else:
            self.chi = chi
            self.rowIDs = []
            self.columnIDs = []
            if deterministic:
                random.seed(self.ID)
            self.rowIDs = random.sample(range(self.blockSize), self.chi)
            self.columnIDs = random.sample(range(self.blockSize), self.chi)

    def logIDs(self):
        if self.proposer == 1:
            self.logger.warning("I am a block proposer."% self.ID)
        else:
            self.logger.debug("Selected rows: "+str(self.rowIDs), extra=self.format)
            self.logger.debug("Selected columns: "+str(self.columnIDs), extra=self.format)

    def initBlock(self):
        self.logger.debug("I am a block proposer.", extra=self.format)
        self.block = Block(self.blockSize)
        self.block.fill()
        #self.block.print()

    def broadcastBlock(self, broadcasted):
        if self.proposer == 0:
            self.logger.error("I am NOT a block proposer", extra=self.format)
        else:
            self.logger.debug("Broadcasting my block...", extra=self.format)
            tempBlock = self.block
            order = [i for i in range(self.blockSize * self.blockSize)]
            random.shuffle(order)
            while(order):
                i = order.pop()
                if (random.randint(0,99) > self.failureRate):
                    broadcasted.data[i] = self.block.data[i]
            #broadcasted.print()

    def getColumn(self, columnID, broadcasted):
        column = broadcasted.getColumn(columnID)
        self.columns.append(column)

    def getRow(self, rowID, broadcasted):
        row = broadcasted.getRow(rowID)
        self.rows.append(row)

    def receiveRowsColumns(self, broadcasted):
        self.rows = []
        self.columns = []
        if self.proposer == 1:
            self.logger.error("I am a block proposer", extra=self.format)
        else:
            self.logger.debug("Receiving the data...", extra=self.format)
            for r in self.rowIDs:
                self.getRow(r, broadcasted)
            for c in self.columnIDs:
                self.getColumn(c, broadcasted)

    def sendColumn(self, c, columnID, broadcasted):
        broadcasted.data[columnID::self.blockSize] |= self.columns[c]

    def sendRow(self, r, rowID, broadcasted):
        broadcasted.data[rowID*self.blockSize:(rowID+1)*self.blockSize] |=  self.rows[r]

    def sendRows(self, broadcasted):
        if self.proposer == 1:
            self.logger.error("I am a block proposer", extra=self.format)
        else:
            self.logger.debug("Sending restored rows...", extra=self.format)
            for r in range(len(self.rowIDs)):
                self.sendRow(r, self.rowIDs[r], broadcasted)

    def sendColumns(self, broadcasted):
        if self.proposer == 1:
            self.logger.error("I am a block proposer", extra=self.format)
        else:
            self.logger.debug("Sending restored columns...", extra=self.format)
            for c in range(len(self.columnIDs)):
                self.sendColumn(c, self.columnIDs[c], broadcasted)

    def logRows(self):
        self.logger.debug("Rows: "+str(self.rows), extra=self.format)

    def logColumns(self):
        self.logger.debug("Columns: "+str(self.columns), extra=self.format)

    def restoreRows(self):
        for rid in range(len(self.rows)):
            row = self.rows[rid]
            success = row.count(1)

            if success >= len(row)/2:
                self.rows[rid].setall(1)
                self.logger.debug("%d samples restored in row %d" % (len(row)-success, self.rowIDs[rid]), extra=self.format )
            else:
                self.logger.debug("Row %d cannot be restored" %  (self.rowIDs[rid]), extra=self.format)

    def restoreColumns(self):
        for cid in range(len(self.columns)):
            column = self.columns[cid]
            success = column.count(1)
            if success >= len(column)/2:
                self.columns[cid].setall(1)
                self.logger.debug("%d samples restored in column %d" % (len(column)-success, self.columnIDs[cid]), extra=self.format)
            else:
                self.logger.debug("Column %d cannot be restored" % (self.columnIDs[cid]), extra=self.format)


