#!/bin/python

import networkx as nx
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

    def initNetwork(self, d=6):
        rowChannels = [[] for i in range(self.blockSize)]
        columnChannels = [[] for i in range(self.blockSize)]
        for v in self.validators:
            for id in v.rowIDs:
                rowChannels[id].append(v)
            for id in v.columnIDs:
                columnChannels[id].append(v)

        for id in range(self.blockSize):
            G = nx.random_regular_graph(d, len(rowChannels[id]))
            if not nx.is_connected(G):
                self.logger.error("graph not connected for row %d !" % id, extra=self.format)
            for u, v in G.edges:
                val1=rowChannels[id][u]
                val2=rowChannels[id][v]
                val1.rowNeighbors[id].append(val2)
                val2.rowNeighbors[id].append(val1)
            G = nx.random_regular_graph(d, len(columnChannels[id]))
            if not nx.is_connected(G):
                self.logger.error("graph not connected for column %d !" % id, extra=self.format)
            for u, v in G.edges:
                val1=columnChannels[id][u]
                val2=columnChannels[id][v]
                val1.columnNeighbors[id].append(val2)
                val2.columnNeighbors[id].append(val1)

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
        self.validators[self.proposerID].broadcastBlock()
        arrived, expected = self.glob.checkStatus(self.validators)
        missingSamples = expected - arrived
        self.steps = 0
        while(missingSamples > 0):
            oldMissingSamples = missingSamples
            for i in range(1,self.numberValidators):
                self.validators[i].receiveRowsColumns()
            for i in range(1,self.numberValidators):
                self.validators[i].restoreRows()
                self.validators[i].restoreColumns()
                self.validators[i].sendRows()
                self.validators[i].sendColumns()
                self.validators[i].logRows()
                self.validators[i].logColumns()

            arrived, expected = self.glob.checkStatus(self.validators)
            missingSamples = expected - arrived
            missingRate = missingSamples*100/expected
            self.logger.info("step %d, missing %d of %d (%0.02f %%)" % (self.steps, missingSamples, expected, missingRate), extra=self.format)
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

