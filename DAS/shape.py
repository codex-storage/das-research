#!/bin/python3

class Shape:
    """This class represents a set of parameters for a specific simulation."""

    def __init__(self, nbCols, nbColsK, nbRows, nbRowsK,
                 numberNodes, failureModel, failureRate, class1ratio, custodyRows, custodyCols, vpn1, vpn2, netDegree, bwUplinkProd, bwUplink1, bwUplink2, run):
        """Initializes the shape with the parameters passed in argument."""
        self.run = run
        self.numberNodes = numberNodes
        self.nbCols = nbCols
        self.nbColsK = nbColsK
        self.nbRows = nbRows
        self.nbRowsK = nbRowsK
        self.failureModel = failureModel
        self.failureRate = failureRate
        self.netDegree = netDegree
        self.class1ratio = class1ratio
        self.custodyRows = custodyRows
        self.custodyCols = custodyCols
        self.vpn1 = vpn1
        self.vpn2 = vpn2
        self.bwUplinkProd = bwUplinkProd
        self.bwUplink1 = bwUplink1
        self.bwUplink2 = bwUplink2
        self.randomSeed = ""

    def __repr__(self):
        """Returns a printable representation of the shape"""
        shastr = ""
        shastr += "bsrn-"+str(self.nbCols)
        shastr += "-bsrk-"+str(self.nbColsK)
        shastr += "-bscn-"+str(self.nbRows)
        shastr += "-bsck-"+str(self.nbRowsK)
        shastr += "-nn-"+str(self.numberNodes)
        shastr += "-fm-"+str(self.failureModel)
        shastr += "-fr-"+str(self.failureRate)
        shastr += "-c1r-"+str(self.class1ratio)
        shastr += "-cusr-"+str(self.custodyRows)
        shastr += "-cusc-"+str(self.custodyCols)
        shastr += "-vpn1-"+str(self.vpn1)
        shastr += "-vpn2-"+str(self.vpn2)
        shastr += "-bwupprod-"+str(self.bwUplinkProd)
        shastr += "-bwup1-"+str(self.bwUplink1)
        shastr += "-bwup2-"+str(self.bwUplink2)
        shastr += "-nd-"+str(self.netDegree)
        shastr += "-r-"+str(self.run)
        return shastr

    def setSeed(self, seed):
        """Adds the random seed to the shape"""
        self.randomSeed = seed

