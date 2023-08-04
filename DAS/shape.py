#!/bin/python3

class Shape:
    """This class represents a set of parameters for a specific simulation."""

    def __init__(self, blockSize, numberNodes, failureModel, failureRate, class1ratio, chi, vpn1, vpn2, netDegree, bwUplinkProd, bwUplink1, bwUplink2, k, alpha, run):
        """Initializes the shape with the parameters passed in argument."""
        # block-segment related parameters
        self.run = run
        self.numberNodes = numberNodes
        self.blockSize = blockSize
        self.failureModel = failureModel
        self.failureRate = failureRate
        self.netDegree = netDegree
        self.class1ratio = class1ratio
        self.chi = chi
        self.vpn1 = vpn1
        self.vpn2 = vpn2
        self.bwUplinkProd = bwUplinkProd
        self.bwUplink1 = bwUplink1
        self.bwUplink2 = bwUplink2
        self.randomSeed = ""
        # DHT related parameters
        self.k = k
        self.alpha = alpha

    def __repr__(self):
        """Returns a printable representation of the shape"""
        shastr = ""
        shastr += "bs-"+str(self.blockSize)
        shastr += "-nn-"+str(self.numberNodes)
        shastr += "-fm-"+str(self.failureModel)
        shastr += "-fr-"+str(self.failureRate)
        shastr += "-c1r-"+str(self.class1ratio)
        shastr += "-chi-"+str(self.chi)
        shastr += "-vpn1-"+str(self.vpn1)
        shastr += "-vpn2-"+str(self.vpn2)
        shastr += "-bwupprod-"+str(self.bwUplinkProd)
        shastr += "-bwup1-"+str(self.bwUplink1)
        shastr += "-bwup2-"+str(self.bwUplink2)
        shastr += "-nd-"+str(self.netDegree)
        shastr += "-k-"+str(self.k)
        shastr += "-alpha-"+str(self.alpha)
        shastr += "-r-"+str(self.run)
        return shastr

    def setSeed(self, seed):
        """Adds the random seed to the shape"""
        self.randomSeed = seed

