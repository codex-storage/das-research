#! /bin/python3

import random, logging, time
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
        dash = "-" * (self.blockSize+2)
        print(dash)
        for i in range(self.blockSize):
            line = "|"
            for j in range(self.blockSize):
                line += "%i" % self.data[(i*self.blockSize)+j]
            print(line+"|")
        print(dash)

class CustomFormatter(logging.Formatter):

    blue = "\x1b[34;20m"
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(levelname)s : %(entity)s : %(message)s"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: blue + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

class Validator:

    ID = 0
    chi = 0
    format = {}
    blocksize = 0
    block = []
    rowIDs = []
    columnIDs = []
    rows = []
    columns = []
    proposer = 0
    failureRate = 0
    logger = []

    def __init__(self, ID, chi, blockSize, proposer, failureRate, deterministic, logger):
        FORMAT = "%(levelname)s : %(entity)s : %(message)s"
        self.ID = ID
        self.format = {"entity": "Val "+str(self.ID)}
        self.blockSize = blockSize
        self.proposer = proposer
        self.failureRate = failureRate
        self.logger = logger
        if chi < 1:
            self.logger.error("Chi has to be greater than 0", extra=self.format)
        elif chi > blockSize:
            self.logger.error("Chi has to be smaller than %d" % blockSize, extra=self.format)
        else:
            self.chi = chi
            self.rowIDs = []
            self.columnIDs = []
            if deterministic:
                random.seed(self.ID)
            lr = [i for i in range(self.blockSize)]
            lc = [i for i in range(self.blockSize)]
            random.shuffle(lr)
            random.shuffle(lc)
            for i in range(self.chi): # TODO : Avoid doubles
                self.rowIDs.append(lr.pop())
                self.columnIDs.append(lc.pop())

    def logIDs(self):
        if self.proposer == 1:
            self.logger.warning("I am a block proposer."% self.ID)
        else:
            self.logger.debug("Selected rows: "+str(self.rowIDs), extra=self.format)
            self.logger.debug("Selected columns: "+str(self.columnIDs), extra=self.format)

    def initBlock(self):
        self.logger.debug("I am a block proposer.", extra=self.format)
        self.block = Block(self.blockSize)
        self.block.fill()
        #self.block.print()

    def broadcastBlock(self, broadcasted):
        if self.proposer == 0:
            self.logger.error("I am NOT a block proposer", extra=self.format)
        else:
            self.logger.debug("Broadcasting my block...", extra=self.format)
            tempBlock = self.block
            order = [i for i in range(self.blockSize * self.blockSize)]
            random.shuffle(order)
            while(order):
                i = order.pop()
                if (random.randint(0,99) > self.failureRate):
                    broadcasted.data[i] = self.block.data[i]
            #broadcasted.print()

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
            self.logger.error("I am a block proposer", extra=self.format)
        else:
            self.logger.debug("Receiving the data...", extra=self.format)
            for r in self.rowIDs:
                self.getRow(r, broadcasted)
            for c in self.columnIDs:
                self.getColumn(c, broadcasted)

    def sendColumn(self, c, columnID, broadcasted):
        column = [0] * self.blockSize
        for i in range(self.blockSize):
            if broadcasted.data[(i*self.blockSize)+columnID] == 0:
                broadcasted.data[(i*self.blockSize)+columnID] = self.columns[c][i]

    def sendRow(self, r, rowID, broadcasted):
        for i in range(self.blockSize):
            if broadcasted.data[(rowID*self.blockSize)+i] == 0:
                broadcasted.data[(rowID*self.blockSize)+i] = self.rows[r][i]

    def sendRows(self, broadcasted):
        if self.proposer == 1:
            self.logger.error("I am a block proposer", extra=self.format)
        else:
            self.logger.debug("Sending restored rows...", extra=self.format)
            for r in range(len(self.rowIDs)):
                self.sendRow(r, self.rowIDs[r], broadcasted)

    def sendColumns(self, broadcasted):
        if self.proposer == 1:
            self.logger.error("I am a block proposer", extra=self.format)
        else:
            self.logger.debug("Sending restored columns...", extra=self.format)
            for c in range(len(self.columnIDs)):
                self.sendColumn(c, self.columnIDs[c], broadcasted)

    def logRows(self):
        self.logger.debug("Rows: "+str(self.rows), extra=self.format)

    def logColumns(self):
        self.logger.debug("Columns: "+str(self.columns), extra=self.format)

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
                    self.logger.error("Data has been corrupted")

            if failures > 0:
                if success >= len(row)/2:
                    for i in range(len(row)):
                        self.rows[rid][i] = goldenData[(self.rowIDs[rid]*self.blockSize)+i]
                    self.logger.debug("%d samples restored in row %d" % (failures, self.rowIDs[rid]), extra=self.format )
                else:
                    self.logger.debug("Row %d cannot be restored" %  (self.rowIDs[rid]), extra=self.format)

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
                    self.logger.error("Data has been corrupted", extra=self.format)

            if failures > 0:
                if success >= len(column)/2:
                    for i in range(len(column)):
                        self.columns[cid][i] = goldenData[(i*self.blockSize)+self.columnIDs[cid]]
                    self.logger.debug("%d samples restored in column %d" % (failures, self.columnIDs[cid]), extra=self.format)
                else:
                    self.logger.debug("Column %d cannot be restored" % (self.columnIDs[cid]), extra=self.format)


