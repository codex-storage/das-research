#!/bin/python3

import random

class Block:

    blockSize = 0
    data = []

    def __init__(self, size):
        self.blockSize = size
        self.data = [0] * (self.blockSize*self.blockSize)

    def fill(self):
        for i in range(self.blockSize*self.blockSize):
            self.data[i] = random.randint(1, 9)

    def getColumn(self, columnID):
        column = [0] * self.blockSize
        for i in range(self.blockSize):
            column[i] = self.data[(i*self.blockSize)+columnID]
        return column

    def getRow(self, rowID):
        row = [0] * self.blockSize
        for i in range(self.blockSize):
            row[i] = self.data[(rowID*self.blockSize)+i]
        return row

    def print(self):
        dash = "-" * (self.blockSize+2)
        print(dash)
        for i in range(self.blockSize):
            line = "|"
            for j in range(self.blockSize):
                line += "%i" % self.data[(i*self.blockSize)+j]
            print(line+"|")
        print(dash)

