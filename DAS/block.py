#!/bin/python3

import random
from bitarray import bitarray
from bitarray.util import zeros

class Block:

    blockSize = 0
    data = bitarray()

    def __init__(self, blockSize):
        self.blockSize = blockSize
        self.data = zeros(self.blockSize*self.blockSize)

    def fill(self):
        self.data.setall(1)

    def merge(self, merged):
        self.data |= merged.data

    def getColumn(self, columnID):
        return self.data[columnID::self.blockSize]

    def mergeColumn(self, columnID, column):
        self.data[columnID::self.blockSize] |= column

    def repairColumn(self, id):
        success = self.data[id::self.blockSize].count(1)
        if success >= self.blockSize/2:
            self.data[id::self.blockSize] = 1

    def getRow(self, rowID):
        return self.data[rowID*self.blockSize:(rowID+1)*self.blockSize]

    def mergeRow(self, rowID, row):
        self.data[rowID*self.blockSize:(rowID+1)*self.blockSize] |= row

    def repairRow(self, id):
        success = self.data[id*self.blockSize:(id+1)*self.blockSize].count(1)
        if success >= self.blockSize/2:
            self.data[id*self.blockSize:(id+1)*self.blockSize] = 1

    def print(self):
        dash = "-" * (self.blockSize+2)
        print(dash)
        for i in range(self.blockSize):
            line = "|"
            for j in range(self.blockSize):
                line += "%i" % self.data[(i*self.blockSize)+j]
            print(line+"|")
        print(dash)

