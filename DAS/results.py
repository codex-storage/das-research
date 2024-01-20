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

    def copyValidators(self, validators):
        """Copy information from simulator.validators to result."""
        for i in range(0,self.shape.numberNodes):
            self.amImalicious[i] = validators[i].amImalicious
            self.msgSentCount[i] = validators[i].msgSentCount
            self.msgRecvCount[i] = validators[i].msgRecvCount
            self.sampleRecvCount[i] = validators[i].sampleRecvCount

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
