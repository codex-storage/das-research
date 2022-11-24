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

    def __init__(self, ID, chi, blockSize, proposer, failureRate, deterministic):
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
            if deterministic:
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

    def printRows(self):
        print("Val %d - Rows: " % self.ID, end="")
        print(self.rows)

    def printColumns(self):
        print("Val %d - Columns: " % self.ID, end="")
        print(self.columns)

    def checkRestoreRows(self, goldenData):
        for rid in range(len(self.rows)):
            row = self.rows[rid]
            failures = 0
            success = 0
            for i in row:
                if i == 0:
                    failures += 1
                elif i > 0 and i < 10:
                    success += 1
                else:
                    print("ERROR: Data has been corrupted")

            if failures > 0:
                if success >= len(row)/2:
                    for i in range(len(row)):
                        self.rows[rid][i] = goldenData[(self.rowIDs[rid]*self.blockSize)+i]
                    print("Val %d: Row %d data restored" % (self.ID, self.rowIDs[rid]))
                else:
                    print("WARNING Val %d: Row %d cannot be restored" %  (self.ID, self.rowIDs[rid]))

    def checkRestoreColumns(self, goldenData):
        for cid in range(len(self.columns)):
            column = self.columns[cid]
            failures = 0
            success = 0
            for i in column:
                if i == 0:
                    failures += 1
                elif i > 0 and i < 10:
                    success += 1
                else:
                    print("ERROR: Data has been corrupted")

            if failures > 0:
                if success >= len(column)/2:
                    for i in range(len(column)):
                        self.columns[cid][i] = goldenData[(i*self.blockSize)+self.columnIDs[cid]]
                    print("Val %d: Column %d data restored" % (self.ID, self.columnIDs[cid]))
                else:
                    print("Val %d: Column %d cannot be restored" % (self.ID, self.columnIDs[cid]))


class Observer:

    block = []
    blockSize = 0
    rows = []
    columns = []
    goldenData = []

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

    def setGoldenData(self, block):
        self.goldenData = [0] * self.blockSize * self.blockSize
        for i in range(self.blockSize*self.blockSize):
            self.goldenData[i] = block.data[i]

class Simulator:

    chi = 4
    blockSize = 16
    numberValidators = 32
    failureRate = 10
    proposerID = 0
    deterministic = 1
    validators = []
    glob = []

    def __init__(self):
        if not self.deterministic:
            random.seed(datetime.now())
        self.glob = Observer(self.blockSize)
        for i in range(self.numberValidators):
            val = Validator(i, self.chi, self.blockSize, int(not i!=0), self.failureRate, self.deterministic)
            if i == self.proposerID:
                val.initBlock()
                self.glob.setGoldenData(val.block)
            else:
                val.printIDs()
            self.validators.append(val)

    def run(self):
        broadcasted = Block(self.blockSize)
        self.glob.checkRowsColumns(self.validators)
        self.validators[self.proposerID].broadcastBlock(broadcasted)
        for i in range(1,self.numberValidators):
            self.validators[i].receiveRowsColumns(broadcasted)
            self.validators[i].printRows()
            self.validators[i].printColumns()
            self.validators[i].checkRestoreRows(self.glob.goldenData)
            self.validators[i].checkRestoreColumns(self.glob.goldenData)
            self.validators[i].printRows()
            self.validators[i].printColumns()


sim = Simulator()
sim.run()



