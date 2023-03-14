#!/bin/python

import networkx as nx
import logging, random
from datetime import datetime
from statistics import mean
from DAS.tools import *
from DAS.results import *
from DAS.observer import *
from DAS.validator import *

class Simulator:
    """This class implements the main DAS simulator."""

    def __init__(self, shape, config):
        """It initializes the simulation with a set of parameters (shape)."""
        self.shape = shape
        self.config = config
        self.format = {"entity": "Simulator"}
        self.result = Result(self.shape)
        self.validators = []
        self.logger = []
        self.logLevel = config.logLevel
        self.proposerID = 0
        self.glob = []

    def initValidators(self):
        """It initializes all the validators in the network."""
        self.glob = Observer(self.logger, self.shape)
        self.glob.reset()
        self.validators = []
        if self.config.evenLineDistribution:
            rows = list(range(self.shape.blockSize)) * int(self.shape.chi*self.shape.numberNodes/self.shape.blockSize)
            columns = list(range(self.shape.blockSize)) * int(self.shape.chi*self.shape.numberNodes/self.shape.blockSize)
            random.shuffle(rows)
            random.shuffle(columns)
        for i in range(self.shape.numberNodes):
            if self.config.evenLineDistribution:
                val = Validator(i, int(not i!=0), self.logger, self.shape,
                            rows[(i*self.shape.chi):((i+1)*self.shape.chi)],
                            columns[(i*self.shape.chi):((i+1)*self.shape.chi)])
            else:
                val = Validator(i, int(not i!=0), self.logger, self.shape)
            if i == self.proposerID:
                val.initBlock()
            else:
                val.logIDs()
            self.validators.append(val)

    def initNetwork(self):
        """It initializes the simulated network."""
        rowChannels = [[] for i in range(self.shape.blockSize)]
        columnChannels = [[] for i in range(self.shape.blockSize)]
        for v in self.validators:
            if not (self.proposerPublishOnly and v.amIproposer):
                for id in v.rowIDs:
                    rowChannels[id].append(v)
                for id in v.columnIDs:
                    columnChannels[id].append(v)

        for id in range(self.shape.blockSize):

            # If the number of nodes in a channel is smaller or equal to the
            # requested degree, a fully connected graph is used. For n>d, a random
            # d-regular graph is set up. (For n=d+1, the two are the same.)
            if not rowChannels[id]:
                self.logger.error("No nodes for row %d !" % id, extra=self.format)
                continue
            elif (len(rowChannels[id]) <= self.shape.netDegree):
                self.logger.debug("Graph fully connected with degree %d !" % (len(rowChannels[id]) - 1), extra=self.format)
                G = nx.complete_graph(len(rowChannels[id]))
            else:
                G = nx.random_regular_graph(self.shape.netDegree, len(rowChannels[id]))
            if not nx.is_connected(G):
                self.logger.error("Graph not connected for row %d !" % id, extra=self.format)
            for u, v in G.edges:
                val1=rowChannels[id][u]
                val2=rowChannels[id][v]
                val1.rowNeighbors[id].update({val2.ID : Neighbor(val2, 0, self.shape.blockSize)})
                val2.rowNeighbors[id].update({val1.ID : Neighbor(val1, 0, self.shape.blockSize)})

            if not columnChannels[id]:
                self.logger.error("No nodes for column %d !" % id, extra=self.format)
                continue
            elif (len(columnChannels[id]) <= self.shape.netDegree):
                self.logger.debug("Graph fully connected with degree %d !" % (len(columnChannels[id]) - 1), extra=self.format)
                G = nx.complete_graph(len(columnChannels[id]))
            else:
                G = nx.random_regular_graph(self.shape.netDegree, len(columnChannels[id]))
            if not nx.is_connected(G):
                self.logger.error("Graph not connected for column %d !" % id, extra=self.format)
            for u, v in G.edges:
                val1=columnChannels[id][u]
                val2=columnChannels[id][v]
                val1.columnNeighbors[id].update({val2.ID : Neighbor(val2, 1, self.shape.blockSize)})
                val2.columnNeighbors[id].update({val1.ID : Neighbor(val1, 1, self.shape.blockSize)})

        for v in self.validators:
            if (self.proposerPublishOnly and v.amIproposer):
                for id in v.rowIDs:
                    count = min(self.proposerPublishTo, len(rowChannels[id]))
                    publishTo = random.sample(rowChannels[id], count)
                    for vi in publishTo:
                        v.rowNeighbors[id].update({vi.ID : Neighbor(vi, 0, self.shape.blockSize)})
                for id in v.columnIDs:
                    count = min(self.proposerPublishTo, len(columnChannels[id]))
                    publishTo = random.sample(columnChannels[id], count)
                    for vi in publishTo:
                        v.columnNeighbors[id].update({vi.ID : Neighbor(vi, 1, self.shape.blockSize)})

        if self.logger.isEnabledFor(logging.DEBUG):
            for i in range(0, self.shape.numberNodes):
                self.logger.debug("Val %d : rowN %s", i, self.validators[i].rowNeighbors, extra=self.format)
                self.logger.debug("Val %d : colN %s", i, self.validators[i].columnNeighbors, extra=self.format)

    def initLogger(self):
        """It initializes the logger."""
        logger = logging.getLogger("DAS")
        if len(logger.handlers) == 0:
            logger.setLevel(self.logLevel)
            ch = logging.StreamHandler()
            ch.setLevel(self.logLevel)
            ch.setFormatter(CustomFormatter())
            logger.addHandler(ch)
        self.logger = logger


    def resetShape(self, shape):
        """It resets the parameters of the simulation."""
        self.shape = shape
        self.result = Result(self.shape)
        for val in self.validators:
            val.shape.failureRate = shape.failureRate
            val.shape.chi = shape.chi
            val.shape.vpn1 = shape.vpn1
            val.shape.vpn2 = shape.vpn2

        # In GossipSub the initiator might push messages without participating in the mesh.
        # proposerPublishOnly regulates this behavior. If set to true, the proposer is not
        # part of the p2p distribution graph, only pushes segments to it. If false, the proposer
        # might get back segments from other peers since links are symmetric.
        self.proposerPublishOnly = True

        # If proposerPublishOnly == True, this regulates how many copies of each segment are
        # pushed out by the proposer.
        # 1: the data is sent out exactly once on rows and once on columns (2 copies in total)
        # self.shape.netDegree: default behavior similar (but not same) to previous code
        self.proposerPublishTo = self.shape.netDegree


    def run(self):
        """It runs the main simulation until the block is available or it gets stucked."""
        self.glob.checkRowsColumns(self.validators)
        self.validators[self.proposerID].broadcastBlock()
        arrived, expected = self.glob.checkStatus(self.validators)
        missingSamples = expected - arrived
        missingVector = []
        steps = 0
        while(True):
            missingVector.append(missingSamples)
            oldMissingSamples = missingSamples
            self.logger.debug("PHASE SEND %d" % steps, extra=self.format)
            for i in range(0,self.shape.numberNodes):
                self.validators[i].send()
            self.logger.debug("PHASE RECEIVE %d" % steps, extra=self.format)
            for i in range(1,self.shape.numberNodes):
                self.validators[i].receiveRowsColumns()
            self.logger.debug("PHASE RESTORE %d" % steps, extra=self.format)
            for i in range(1,self.shape.numberNodes):
                self.validators[i].restoreRows()
                self.validators[i].restoreColumns()
            self.logger.debug("PHASE LOG %d" % steps, extra=self.format)
            for i in range(0,self.shape.numberNodes):
                self.validators[i].logRows()
                self.validators[i].logColumns()

            # log TX and RX statistics
            statsTxInSlot = [v.statsTxInSlot for v in self.validators]
            statsRxInSlot = [v.statsRxInSlot for v in self.validators]
            self.logger.debug("step %d: TX_prod=%.1f, RX_prod=%.1f, TX_avg=%.1f, TX_max=%.1f, Rx_avg=%.1f, Rx_max=%.1f" % 
                (steps, statsTxInSlot[0], statsRxInSlot[0],
                 mean(statsTxInSlot[1:]), max(statsTxInSlot[1:]),
                 mean(statsRxInSlot[1:]), max(statsRxInSlot[1:])), extra=self.format)
            for i in range(0,self.shape.numberNodes):
                self.validators[i].updateStats()

            arrived, expected = self.glob.checkStatus(self.validators)
            missingSamples = expected - arrived
            missingRate = missingSamples*100/expected
            self.logger.debug("step %d, missing %d of %d (%0.02f %%)" % (steps, missingSamples, expected, missingRate), extra=self.format)
            if missingSamples == oldMissingSamples:
                self.logger.debug("The block cannot be recovered, failure rate %d!" % self.shape.failureRate, extra=self.format)
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

