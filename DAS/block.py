#!/bin/python3

import random
from bitarray import bitarray
from bitarray.util import zeros

class Block:
    """This class represents a block in the Ethereum blockchain."""

    def __init__(self, blockSize):
        """Initialize the block with a data array of blocksize^2 zeros."""
        self.blockSize = blockSize
        self.data = zeros(self.blockSize*self.blockSize)

    def fill(self):
        """It fills the block data with ones."""
        self.data.setall(1)

    def merge(self, merged):
        """It merges (OR) the existing block with the received one."""
        self.data |= merged.data

    def getSegment(self, rowID, columnID):
        """Check whether a segment is included"""
        return self.data[rowID*self.blockSize + columnID]

    def setSegment(self, rowID, columnID, value = 1):
        """Set value for a segment (default 1)"""
        self.data[rowID*self.blockSize + columnID] = value

    def getColumn(self, columnID):
        """It returns the block column corresponding to columnID."""
        return self.data[columnID::self.blockSize]

    def mergeColumn(self, columnID, column):
        """It merges (OR) the existing column with the received one."""
        self.data[columnID::self.blockSize] |= column

    def repairColumn(self, id):
        """It repairs the entire column if it has at least blockSize/2 ones.
            Returns: list of repaired segments
        """
        line = self.data[id::self.blockSize]
        success = line.count(1)
        if success >= self.blockSize/2:
            ret = ~line
            self.data[id::self.blockSize] = 1
        else:
            ret = zeros(self.blockSize)
        return ret

    def getRow(self, rowID):
        """It returns the block row corresponding to rowID."""
        return self.data[rowID*self.blockSize:(rowID+1)*self.blockSize]

    def mergeRow(self, rowID, row):
        """It merges (OR) the existing row with the received one."""
        self.data[rowID*self.blockSize:(rowID+1)*self.blockSize] |= row

    def repairRow(self, id):
        """It repairs the entire row if it has at least blockSize/2 ones.
            Returns: list of repaired segments.
        """
        line = self.data[id*self.blockSize:(id+1)*self.blockSize]
        success = line.count(1)
        if success >= self.blockSize/2:
            ret = ~line
            self.data[id*self.blockSize:(id+1)*self.blockSize] = 1
        else:
            ret = zeros(self.blockSize)
        return ret

    def print(self):
        """It prints the block in the terminal (outside of the logger rules))."""
        dash = "-" * (self.blockSize+2)
        print(dash)
        for i in range(self.blockSize):
            line = "|"
            for j in range(self.blockSize):
                line += "%i" % self.data[(i*self.blockSize)+j]
            print(line+"|")
        print(dash)


    def getUniqueIDforSegment(self, rowID, columnID):
        """It returns a unique ID for a segment indicating its coordinates in the block"""
        return f"r{rowID}-c{columnID}"

