#!/bin/python3

class Shape:
    """This class represents a set of parameters for a specific simulation."""

    def __init__(self, blockSize, numberValidators, failureRate, chi, netDegree, run):
        """Initializes the shape with the parameters passed in argument."""
        self.run = run
        self.numberValidators = numberValidators
        self.blockSize = blockSize
        self.failureRate = failureRate
        self.netDegree = netDegree
        self.chi = chi
        self.randomSeed = ""

    def __repr__(self):
        """Returns a printable representation of the shape"""
        shastr = ""
        shastr += "bs-"+str(self.blockSize)
        shastr += "-nbv-"+str(self.numberValidators)
        shastr += "-fr-"+str(self.failureRate)
        shastr += "-chi-"+str(self.chi)
        shastr += "-nd-"+str(self.netDegree)
        shastr += "-r-"+str(self.run)
        return shastr

    def setSeed(self, seed):
        """Adds the random seed to the shape"""
        self.randomSeed = seed

