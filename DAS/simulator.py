#!/bin/python

import networkx as nx
import logging, random
import pandas as pd
from functools import partial, partialmethod
from datetime import datetime
from DAS.tools import *
from DAS.results import *
from DAS.observer import *
from DAS.node import *

class Simulator:
    """This class implements the main DAS simulator."""

    def __init__(self, shape, config, execID):
        """It initializes the simulation with a set of parameters (shape)."""
        self.shape = shape
        self.config = config
        self.format = {"entity": "Simulator"}
        self.execID = execID
        self.result = Result(self.shape, self.execID)
        self.validators = []
        self.logger = []
        self.logLevel = config.logLevel
        self.proposerID = 0
        self.glob = []
        self.execID = execID
        self.distR = []
        self.distC = []
        self.nodeRows = []
        self.nodeColumns = []

        # In GossipSub the initiator might push messages without participating in the mesh.
        # proposerPublishOnly regulates this behavior. If set to true, the proposer is not
        # part of the p2p distribution graph, only pushes segments to it. If false, the proposer
        # might get back segments from other peers since links are symmetric.
        self.proposerPublishOnly = True

        # If proposerPublishOnly == True, this regulates how many copies of each segment are
        # pushed out by the proposer.
        # 1: the data is sent out exactly once on rows and once on columns (2 copies in total)
        # self.shape.netDegree: default behavior similar (but not same) to previous code
        self.proposerPublishToR = config.evalConf(self, config.proposerPublishToR, shape)
        self.proposerPublishToC = config.evalConf(self, config.proposerPublishToR, shape)

    def initValidators(self):
        """It initializes all the validators in the network."""
        self.glob = Observer(self.logger, self.shape)
        self.validators = []
        evenLineDistribution = False
        if evenLineDistribution:

            lightNodes = int(self.shape.numberNodes * self.shape.class1ratio)
            heavyNodes = self.shape.numberNodes - lightNodes
            lightVal = lightNodes * self.shape.vpn1
            heavyVal = heavyNodes * self.shape.vpn2
            totalValidators = lightVal + heavyVal
            totalRows = totalValidators * self.shape.custodyRows
            totalColumns = totalValidators * self.shape.custodyCols
            rows =    list(range(self.shape.nbRows)) * (int(totalRows/self.shape.nbRows)+1)
            columns = list(range(self.shape.nbCols)) * (int(totalColumns/self.shape.nbCols)+1)
            rows =    rows[0:totalRows]
            columns = columns[0:totalColumns]
            random.shuffle(rows)
            random.shuffle(columns)
            offsetR = lightVal*self.shape.custodyRows
            offsetC = lightVal*self.shape.custodyCols
            self.logger.debug("There is a total of %d nodes, %d light and %d heavy." % (self.shape.numberNodes, lightNodes, heavyNodes), extra=self.format)
            self.logger.debug("There is a total of %d validators, %d in light nodes and %d in heavy nodes" % (totalValidators, lightVal, heavyVal), extra=self.format)
            self.logger.debug("Shuffling a total of %d rows to be assigned (X=%d)" % (len(rows), self.shape.custodyRows), extra=self.format)
            self.logger.debug("Shuffling a total of %d columns to be assigned (X=%d)" % (len(columns), self.shape.custodyCols), extra=self.format)
            self.logger.debug("Shuffled rows: %s" % str(rows), extra=self.format)
            self.logger.debug("Shuffled columns: %s" % str(columns), extra=self.format)

        assignedRows = []
        assignedCols = []
        maliciousNodesCount = int((self.shape.maliciousNodes / 100) * self.shape.numberNodes)
        remainingMaliciousNodes = maliciousNodesCount

        for i in range(self.shape.numberNodes):
            if i == 0:
                amImalicious_value = 0
            else:
                if not self.config.randomizeMaliciousNodes:
                    # Assign based on predefined pattern when randomization is turned off
                    if i < maliciousNodesCount + 1:
                        amImalicious_value = 1
                    else:
                        amImalicious_value = 0
                else:
                    # Randomly assign amImalicious_value when randomization is turned on
                    if remainingMaliciousNodes > 0 and random.random() < (self.shape.maliciousNodes / 100):
                        amImalicious_value = 1
                        remainingMaliciousNodes -= 1
                    else:
                        amImalicious_value = 0
    
            if evenLineDistribution:
                if i < int(lightVal/self.shape.vpn1):  # First start with the light nodes
                    startR =   i  *self.shape.custodyRows*self.shape.vpn1
                    endR   = (i+1)*self.shape.custodyRows*self.shape.vpn1
                    startC =   i  *self.shape.custodyCols*self.shape.vpn1
                    endC   = (i+1)*self.shape.custodyCols*self.shape.vpn1
                else:
                    j = i - int(lightVal/self.shape.vpn1)
                    startR = offsetR+(  j  *self.shape.custodyRows*self.shape.vpn2)
                    endR   = offsetR+((j+1)*self.shape.custodyRows*self.shape.vpn2)
                    startC = offsetC+(  j  *self.shape.custodyCols*self.shape.vpn2)
                    endC   = offsetC+((j+1)*self.shape.custodyCols*self.shape.vpn2)
                r = rows[startR:endR]
                c = columns[startC:endC]
                val = Node(i, int(not i!=0), amImalicious_value, self.logger, self.shape, self.config, r, c)
                self.logger.debug("Node %d has row IDs: %s" % (val.ID, val.rowIDs), extra=self.format)
                self.logger.debug("Node %d has column IDs: %s" % (val.ID, val.columnIDs), extra=self.format)
                assignedRows = assignedRows + list(r)
                assignedCols = assignedCols + list(c)
                self.nodeRows.append(val.rowIDs)
                self.nodeColumns.append(val.columnIDs)

            else:
                if self.shape.custodyCols > self.shape.nbCols:
                    self.logger.error("custodyCols has to be smaller than %d" % self.shape.nbCols)
                elif self.shape.custodyRows > self.shape.nbRows:
                    self.logger.error("custodyRows has to be smaller than %d" % self.shape.nbRows)

                vs = []
                nodeClass = 1 if (i <= self.shape.numberNodes * self.shape.class1ratio) else 2
                vpn = self.shape.vpn1 if (nodeClass == 1) else self.shape.vpn2
                for v in range(vpn):
                    vs.append(initValidator(self.shape.nbRows, self.shape.custodyRows, self.shape.nbCols, self.shape.custodyCols))
                val = Node(i, int(not i!=0), amImalicious_value, self.logger, self.shape, self.config, vs)
            if i == self.proposerID:
                val.initBlock()
            else:
                val.logIDs()
            self.validators.append(val)

        assignedRows.sort()
        assignedCols.sort()
        self.logger.debug("Rows assigned: %s" % str(assignedRows), extra=self.format)
        self.logger.debug("Columns assigned: %s" % str(assignedCols), extra=self.format)
        self.logger.debug("Validators initialized.", extra=self.format)

    def initNetwork(self):
        """It initializes the simulated network."""
        rowChannels = [[] for i in range(self.shape.nbRows)]
        columnChannels = [[] for i in range(self.shape.nbCols)]
        for v in self.validators:
            if not (self.proposerPublishOnly and v.amIproposer):
                for id in v.rowIDs:
                    rowChannels[id].append(v)
                for id in v.columnIDs:
                    columnChannels[id].append(v)

        # Check rows/columns distribution
        for r in rowChannels:
            self.distR.append(len(r))
        for c in columnChannels:
            self.distC.append(len(c))
        self.logger.debug("Number of validators per row; Min: %d, Max: %d" % (min(self.distR), max(self.distR)), extra=self.format)
        self.logger.debug("Number of validators per column; Min: %d, Max: %d" % (min(self.distC), max(self.distC)), extra=self.format)

        for id in range(self.shape.nbRows):

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
                val1.rowNeighbors[id].update({val2.ID : Neighbor(val2, 0, self.shape.nbCols)})
                val2.rowNeighbors[id].update({val1.ID : Neighbor(val1, 0, self.shape.nbCols)})

        for id in range(self.shape.nbCols):

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
                val1.columnNeighbors[id].update({val2.ID : Neighbor(val2, 1, self.shape.nbRows)})
                val2.columnNeighbors[id].update({val1.ID : Neighbor(val1, 1, self.shape.nbRows)})

        for v in self.validators:
            if (self.proposerPublishOnly and v.amIproposer):
                for id in v.rowIDs:
                    count = min(self.proposerPublishToR, len(rowChannels[id]))
                    publishTo = random.sample(rowChannels[id], count)
                    for vi in publishTo:
                        v.rowNeighbors[id].update({vi.ID : Neighbor(vi, 0, self.shape.nbCols)})
                for id in v.columnIDs:
                    count = min(self.proposerPublishToC, len(columnChannels[id]))
                    publishTo = random.sample(columnChannels[id], count)
                    for vi in publishTo:
                        v.columnNeighbors[id].update({vi.ID : Neighbor(vi, 1, self.shape.nbRows)})

        if self.logger.isEnabledFor(logging.DEBUG):
            for i in range(0, self.shape.numberNodes):
                self.logger.debug("Val %d : rowN %s", i, self.validators[i].rowNeighbors, extra=self.format)
                self.logger.debug("Val %d : colN %s", i, self.validators[i].columnNeighbors, extra=self.format)

    def initLogger(self):
        """It initializes the logger."""
        logging.TRACE = 5
        logging.addLevelName(logging.TRACE, 'TRACE')
        logging.Logger.trace = partialmethod(logging.Logger.log, logging.TRACE)
        logging.trace = partial(logging.log, logging.TRACE)

        logger = logging.getLogger("DAS")
        if len(logger.handlers) == 0:
            logger.setLevel(self.logLevel)
            ch = logging.StreamHandler()
            ch.setLevel(self.logLevel)
            ch.setFormatter(CustomFormatter())
            logger.addHandler(ch)
        self.logger = logger

    def printDiagnostics(self):
        """Print all required diagnostics to check when a block does not become available"""
        for val in self.validators:
            (a, e) = val.checkStatus()
            if e-a > 0 and val.ID != 0:
                self.logger.warning("Node %d is missing %d samples" % (val.ID, e-a), extra=self.format)
                for r in val.rowIDs:
                    row = val.getRow(r)
                    if row.count() < len(row):
                        self.logger.debug("Row %d: %s" % (r, str(row)), extra=self.format)
                        neiR = val.rowNeighbors[r]
                        for nr in neiR:
                            self.logger.debug("Row %d, Neighbor %d sent: %s" % (r, val.rowNeighbors[r][nr].node.ID, val.rowNeighbors[r][nr].received), extra=self.format)
                            self.logger.debug("Row %d, Neighbor %d has: %s" % (r, val.rowNeighbors[r][nr].node.ID, self.validators[val.rowNeighbors[r][nr].node.ID].getRow(r)), extra=self.format)
                for c in val.columnIDs:
                    col = val.getColumn(c)
                    if col.count() < len(col):
                        self.logger.debug("Column %d: %s" % (c, str(col)), extra=self.format)
                        neiC = val.columnNeighbors[c]
                        for nc in neiC:
                            self.logger.debug("Column %d, Neighbor %d sent: %s" % (c, val.columnNeighbors[c][nc].node.ID, val.columnNeighbors[c][nc].received), extra=self.format)
                            self.logger.debug("Column %d, Neighbor %d has: %s" % (c, val.columnNeighbors[c][nc].node.ID, self.validators[val.columnNeighbors[c][nc].node.ID].getColumn(c)), extra=self.format)

    def run(self):
        """It runs the main simulation until the block is available or it gets stucked."""
        self.glob.checkRowsColumns(self.validators)
        for i in range(0,self.shape.numberNodes):
            if i == self.proposerID:
                # self.validators[i].initBlock()
                self.logger.warning("I am a block proposer.", extra=self.format)
            else:
                self.validators[i].logIDs()
        arrived, expected, ready, validatedall, validated = self.glob.checkStatus(self.validators)
        missingSamples = expected - arrived
        missingVector = []
        progressVector = []
        trafficStatsVector = []
        malicious_nodes_not_added_count = 0
        steps = 0
        while(True):
            missingVector.append(missingSamples)
            self.logger.debug("Expected Samples: %d" % expected, extra=self.format)
            self.logger.debug("Missing Samples: %d" % missingSamples, extra=self.format)
            oldMissingSamples = missingSamples

            self.logger.debug("PHASE SEND %d" % steps, extra=self.format)
            for i in range(0,self.shape.numberNodes):
                if not self.validators[i].amImalicious:
                    self.validators[i].send()
            if steps % self.config.heartbeat == 0 and self.config.gossip:
                self.logger.debug("PHASE GOSSIP %d" % steps, extra=self.format)
                for i in range(1,self.shape.numberNodes):
                    if not self.validators[i].amImalicious:
                        self.validators[i].gossip(self)
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
            trafficStats = self.glob.getTrafficStats(self.validators)
            self.logger.debug("step %d: %s" %
                (steps, trafficStats), extra=self.format)
            for i in range(0,self.shape.numberNodes):
                self.validators[i].updateStats()
            trafficStatsVector.append(trafficStats)

            missingSamples, sampleProgress, nodeProgress, validatorAllProgress, validatorProgress = self.glob.getProgress(self.validators)
            self.logger.info("step %d, arrived %0.02f %%, ready %0.02f %%, validatedall %0.02f %%, , validated %0.02f %%"
                              % (steps, sampleProgress*100, nodeProgress*100, validatorAllProgress*100, validatorProgress*100), extra=self.format)

            cnS = "samples received"
            cnN = "nodes ready"
            cnV = "validators ready"
            cnT0 = "TX builder mean"
            cnT1 = "TX class1 mean"
            cnT2 = "TX class2 mean"
            cnR1 = "RX class1 mean"
            cnR2 = "RX class2 mean"
            cnD1 = "Dup class1 mean"
            cnD2 = "Dup class2 mean"

            # if custody is based on the requirements of underlying individual
            # validators, we can get detailed data on how many validated.
            # Otherwise, we can only use the weighted average.
            if self.config.validatorBasedCustody:
              cnVv = validatorProgress
            else:
              cnVv = validatorAllProgress

            progressVector.append({
                cnS:sampleProgress,
                cnN:nodeProgress,
                cnV:cnVv,
                cnT0: trafficStats[0]["Tx"]["mean"],
                cnT1: trafficStats[1]["Tx"]["mean"],
                cnT2: trafficStats[2]["Tx"]["mean"],
                cnR1: trafficStats[1]["Rx"]["mean"],
                cnR2: trafficStats[2]["Rx"]["mean"],
                cnD1: trafficStats[1]["RxDup"]["mean"],
                cnD2: trafficStats[2]["RxDup"]["mean"],
                })

            if missingSamples == oldMissingSamples:
                if len(missingVector) > self.config.steps4StopCondition:
                    if missingSamples == missingVector[-self.config.steps4StopCondition]:
                        self.logger.debug("The block cannot be recovered, failure rate %d!" % self.shape.failureRate, extra=self.format)
                        if self.config.diagnostics:
                            self.printDiagnostics()
                        break
                missingVector.append(missingSamples)
            elif missingSamples == 0:
                self.logger.debug("The entire block is available at step %d, with failure rate %d !" % (steps, self.shape.failureRate), extra=self.format)
                missingVector.append(missingSamples)
                break
            steps += 1

        for i in range(0,self.shape.numberNodes):
            if not self.validators[i].amIaddedToQueue :
                malicious_nodes_not_added_count += 1

        for i in range(0,self.shape.numberNodes):
            column_ids = []
            row_ids = []
            for rID in self.validators[i].rowIDs:
                row_ids.append(rID)
            for cID in self.validators[i].columnIDs:
                column_ids.append(cID)

            self.logger.debug("List of columnIDs for %d node: %s", i, column_ids, extra=self.format)
            self.logger.debug("List of rowIDs for %d node: %s", i, row_ids, extra=self.format)

        self.logger.debug("Number of malicious nodes not added to the send queue: %d" % malicious_nodes_not_added_count, extra=self.format)
        malicious_nodes_not_added_percentage = (malicious_nodes_not_added_count * 100)/(self.shape.numberNodes)
        self.logger.debug("Percentage of malicious nodes not added to the send queue: %d" % malicious_nodes_not_added_percentage, extra=self.format)

        progress = pd.DataFrame(progressVector)
        if self.config.saveRCdist:
            self.result.addMetric("rowDist", self.distR)
            self.result.addMetric("columnDist", self.distC)
        if self.config.saveProgress:
            self.result.addMetric("progress", progress.to_dict(orient='list'))
        self.result.populate(self.shape, self.config, missingVector)
        self.result.copyValidators(self.validators)
        return self.result
