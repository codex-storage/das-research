#!/bin/python3

class Shape:
    """This class represents a set of parameters for a specific simulation."""

    def __init__(self, blockSizeR, blockSizeRK, blockSizeC, blockSizeCK,
                 numberNodes, failureModel, failureRate, class1ratio, chiR, chiC, vpn1, vpn2, netDegree, bwUplinkProd, bwUplink1, bwUplink2, run, sendDqSize, receivedDqSize):
        """Initializes the shape with the parameters passed in argument."""
        self.run = run
        self.numberNodes = numberNodes
        self.blockSizeR = blockSizeR
        self.blockSizeRK = blockSizeRK
        self.blockSizeC = blockSizeC
        self.blockSizeCK = blockSizeCK
        self.failureModel = failureModel
        self.failureRate = failureRate
        self.netDegree = netDegree
        self.class1ratio = class1ratio
        self.chiR = chiR
        self.chiC = chiC
        self.vpn1 = vpn1
        self.vpn2 = vpn2
        self.bwUplinkProd = bwUplinkProd
        self.bwUplink1 = bwUplink1
        self.bwUplink2 = bwUplink2
        self.randomSeed = ""
        self.sendDqSize = sendDqSize
        self.receivedDqSize = receivedDqSize

    def __repr__(self):
        """Returns a printable representation of the shape"""
        shastr = ""
        shastr += "bsrn-"+str(self.blockSizeR)
        shastr += "-bsrk-"+str(self.blockSizeRK)
        shastr += "-bscn-"+str(self.blockSizeC)
        shastr += "-bsck-"+str(self.blockSizeCK)
        shastr += "-nn-"+str(self.numberNodes)
        shastr += "-fm-"+str(self.failureModel)
        shastr += "-fr-"+str(self.failureRate)
        shastr += "-c1r-"+str(self.class1ratio)
        shastr += "-chir-"+str(self.chiR)
        shastr += "-chic-"+str(self.chiC)
        shastr += "-vpn1-"+str(self.vpn1)
        shastr += "-vpn2-"+str(self.vpn2)
        shastr += "-bwupprod-"+str(self.bwUplinkProd)
        shastr += "-bwup1-"+str(self.bwUplink1)
        shastr += "-bwup2-"+str(self.bwUplink2)
        shastr += "-nd-"+str(self.netDegree)
        shastr += "-r-"+str(self.run)
        shastr += "-sdq-"+str(self.sendDqSize)
        shastr += "-rdq-"+str(self.receivedDqSize)
        return shastr

    def setSeed(self, seed):
        """Adds the random seed to the shape"""
        self.randomSeed = seed

