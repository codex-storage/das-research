#!/bin/python

import networkx as nx
import logging, random
from datetime import datetime
from DAS.tools import *
from DAS.results import *
from DAS.observer import *
from DAS.validator import *

class Simulator:

    proposerID = 0
    logLevel = logging.INFO
    validators = []
    glob = []
    result = []
    shape = []
    logger = []
    format = {}

    def __init__(self, shape):
        self.shape = shape
        self.format = {"entity": "Simulator"}
        self.result = Result(self.shape)

    def initValidators(self):
        self.glob = Observer(self.logger, self.shape)
        self.glob.reset()
        self.validators = []
        rows = list(range(self.shape.blockSize)) * int(self.shape.chi*self.shape.numberValidators/self.shape.blockSize)
        columns = list(range(self.shape.blockSize)) * int(self.shape.chi*self.shape.numberValidators/self.shape.blockSize)
        random.shuffle(rows)
        random.shuffle(columns)
        for i in range(self.shape.numberValidators):
            val = Validator(i, int(not i!=0), self.logger, self.shape, rows, columns)
            if i == self.proposerID:
                val.initBlock()
                self.glob.setGoldenData(val.block)
            else:
                val.logIDs()
            self.validators.append(val)

    def initNetwork(self):
        self.shape.netDegree = 6
        rowChannels = [[] for i in range(self.shape.blockSize)]
        columnChannels = [[] for i in range(self.shape.blockSize)]
        for v in self.validators:
            for id in v.rowIDs:
                rowChannels[id].append(v)
            for id in v.columnIDs:
                columnChannels[id].append(v)

        for id in range(self.shape.blockSize):

            if (len(rowChannels[id]) < self.shape.netDegree):
                self.logger.error("Graph degree higher than %d" % len(rowChannels[id]), extra=self.format)
            G = nx.random_regular_graph(self.shape.netDegree, len(rowChannels[id]))
            if not nx.is_connected(G):
                self.logger.error("Graph not connected for row %d !" % id, extra=self.format)
            for u, v in G.edges:
                val1=rowChannels[id][u]
                val2=rowChannels[id][v]
                val1.rowNeighbors[id].update({val2.ID : Neighbor(val2, self.shape.blockSize)})
                val2.rowNeighbors[id].update({val1.ID : Neighbor(val1, self.shape.blockSize)})

            if (len(columnChannels[id]) < self.shape.netDegree):
                self.logger.error("Graph degree higher than %d" % len(columnChannels[id]), extra=self.format)
            G = nx.random_regular_graph(self.shape.netDegree, len(columnChannels[id]))
            if not nx.is_connected(G):
                self.logger.error("Graph not connected for column %d !" % id, extra=self.format)
            for u, v in G.edges:
                val1=columnChannels[id][u]
                val2=columnChannels[id][v]
                val1.columnNeighbors[id].update({val2.ID : Neighbor(val2, self.shape.blockSize)})
                val2.columnNeighbors[id].update({val1.ID : Neighbor(val1, self.shape.blockSize)})

    def initLogger(self):
        logger = logging.getLogger("DAS")
        logger.setLevel(self.logLevel)
        ch = logging.StreamHandler()
        ch.setLevel(self.logLevel)
        ch.setFormatter(CustomFormatter())
        logger.addHandler(ch)
        self.logger = logger


    def resetShape(self, shape):
        self.shape = shape
        self.result = Result(self.shape)
        for val in self.validators:
            val.shape.failureRate = shape.failureRate
            val.shape.chi = shape.chi


    def run(self):
        self.glob.checkRowsColumns(self.validators)
        self.validators[self.proposerID].broadcastBlock()
        arrived, expected = self.glob.checkStatus(self.validators)
        missingSamples = expected - arrived
        missingVector = []
        steps = 0
        while(True):
            missingVector.append(missingSamples)
            oldMissingSamples = missingSamples
            for i in range(0,self.shape.numberValidators):
                self.validators[i].sendRows()
                self.validators[i].sendColumns()
            for i in range(1,self.shape.numberValidators):
                self.validators[i].receiveRowsColumns()
            for i in range(1,self.shape.numberValidators):
                self.validators[i].restoreRows()
                self.validators[i].restoreColumns()
            for i in range(0,self.shape.numberValidators):
                self.validators[i].logRows()
                self.validators[i].logColumns()
                self.validators[i].updateStats()

            arrived, expected = self.glob.checkStatus(self.validators)
            missingSamples = expected - arrived
            missingRate = missingSamples*100/expected
            self.logger.debug("step %d, missing %d of %d (%0.02f %%)" % (steps, missingSamples, expected, missingRate), extra=self.format)
            if missingSamples == oldMissingSamples:
                #self.logger.info("The block cannot be recovered, failure rate %d!" % self.shape.failureRate, extra=self.format)
                missingVector.append(missingSamples)
                break
            elif missingSamples == 0:
                #self.logger.info("The entire block is available at step %d, with failure rate %d !" % (steps, self.shape.failureRate), extra=self.format)
                missingVector.append(missingSamples)
                break
            else:
                steps += 1

        self.result.populate(self.shape, missingVector)
        return self.result

