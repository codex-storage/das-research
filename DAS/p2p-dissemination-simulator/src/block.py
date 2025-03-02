#!/bin/python3

import random
from bitarray import bitarray
from bitarray.util import zeros

class Block:
    
    def __init__(self, blockSizeR, blockSizeRK=0, blockSizeC=0, blockSizeCK=0):
        self.blockSizeR = blockSizeR
        self.blockSizeRK = blockSizeRK if blockSizeRK else blockSizeR/2
        self.blockSizeC = blockSizeC if blockSizeC else blockSizeR
        self.blockSizeCK = blockSizeCK if blockSizeCK else blockSizeRK
        self.data = zeros(self.blockSizeR*self.blockSizeC)

    def fill(self):
        self.data.setall(1)

    def merge(self, merged):
        self.data |= merged.data

    def getSegment(self, rowID, columnID):
        return self.data[rowID*self.blockSizeR + columnID]

    def setSegment(self, rowID, columnID, value = 1):
        self.data[rowID*self.blockSizeR + columnID] = value

    def getColumn(self, columnID):
        return self.data[columnID::self.blockSizeR]

    def mergeColumn(self, columnID, column):
        self.data[columnID::self.blockSizeR] |= column

    def repairColumn(self, id):
        line = self.data[id::self.blockSizeR]
        success = line.count(1)
        if success >= self.blockSizeCK:
            ret = ~line
            self.data[id::self.blockSizeR] = 1
        else:
            ret = zeros(self.blockSizeC)
        return ret

    def getRow(self, rowID):
        return self.data[rowID*self.blockSizeR:(rowID+1)*self.blockSizeR]

    def mergeRow(self, rowID, row):
        self.data[rowID*self.blockSizeR:(rowID+1)*self.blockSizeR] |= row

    def repairRow(self, id):
        line = self.data[id*self.blockSizeR:(id+1)*self.blockSizeR]
        success = line.count(1)
        if success >= self.blockSizeRK:
            ret = ~line
            self.data[id*self.blockSizeR:(id+1)*self.blockSizeR] = 1
        else:
            ret = zeros(self.blockSizeR)
        return ret
    
    def print(self):
        dash = "-" * (self.blockSizeR+2)
        print(dash)
        for i in range(self.blockSizeC):
            line = "|"
            for j in range(self.blockSizeR):
                line += "%i" % self.data[(i*self.blockSizeR)+j]
            print(line+"|")
        print(dash)

