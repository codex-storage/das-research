#!/bin/python3

from statistics import mean
from DAS.block import *

class Observer:
    """This class gathers global data from the simulation, like an 'all-seen god'."""

    def __init__(self, logger, config):
        """It initializes the observer with a logger and given configuration."""
        self.config = config
        self.format = {"entity": "Observer"}
        self.logger = logger
        self.block = [0] * self.config.blockSize * self.config.blockSize
        self.rows = [0] * self.config.blockSize
        self.columns = [0] * self.config.blockSize
        self.broadcasted = Block(self.config.blockSize)


    def checkRowsColumns(self, validators):
        """It checks how many validators have been assigned to each row and column."""
        for val in validators:
            if val.amIproposer == 0:
                for r in val.rowIDs:
                    self.rows[r] += 1
                for c in val.columnIDs:
                    self.columns[c] += 1

        for i in range(self.config.blockSize):
            self.logger.debug("Row/Column %d have %d and %d validators assigned." % (i, self.rows[i], self.columns[i]), extra=self.format)
            if self.rows[i] == 0 or self.columns[i] == 0:
                self.logger.warning("There is a row/column that has not been assigned", extra=self.format)

    def checkBroadcasted(self):
        """It checks how many broadcasted samples are still missing in the network."""
        zeros = 0
        for i in range(self.blockSize * self.blockSize):
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
        validated = 0
        for val in validators:
            if val.amIproposer == 0:
                (a, e) = val.checkStatus()
                arrived += a
                expected += e
                if a == e:
                    ready += 1
                    validated += val.vpn
        return (arrived, expected, ready, validated)

    def getProgress(self, validators):
            arrived, expected, ready, validated = self.checkStatus(validators)
            missingSamples = expected - arrived
            sampleProgress = arrived / expected
            nodeProgress = ready / (len(validators)-1)
            validatorCnt = sum([v.vpn for v in validators[1:]])
            validatorProgress = validated / validatorCnt

            return missingSamples, sampleProgress, nodeProgress, validatorProgress

    def getTrafficStats(self, validators):
            statsTxInSlot = [v.statsTxInSlot for v in validators]
            statsRxInSlot = [v.statsRxInSlot for v in validators]
            statsRxDupInSlot = [v.statsRxDupInSlot for v in validators]
            TX_prod = statsTxInSlot[0]
            RX_prod = statsRxInSlot[0]
            TX_avg = mean(statsTxInSlot[1:])
            TX_max = max(statsTxInSlot[1:])
            Rx_avg = mean(statsRxInSlot[1:])
            Rx_max = max(statsRxInSlot[1:])
            RxDup_avg = mean(statsRxDupInSlot[1:])
            RxDup_max = max(statsRxDupInSlot[1:])

            return (TX_prod, RX_prod, TX_avg, TX_max, Rx_avg, Rx_max, RxDup_avg, RxDup_max)
