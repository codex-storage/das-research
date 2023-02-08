#!/bin/python3

import os
from xml.dom import minidom
from dicttoxml import dicttoxml

class Result:


    def __init__(self, shape):
        self.shape = shape
        self.blockAvailable = -1
        self.tta = -1
        self.missingVector = []

    def populate(self, shape, missingVector):
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
