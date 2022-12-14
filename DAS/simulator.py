#!/bin/python

import logging
from datetime import datetime
from DAS.tools import *
from DAS.observer import *
from DAS.validator import *

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
                self.validators[i].restoreRows()
                self.validators[i].sendRows(self.glob.broadcasted)
                self.validators[i].logRows()
                self.validators[i].logColumns()
                # Columns
                self.validators[i].restoreColumns()
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

