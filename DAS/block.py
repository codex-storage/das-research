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

class SparseBlock:

    def __init__(self, size, rows, columns):
        self.blockSize = size
        self.rows = {r: zeros(self.blockSize) for r in rows}
        self.columns = {r: zeros(self.blockSize) for r in columns}

    def fill(self):
        for line in self.rows:
            line.setall(1)
        for line in self.columns:
            line.setall(1)

    def merge(self, merged):
        for id in self.rows:
            self.mergeRow(id, merged.getRow(id))
        for id in self.columns:
            self.mergeColumn(id, merged.getColumn(id))

    def getSegment(self, rowID, columnID):
        """Check whether a segment is included"""
        ret = 0

        r = self.rows.get(rowID)
        if r:
            ret |= r[columnID]

        c = self.columns.get(columnID)
        if c:
            ret |= c[rowID]

        return ret

    def setSegment(self, rowID, columnID, value = 1):
        """Set value for a segment (default 1)"""
        r = self.rows.get(rowID)
        if r:
            r[columnID] = 1

        c = self.columns.get(columnID)
        if c:
            c[rowID] = 1

    def getColumn(self, id):
        return self.columns[id]

    def mergeColumn(self, id, column):
        self.columns[id] |= column
        for xid, line in self.rows.items():
            line[id] |= self.columns[id][xid]

    def repairColumn(self, id):
        success = self.columns[id].count(1)
        if success >= self.blockSize/2:
            ret = ~self.columns[id]
            self.columns[id].setall(1)
        else:
            ret = zeros(self.blockSize)
        return ret

    def getRow(self, id):
        return self.rows[id]

    def mergeRow(self, id, row):
        self.rows[id] |= row
        for xid, line in self.columns.items():
            line[id] |= self.rows[id][xid]

    def repairRow(self, id):
        success = self.rows[id].count(1)
        if success >= self.blockSize/2:
            ret = ~self.rows[id]
            self.rows[id].setall(1)
        else:
            ret = zeros(self.blockSize)
        return ret

    # def print(self):
    #     dash = "-" * (self.blockSize+2)
    #     print(dash)
    #     for i in range(self.blockSize):
    #         line = "|"
    #         for j in range(self.blockSize):
    #             line += "%i" % self.data[(i*self.blockSize)+j]
    #         print(line+"|")
    #     print(dash)

