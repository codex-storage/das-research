#!/bin/python3

import random
from bitarray import bitarray
from bitarray.util import zeros

class Block:

    blockSize = 0
    data = bitarray()

    def __init__(self, size):
        self.blockSize = size
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

    def getColumn(self, id):
        return self.columns[id]

    def mergeColumn(self, id, column):
        self.columns[id] |= column
        for xid, line in self.rows.items():
            line[id] |= self.columns[id][xid]

    def repairColumn(self, id):
        success = self.columns[id].count(1)
        if success >= self.blockSize/2:
            self.columns[id].setall(1)

    def getRow(self, id):
        return self.rows[id]

    def mergeRow(self, id, row):
        self.rows[id] |= row
        for xid, line in self.columns.items():
            line[id] |= self.rows[id][xid]

    def repairRow(self, id):
        success = self.rows[id].count(1)
        if success >= self.blockSize/2:
            self.rows[id].setall(1)

    # def print(self):
    #     dash = "-" * (self.blockSize+2)
    #     print(dash)
    #     for i in range(self.blockSize):
    #         line = "|"
    #         for j in range(self.blockSize):
    #             line += "%i" % self.data[(i*self.blockSize)+j]
    #         print(line+"|")
    #     print(dash)

