class Shape:
    """This class represents a set of parameters for a specific simulation."""
    def __init__(self, nbCols, nbColsK, nbRows, nbRowsK, 
    valCust, minCust, netDegree, numPeersMin, numPeersMax, bwUplinkProd, bwUplink):
        """Initializes the shape with the parameters passed in argument."""
        self.nbCols = nbCols
        self.nbColsK = nbColsK
        self.nbRows = nbRows
        self.nbRowsK = nbRowsK
        self.netDegree = netDegree
        self.numPeers = [numPeersMin, numPeersMax]
        self.valCustody = valCust
        self.minCustody = minCust
        self.bwUplinkProd = bwUplinkProd
        self.bwUplink = bwUplink
        self.randomSeed = ""

    def __repr__(self):
        """Returns a printable representation of the shape"""
        shastr = ""
        shastr += "bsrn-"+str(self.nbCols)
        shastr += "-bsrk-"+str(self.nbColsK)
        shastr += "-bscn-"+str(self.nbRows)
        shastr += "-bsck-"+str(self.nbRowsK)
        shastr += "-cus-"+str(self.valCustody)
        shastr += "-mcus-"+str(self.minCustody)
        shastr += "-bwupprod-"+str(self.bwUplinkProd)
        shastr += "-bwup-"+str(self.bwUplink)
        shastr += "-nd-"+str(self.netDegree)
        shastr += "-np-"+str(self.numPeers)
        return shastr

    def setSeed(self, seed):
        """Adds the random seed to the shape"""
        self.randomSeed = seed