class Observer:

    block = []
    blockSize = 0
    rows = []
    columns = []
    goldenData = []
    broadcasted = []
    logger = []

    def __init__(self, blockSize, logger):
        self.format = {"entity": "Observer"}
        self.blockSize = blockSize
        self.logger = logger

    def reset(self):
        self.block = [0] * self.blockSize * self.blockSize
        self.goldenData = [0] * self.blockSize * self.blockSize
        self.rows = [0] * self.blockSize
        self.columns = [0] * self.blockSize
        self.broadcasted = Block(self.blockSize)

    def checkRowsColumns(self, validators):
        for val in validators:
            if val.proposer == 0:
                for r in val.rowIDs:
                    self.rows[r] += 1
                for c in val.columnIDs:
                    self.columns[c] += 1

        for i in range(self.blockSize):
            self.logger.debug("Row/Column %d have %d and %d validators assigned." % (i, self.rows[i], self.columns[i]), extra=self.format)
            if self.rows[i] == 0 or self.columns[i] == 0:
                self.logger.warning("There is a row/column that has not been assigned", extra=self.format)

    def setGoldenData(self, block):
        for i in range(self.blockSize*self.blockSize):
            self.goldenData[i] = block.data[i]

    def checkBroadcasted(self):
        zeros = 0
        for i in range(self.blockSize * self.blockSize):
            if self.broadcasted.data[i] == 0:
                zeros += 1
        if zeros > 0:
            self.logger.debug("There are %d missing samples in the network" % zeros, extra=self.format)
        return zeros


class Simulator:

    chi = 8
    blockSize = 256
    numberValidators = 8192
    failureRate = 0
    proposerID = 0
    logLevel = logging.INFO
    deterministic = 0
    validators = []
    glob = []
    logger = []
    format = {}
    steps = 0

    def __init__(self, failureRate):
        self.failureRate = failureRate
        self.format = {"entity": "Simulator"}
        self.steps = 0

    def initValidators(self):
        if not self.deterministic:
            random.seed(datetime.now())
        self.glob = Observer(self.blockSize, self.logger)
        self.glob.reset()
        self.validators = []
        for i in range(self.numberValidators):
            val = Validator(i, self.chi, self.blockSize, int(not i!=0), self.failureRate, self.deterministic, self.logger)
            if i == self.proposerID:
                val.initBlock()
                self.glob.setGoldenData(val.block)
            else:
                val.logIDs()
            self.validators.append(val)

    def initLogger(self):
        logger = logging.getLogger("DAS")
        logger.setLevel(self.logLevel)
        ch = logging.StreamHandler()
        ch.setLevel(self.logLevel)
        ch.setFormatter(CustomFormatter())
        logger.addHandler(ch)
        self.logger = logger

    def resetFailureRate(self, failureRate):
        self.failureRate = failureRate

    def run(self):
        self.glob.checkRowsColumns(self.validators)
        self.validators[self.proposerID].broadcastBlock(self.glob.broadcasted)
        missingSamples = self.glob.checkBroadcasted()
        self.steps = 0
        while(missingSamples > 0):
            oldMissingSamples = missingSamples
            self.logger.debug("Step %d:" % self.steps, extra=self.format)
            for i in range(1,self.numberValidators):
                self.validators[i].receiveRowsColumns(self.glob.broadcasted)
                #Rows
                self.validators[i].checkRestoreRows(self.glob.goldenData)
                self.validators[i].sendRows(self.glob.broadcasted)
                self.validators[i].logRows()
                self.validators[i].logColumns()
                # Columns
                self.validators[i].checkRestoreColumns(self.glob.goldenData)
                self.validators[i].sendColumns(self.glob.broadcasted)
                self.validators[i].logRows()
                self.validators[i].logColumns()

            missingSamples = self.glob.checkBroadcasted()
            if missingSamples == oldMissingSamples:
                break
            elif missingSamples == 0:
                break
            else:
                self.steps += 1

        if missingSamples == 0:
            self.logger.debug("The entire block is available at step %d, with failure rate %d !" % (self.steps, self.failureRate), extra=self.format)
            return 0
        else:
            self.logger.debug("The block cannot be recovered, failure rate %d!" % self.failureRate, extra=self.format)
            return 1

def study():
    sim = Simulator(0)
    sim.initLogger()
    maxTries = 5
    step = 25
    frRange = []
    resultRange = []
    simCnt = 0
    sim.logger.info("Starting %d simulations:" % (maxTries*100), extra=sim.format)
    start = time.time()
    for fr in range(0, 100, step):
        if fr % 10 == 0:
            sim.logger.info("Failure rate %d %% ..." % fr, extra=sim.format)
        sim.resetFailureRate(fr)
        result = 0
        for i in range(maxTries):
            sim.initValidators()
            result += sim.run()
            simCnt += 1
        frRange.append(fr)
        resultRange.append(100-result)
    end = time.time()
    sim.logger.info("A total of %d simulations ran in %d seconds" % (simCnt, end-start), extra=sim.format)
    for i in range(len(frRange)):
        sim.logger.info("For failure rate of %d we got %d %% success rate in DAS!" % (frRange[i], resultRange[i]), extra=sim.format)


study()

