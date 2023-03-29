#!/bin/python3

import os
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

    def populate(self, shape, config, missingVector):
        """It populates part of the result data inside a vector."""
        self.shape = shape
        self.missingVector = missingVector
        missingSamples = missingVector[-1]
        if missingSamples == 0:
            self.blockAvailable = 1
            self.tta = len(missingVector) * (1000/config.stepDuration)
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
