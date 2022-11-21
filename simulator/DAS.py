#! /bin/python3

import random
from datetime import datetime

class Block:

    blockSize = 0
    data = []

    def __init__(self, size):
        self.blockSize = size
        self.data = [0] * (self.blockSize*self.blockSize)

    def fill(self):
        for i in range(self.blockSize*self.blockSize):
            self.data[i] = random.randint(1, 9)

    def print(self):
        for i in range(self.blockSize):
            for j in range(self.blockSize):
                print("%i" % self.data[(i*self.blockSize)+j], end="")
            print("")


class Validator:

    ID = 0
    chi = 0
    blocksize = 0
    block = []
    rowIDs = []
    columnIDs = []
    rows = []
    columns = []
    proposer = 0
    failureRate = 0

    def __init__(self, ID, chi, blockSize, proposer, failureRate):
        self.ID = ID
        self.blockSize = blockSize
        self.proposer = proposer
        self.failureRate = failureRate
        if chi < 1:
            print("ERROR: chi has to be greater than 0")
        elif chi > blockSize:
            print("ERROR: chi has to be smaller than %d" % blockSize)
        else:
            self.chi = chi
            self.rowIDs = []
            self.columnIDs = []
            random.seed(self.ID)
            for i in range(self.chi):
                self.rowIDs.append(random.randint(0,blockSize-1))
                self.columnIDs.append(random.randint(0,blockSize-1))

    def printIDs(self):
        if self.proposer == 1:
            print("Hi! I am validator %d and I am a block proposer."% self.ID)
        else:
            print("Hi! I am validator %d and these are my rows and columns."% self.ID)
            print("Selected rows: ", end="")
            for i in range(self.chi):
                print("%d " % self.rowIDs[i], end="")
            print("")
            print("Selected columns: ", end="")
            for i in range(self.chi):
                print("%d " % self.columnIDs[i], end="")
            print("")

    def initBlock(self):
        print("Hi! I am validator %d and I am a block proposer."% self.ID)
        self.block = Block(self.blockSize)
        self.block.fill()
        self.block.print()

    def broadcastBlock(self, broadcasted):
        if self.proposer == 0:
            print("ERROR: I am validator %d and I am NOT a block proposer" % self.ID)
        else:
            print("I am validator %d and I am broadcasting my block..." % self.ID)
            tempBlock = self.block
            order = [i for i in range(self.blockSize * self.blockSize)]
            random.shuffle(order)
            while(order):
                i = order.pop()
                if (random.randint(0,99) > self.failureRate):
                    broadcasted.data[i] = self.block.data[i]
            broadcasted.print()

    def getColumn(self, columnID, broadcasted):
        column = [0] * self.blockSize
        for i in range(self.blockSize):
            column[i] = broadcasted.data[(i*self.blockSize)+columnID]
        self.columns.append(column)

    def getRow(self, rowID, broadcasted):
        row = [0] * self.blockSize
        for i in range(self.blockSize):
            row[i] = broadcasted.data[(rowID*self.blockSize)+i]
        self.rows.append(row)

    def receiveRowsColumns(self, broadcasted):
        self.rows = []
        self.columns = []
        if self.proposer == 1:
            print("ERROR: I am validator %d and I am a block proposer" % self.ID)
        else:
            print("I am validator %d and I am receiving the data..." % self.ID)
            for r in self.rowIDs:
                self.getRow(r, broadcasted)
            for c in self.columnIDs:
                self.getColumn(c, broadcasted)
            print(self.rows)
            print(self.columns)


class Observer:

    block = []
    blockSize = 0
    rows = []
    columns = []

    def __init__(self, blockSize):
        self.blockSize = blockSize
        self.block = [0] * self.blockSize * self.blockSize
        self.rows = [0] * self.blockSize
        self.columns = [0] * self.blockSize

    def checkRowsColumns(self, validators):
        for val in validators:
            if val.proposer == 0:
                for r in val.rowIDs:
                    self.rows[r] += 1
                for c in val.columnIDs:
                    self.columns[c] += 1

        for i in range(self.blockSize):
            print("Row/Column %d have %d and %d validators assigned." % (i, self.rows[i], self.columns[i]))
            if self.rows[i] == 0 or self.columns[i] == 0:
                print("WARNING: There is a row/column that has not been assigned")


class Simulator:

    chi = 2
    blockSize = 8
    numberValidators = 16
    proposerID = 0
    validators = []
    glob = []

    def __init__(self):
        random.seed(datetime.now())
        self.glob = Observer(self.blockSize)
        for i in range(self.numberValidators):
            if i == self.proposerID:
                val = Validator(i, self.chi, self.blockSize, 1, 10)
                val.initBlock()
            else:
                val = Validator(i, self.chi, self.blockSize, 0, 10)
                val.printIDs()
            self.validators.append(val)

    def run(self):
        broadcasted = Block(self.blockSize)
        self.glob.checkRowsColumns(self.validators)
        self.validators[self.proposerID].broadcastBlock(broadcasted)
        for i in range(1,self.numberValidators):
            self.validators[i].receiveRowsColumns(broadcasted)

sim = Simulator()
sim.run()



