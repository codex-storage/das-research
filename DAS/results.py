#!/bin/python3

import os
import bisect
from xml.dom import minidom
from dicttoxml import dicttoxml

class Result:
    """This class stores and process/store the results of a simulation."""

    def __init__(self, shape, execID):
        """It initializes the instance with a specific shape."""
        self.shape = shape
        self.execID = execID
        self.blockAvailable = -1
        self.tta = -1
        self.missingVector = []
        self.metrics = {}
        self.amImalicious = [0] * shape.numberNodes
        self.msgSentCount = [0] * shape.numberNodes
        self.msgRecvCount = [0] * shape.numberNodes
        self.sampleRecvCount = [0] * shape.numberNodes
        self.restoreRowCount = [0] * shape.numberNodes
        self.restoreColumnCount = [0] * shape.numberNodes
        self.repairedSampleCount = [0] * shape.numberNodes
        
        self.query_times = [[] for _ in range(shape.numberNodes)]
        self.query_total_time = [None] * shape.numberNodes
        self.all_original_retries = [[] for _ in range(shape.numberNodes)]
        self.query_results = [''] * shape.numberNodes
        self.original_retries_sum = [None] * shape.numberNodes

        self.numberNodes = shape.numberNodes

    def copyValidators(self, validators):
        """Copy information from simulator.validators to result."""
        for i in range(0,self.shape.numberNodes):
            self.amImalicious[i] = validators[i].amImalicious
            self.msgSentCount[i] = validators[i].msgSentCount
            self.msgRecvCount[i] = validators[i].msgRecvCount
            self.sampleRecvCount[i] = validators[i].sampleRecvCount
            self.restoreRowCount[i] = validators[i].restoreRowCount
            self.restoreColumnCount[i] = validators[i].restoreColumnCount
            self.repairedSampleCount[i] = validators[i].repairedSampleCount
            if not validators[i].amImalicious or not validators[i].amIproposer:
                self.query_times[i] = validators[i].query_times[:]
                self.query_total_time[i] = validators[i].query_total_time
                self.all_original_retries[i] = validators[i].all_original_retries[:]
                self.query_results[i] = validators[i].query_results
                self.original_retries_sum[i] = validators[i].original_retries_sum
            else:
                self.query_times[i] = None
                self.query_total_time[i] = None
                self.all_original_retries[i] = None
                self.query_results[i] = None
                self.original_retries_sum[i] = None

    def populate(self, shape, config, missingVector):
        """It populates part of the result data inside a vector."""
        self.shape = shape
        self.missingVector = missingVector
        v = self.metrics["progress"]["validators ready"]
        tta = bisect.bisect(v, config.successCondition)
        if v[-1] >= config.successCondition:
            self.blockAvailable = 1
            self.tta = tta * (config.stepDuration)
        else:
            self.blockAvailable = 0
            self.tta = -1

    def addMetric(self, name, metric):
        """Generic function to add a metric to the results."""
        self.metrics[name] = metric

    def dump(self):
        """It dumps the results of the simulation in an XML file."""
        if not os.path.exists("results"):
            os.makedirs("results")
        if not os.path.exists("results/"+self.execID):
            os.makedirs("results/"+self.execID)
        resd1 = self.shape.__dict__
        resd2 = self.__dict__.copy()
        resd2.pop("shape")
        resd1.update(resd2)
        resXml = dicttoxml(resd1)
        xmlstr = minidom.parseString(resXml)
        xmlPretty = xmlstr.toprettyxml()
        filePath = "results/"+self.execID+"/"+str(self.shape)+".xml"
        with open(filePath, "w") as f:
            f.write(xmlPretty)
