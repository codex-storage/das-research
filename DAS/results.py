#!/bin/python3

import os
from xml.dom import minidom
from dicttoxml import dicttoxml

class Result:
    """This class stores and process/store the results of a simulation."""

    def __init__(self, shape):
        """It initializes the instance with a specific shape."""
        self.shape = shape
        self.blockAvailable = -1
        self.tta = -1
        self.missingVector = []

    def populate(self, shape, missingVector):
        """It populates part of the result data inside a vector."""
        self.shape = shape
        self.missingVector = missingVector
        missingSamples = missingVector[-1]
        if missingSamples == 0:
            self.blockAvailable = 1
            self.tta = len(missingVector)
        else:
            self.blockAvailable = 0
            self.tta = -1

    def dump(self, execID):
        """It dumps the results of the simulation in an XML file."""
        if not os.path.exists("results"):
            os.makedirs("results")
        if not os.path.exists("results/"+execID):
            os.makedirs("results/"+execID)
        resd1 = self.shape.__dict__
        resd2 = self.__dict__.copy()
        resd2.pop("shape")
        resd1.update(resd2)
        resXml = dicttoxml(resd1)
        xmlstr = minidom.parseString(resXml)
        xmlPretty = xmlstr.toprettyxml()
        filePath = "results/"+execID+"/nbv-"+str(self.shape.numberValidators)+\
                "-bs-"+str(self.shape.blockSize)+\
                "-nd-"+str(self.shape.netDegree)+\
                "-fr-"+str(self.shape.failureRate)+\
                "-chi-"+str(self.shape.chi)+\
                "-r-"+str(self.shape.run)+".xml"
        with open(filePath, "w") as f:
            f.write(xmlPretty)
