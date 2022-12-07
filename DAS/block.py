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
        for i in range(self.blockSize*self.blockSize):
            self.data[i] = 1

    def getColumn(self, columnID):
        return self.data[columnID::self.blockSize]

    def getRow(self, rowID):
        return self.data[rowID*self.blockSize:(rowID+1)*self.blockSize]

    def print(self):
        dash = "-" * (self.blockSize+2)
        print(dash)
        for i in range(self.blockSize):
            line = "|"
            for j in range(self.blockSize):
                line += "%i" % self.data[(i*self.blockSize)+j]
            print(line+"|")
        print(dash)

