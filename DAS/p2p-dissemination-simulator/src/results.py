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

    def copyNodes(self, nodes):
        """Copy information from simulator.validators to result."""
        pass
           
    def populate(self, shape, config, missingVector):
        """It populates part of the result data inside a vector."""
        self.shape = shape
        self.missingVector = missingVector
        v = self.metrics["progress"]["nodes ready"]
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
