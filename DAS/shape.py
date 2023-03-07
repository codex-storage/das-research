#!/bin/python3

class Shape:
    """This class represents a set of parameters for a specific simulation."""

    def __init__(self, blockSize, numberValidators, failureRate, class1ratio, chi1, chi2, netDegree, bwUplinkProd, bwUplink1, bwUplink2, run):
        """Initializes the shape with the parameters passed in argument."""
        self.run = run
        self.numberValidators = numberValidators
        self.blockSize = blockSize
        self.failureRate = failureRate
        self.netDegree = netDegree
        self.class1ratio = class1ratio
        self.chi1 = chi1
        self.chi2 = chi2
        self.bwUplinkProd = bwUplinkProd
        self.bwUplink1 = bwUplink1
        self.bwUplink2 = bwUplink2
        self.randomSeed = ""

    def __repr__(self):
        """Returns a printable representation of the shape"""
        shastr = ""
        shastr += "bs-"+str(self.blockSize)
        shastr += "-nbv-"+str(self.numberValidators)
        shastr += "-fr-"+str(self.failureRate)
        shastr += "-c1r-"+str(self.class1ratio)
        shastr += "-chi1-"+str(self.chi1)
        shastr += "-chi2-"+str(self.chi2)
        shastr += "-bwupprod-"+str(self.bwUplinkProd)
        shastr += "-bwup1-"+str(self.bwUplink1)
        shastr += "-bwup2-"+str(self.bwUplink2)
        shastr += "-nd-"+str(self.netDegree)
        shastr += "-r-"+str(self.run)
        return shastr

    def setSeed(self, seed):
        """Adds the random seed to the shape"""
        self.randomSeed = seed

