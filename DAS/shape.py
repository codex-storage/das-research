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




