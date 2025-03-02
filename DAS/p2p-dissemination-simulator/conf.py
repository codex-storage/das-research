"""Example configuration file

To use this example, run:
   python3 study.py conf.py
"""

import itertools
from src.shape import Shape

# number of parallel workers. -1: all cores; 1: sequential
numJobs = -1

# Per-topic mesh neighborhood size
netDegrees = [8]

# Number of peers for sampling
numPeers = [[50, 150]]

valCustody = [2]
minCustody = [2]

# Disseminamtion method
blockProducerDissemination = True
verticalDissemination = False

# Set uplink bandwidth in megabits/second
bwUplinksProd = [500]
bwUplinks = [500]

# Step duration in miliseconds (Classic RTT is about 100ms)
stepDuration = 50

# Segment size in bytes (with proof)
segmentSize = 560

# If your run is deterministic you can decide the random seed. This is ignore otherwise.
randomSeed = "DAS"

# Number of steps without progress to stop simulation
steps4StopCondition = 7

# Number of validators ready to asume block is available
successCondition = 0.9

cols = [512]
rows = [512]
colsK = [256]
rowsK = [256]

def nextShape():
    params = {
        "cols": cols,
        "colsK": colsK,
        "rows": rows,
        "rowsK": rowsK,
        "valCustody": valCustody,
        "minCustody": minCustody,
        "netDegrees": netDegrees,
        "numPeers": numPeers,
        "bwUplinksProd": bwUplinksProd,
        "bwUplinks": bwUplinks
    }
    
    for key, value in params.items():
        if not value:
            print("The parameter '{key}' is empty. Please assign a value and start the simulation.")
            exit(1)

    for (
        nbCols, nbColsK, nbRows, nbRowsK, valCust, minCust, 
        netDegree, numPeersList, bwUplinkProd, bwUplink
    ) in itertools.product(
        cols, colsK, rows, rowsK,  
        valCustody, minCustody, 
        netDegrees, numPeers, bwUplinksProd, bwUplinks
    ):
        numPeersMin, numPeersMax = numPeersList

        # Ensure netDegree is even
        if netDegree % 2 == 0:
            shape = Shape(
                nbCols, nbColsK, nbRows, nbRowsK, valCust, minCust, 
                netDegree, numPeersMin, numPeersMax, bwUplinkProd, bwUplink
            )
            yield shape
