#!/bin/python3

import numpy as np
from src.block import *

class Observer:

    def __init__(self, config):
        self.config = config
        self.format = {"entity": "Observer"}
        self.block = [0] * self.config.nbCols * self.config.nbRows
        self.broadcasted = Block(self.config.nbCols, self.config.nbColsK,
                                self.config.nbRows,  self.config.nbRowsK)



    def checkStatus(self, nodes):
        arrived = 0
        expected = 0
        ready = 0
        for node in nodes:
            if node.amIproposer == 0:
                (a, e) = node.checkStatus()
                arrived += a
                expected += e
                if a == e:
                    ready += 1
        return (arrived, expected, ready)

    def getProgress(self, nodes):
            arrived, expected, ready = self.checkStatus(nodes)
            missingSamples = expected - arrived
            sampleProgress = arrived / expected
            nodeProgress = ready / (len(nodes)-1)
            
            return missingSamples, sampleProgress, nodeProgress
    
    def getRowChannelProgress(self, nodes, selectedRowID):
        arrived = 0
        expected = 0
        ready = 0
        count = 0
        for node in nodes:
            if node.amIproposer == 0 and selectedRowID in node.rowIDs:
                line = node.getRow(selectedRowID)
                arrived += line.count(1)
                expected += len(line)
                if line.count(1) == len(line):
                    ready += 1
                count += 1
        rowChannelMissingSamples = expected - arrived
        rowChannelSampleProgress = arrived / expected
        # number of nodes that have the entire row / number of nodes that are expected to have the row
        rowChannelNodeProgress = ready / count
        return rowChannelMissingSamples, rowChannelSampleProgress, rowChannelNodeProgress

