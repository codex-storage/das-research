#!/bin/python3

import random
from bitarray import bitarray
from bitarray.util import zeros

class Block:
    """This class represents a block in the Ethereum blockchain."""

    def __init__(self, blockSizeR, blockSizeC=0):
        """Initialize the block with a data array of blocksize^2 zeros.

        BlockSizeR: row size
        BlockSizeC: column size (i.e. number of rows)
        """
        self.blockSizeR = blockSizeR
        self.blockSizeC = blockSizeC if blockSizeC else blockSizeR
        self.data = zeros(self.blockSizeR*self.blockSizeC)

    def fill(self):
        """It fills the block data with ones."""
        self.data.setall(1)

    def merge(self, merged):
        """It merges (OR) the existing block with the received one."""
        self.data |= merged.data

    def getSegment(self, rowID, columnID):
        """Check whether a segment is included"""
        return self.data[rowID*self.blockSizeR + columnID]

    def setSegment(self, rowID, columnID, value = 1):
        """Set value for a segment (default 1)"""
        self.data[rowID*self.blockSizeR + columnID] = value

    def getColumn(self, columnID):
        """It returns the block column corresponding to columnID."""
        return self.data[columnID::self.blockSizeR]

    def mergeColumn(self, columnID, column):
        """It merges (OR) the existing column with the received one."""
        self.data[columnID::self.blockSizeR] |= column

    def repairColumn(self, id):
        """It repairs the entire column if it has at least blockSizeC/2 ones.
            Returns: list of repaired segments
        """
        line = self.data[id::self.blockSizeR]
        success = line.count(1)
        if success >= self.blockSizeC/2:
            ret = ~line
            self.data[id::self.blockSizeR] = 1
        else:
            ret = zeros(self.blockSizeC)
        return ret

    def getRow(self, rowID):
        """It returns the block row corresponding to rowID."""
        return self.data[rowID*self.blockSizeR:(rowID+1)*self.blockSizeR]

    def mergeRow(self, rowID, row):
        """It merges (OR) the existing row with the received one."""
        self.data[rowID*self.blockSizeR:(rowID+1)*self.blockSizeR] |= row

    def repairRow(self, id):
        """It repairs the entire row if it has at least blockSizeR/2 ones.
            Returns: list of repaired segments.
        """
        line = self.data[id*self.blockSizeR:(id+1)*self.blockSizeR]
        success = line.count(1)
        if success >= self.blockSizeR/2:
            ret = ~line
            self.data[id*self.blockSizeR:(id+1)*self.blockSizeR] = 1
        else:
            ret = zeros(self.blockSizeR)
        return ret

    def print(self):
        """It prints the block in the terminal (outside of the logger rules))."""
        dash = "-" * (self.blockSizeR+2)
        print(dash)
        for i in range(self.blockSizeC):
            line = "|"
            for j in range(self.blockSizeR):
                line += "%i" % self.data[(i*self.blockSizeR)+j]
            print(line+"|")
        print(dash)

