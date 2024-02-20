#!/bin/python3

import numpy as np
from DAS.block import *

class Observer:
    """This class gathers global data from the simulation, like an 'all-seen god'."""

    def __init__(self, logger, config):
        """It initializes the observer with a logger and given configuration."""
        self.config = config
        self.format = {"entity": "Observer"}
        self.logger = logger
        self.block = [0] * self.config.blockSizeR * self.config.blockSizeC
        self.rows = [0] * self.config.blockSizeC
        self.columns = [0] * self.config.blockSizeR
        self.broadcasted = Block(self.config.blockSizeR, self.config.blockSizeRK,
                                self.config.blockSizeC,  self.config.blockSizeCK)


    def checkRowsColumns(self, validators):
        """It checks how many validators have been assigned to each row and column."""
        for val in validators:
            if val.amIproposer == 0:
                for r in val.rowIDs:
                    self.rows[r] += 1
                for c in val.columnIDs:
                    self.columns[c] += 1

        for i in range(self.config.blockSizeC):
            self.logger.debug("Row %d have %d validators assigned." % (i, self.rows[i]), extra=self.format)
            if self.rows[i] == 0:
                self.logger.warning("There is a row that has not been assigned", extra=self.format)
        for i in range(self.config.blockSizeR):
            self.logger.debug("Column %d have %d validators assigned." % (i, self.columns[i]), extra=self.format)
            if self.columns[i] == 0:
                self.logger.warning("There is a column that has not been assigned", extra=self.format)

    def checkBroadcasted(self):
        """It checks how many broadcasted samples are still missing in the network."""
        zeros = 0
        for i in range(self.blockSizeR * self.blockSizeC):
            if self.broadcasted.data[i] == 0:
                zeros += 1
        if zeros > 0:
            self.logger.debug("There are %d missing samples in the network" % zeros, extra=self.format)
        return zeros

    def checkStatus(self, validators):
        """It checks the status of how many expected and arrived samples globally."""
        arrived = 0
        expected = 0
        ready = 0
        validatedall = 0
        validated = 0
        for val in validators:
            if val.amIproposer == 0:
                (a, e, v) = val.checkStatus()
                arrived += a
                expected += e
                if a == e:
                    ready += 1
                    validatedall += val.vpn
                validated += v
        return (arrived, expected, ready, validatedall, validated)

    def getProgress(self, validators):
            """Calculate current simulation progress with different metrics.

            Returns:
            - missingSamples: overall number of sample instances missing in nodes.
            Sample are counted on both rows and columns, so intersections of interest are counted twice.
            - sampleProgress: previous expressed as progress ratio
            - nodeProgress: ratio of nodes having all segments interested in
            - validatorProgress: same as above, but vpn weighted average. I.e. it counts per validator,
            but counts a validator only if its support node's all validators see all interesting segments
            TODO: add real per validator progress counter
            """
            arrived, expected, ready, validatedall, validated = self.checkStatus(validators)
            missingSamples = expected - arrived
            sampleProgress = arrived / expected
            nodeProgress = ready / (len(validators)-1)
            validatorCnt = sum([v.vpn for v in validators[1:]])
            validatorAllProgress = validatedall / validatorCnt
            validatorProgress = validated / validatorCnt

            return missingSamples, sampleProgress, nodeProgress, validatorAllProgress, validatorProgress

    def getTrafficStats(self, validators):
            """Summary statistics of traffic measurements in a timestep."""
            def maxOrNan(l):
                return np.max(l) if l else np.NaN
            def meanOrNan(l):
                return np.mean(l) if l else np.NaN

            trafficStats = {}
            for cl in range(0,3):
                Tx = [v.statsTxInSlot for v in validators if v.nodeClass == cl]
                Rx = [v.statsRxInSlot for v in validators if v.nodeClass == cl]
                RxDup = [v.statsRxDupInSlot for v in validators if v.nodeClass == cl]
                trafficStats[cl] = {
                    "Tx": {"mean": meanOrNan(Tx), "max": maxOrNan(Tx)},
                    "Rx": {"mean": meanOrNan(Rx), "max": maxOrNan(Rx)},
                    "RxDup": {"mean": meanOrNan(RxDup), "max": maxOrNan(RxDup)},
                    }

            return trafficStats
