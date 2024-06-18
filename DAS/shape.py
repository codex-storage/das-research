#!/bin/python3

class Shape:
    """This class represents a set of parameters for a specific simulation."""
    def __init__(self, nbCols, nbColsK, nbRows, nbRowsK, 
    numberNodes, failureModel, failureRate, maliciousNodes, custodyRows, custodyCols, minCustodyRows, minCustodyCols, netDegree, bwUplinkProd, run, nodeTypes):
        """Initializes the shape with the parameters passed in argument."""
        self.run = run
        self.numberNodes = numberNodes
        self.nbCols = nbCols
        self.nbColsK = nbColsK
        self.nbRows = nbRows
        self.nbRowsK = nbRowsK
        self.failureModel = failureModel
        self.failureRate = failureRate
        self.maliciousNodes = maliciousNodes
        self.netDegree = netDegree
        self.custodyRows = custodyRows
        self.custodyCols = custodyCols
        self.minCustodyRows = minCustodyRows
        self.minCustodyCols = minCustodyCols
        self.bwUplinkProd = bwUplinkProd
        self.nodeTypes = nodeTypes
        self.nodeClasses = [0] + [_k for _k in nodeTypes["classes"].keys()]
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
        shastr += "-cusr-"+str(self.custodyRows)
        shastr += "-cusc-"+str(self.custodyCols)
        shastr += "-mcusr-"+str(self.minCustodyRows)
        shastr += "-mcusc-"+str(self.minCustodyCols)
        shastr += "-bwupprod-"+str(self.bwUplinkProd)
        shastr += "-nd-"+str(self.netDegree)
        shastr += "-r-"+str(self.run)
        shastr += "-mn-"+str(self.maliciousNodes)
        shastr += "-ntypes-"+str(self.nodeTypes['group'])
        return shastr

    def setSeed(self, seed):
        """Adds the random seed to the shape"""
        self.randomSeed = seed
