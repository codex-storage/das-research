"""Example configuration file

This file illustrates how to define options and simulation parameter ranges.
It also defines the traversal order of the simulation space. As the file
extension suggests, configuration is pure python code, allowing complex
setups. Use at your own risk.

To use this example, run
   python3 study.py config_example

Otherwise copy it and modify as needed. The default traversal order defined
in the nested loop of nextShape() is good for most cases, but customizable
if needed.
"""

import logging
import itertools
import numpy as np
from DAS.shape import Shape

# Dump results into XML files
dumpXML = 1

# save progress and row/column distribution vectors to XML
saveProgress = 1

# plot progress for each run to PNG
plotProgress = 1

# Save row and column distributions
saveRCdist = 1

# Plot all figures
visualization = 1

# Verbosity level
logLevel = logging.INFO

# number of parallel workers. -1: all cores; 1: sequential
# for more details, see joblib.Parallel
numJobs = -1

# distribute rows/columns evenly between validators (True)
# or generate it using local randomness (False)
evenLineDistribution = False

# Number of simulation runs with the same parameters for statistical relevance
runs = range(3)

# Number of validators
numberNodes = range(128, 513, 128)

# select failure model between: "random, sequential, MEP, MEP+1, DEP, DEP+1, MREP, MREP-1"
failureModels = ["random"]

# Percentage of block not released by producer
failureRates = range(40, 81, 20)

# Block size in one dimension in segments. Block is blockSizes * blockSizes segments.
blockSizes = range(64, 113, 128)

# Per-topic mesh neighborhood size
netDegrees = range(8, 9, 2)

# the overall number of row/columns taken into custody by a node is determined by
# a base number (custody) and a class specific multiplier (validatorsPerNode).
# We support two models:
#  - validatorsBasedCustody: each validator has a unique subset of size custody,
#    and custody is the union of these. I.e. VPN is a "probabilistic multiplier"
#  - !validatorsBasedCustody: VPN is interpreted as a simple custody multiplier
validatorBasedCustody = False
custody = [2]

# ratio of class1 nodes (see below for parameters per class)
class1ratios = [0.8]

# Number of validators per beacon node
validatorsPerNode1 = [1]
validatorsPerNode2 = [5]

# Set uplink bandwidth in megabits/second
bwUplinksProd = [200]
bwUplinks1 = [10]
bwUplinks2 = [200]

# Step duration in miliseconds (Classic RTT is about 100ms)
stepDuration = 50

# Segment size in bytes (with proof)
segmentSize = 560

# Set to True if you want your run to be deterministic, False if not
deterministic = True

# If your run is deterministic you can decide the random seed. This is ignore otherwise.
randomSeed = "DAS"

# Number of steps without progress to stop simulation
steps4StopCondition = 7

# Number of validators ready to asume block is available
successCondition = 0.9

# If True, print diagnostics when the block is not available
diagnostics = False

# True to save git diff and git commit
saveGit = False

def nextShape():
    for run, fm, fr, class1ratio, cust, vpn1, vpn2, blockSize, nn, netDegree, bwUplinkProd, bwUplink1, bwUplink2 in itertools.product(
        runs, failureModels, failureRates, class1ratios, custody, validatorsPerNode1, validatorsPerNode2, blockSizes, numberNodes, netDegrees, bwUplinksProd, bwUplinks1, bwUplinks2):
        # Network Degree has to be an even number
        if netDegree % 2 == 0:
            nbCols = nbRows = blockSize
            nbColsK = nbRowsK = blockSize // 2
            custodyRows = custodyCols = cust
            shape = Shape(nbCols, nbColsK, nbRows, nbRowsK, nn, fm, fr, class1ratio, custodyRows, custodyCols, vpn1, vpn2, netDegree, bwUplinkProd, bwUplink1, bwUplink2, run)
            yield shape
