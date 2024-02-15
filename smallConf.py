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
evenLineDistribution = True

# Number of simulation runs with the same parameters for statistical relevance
runs = [1]

# Number of validators
numberNodes = [1024]

# select failure model between: "random, sequential, MEP, MEP+1, DEP, DEP+1, MREP, MREP-1"
failureModels = ["random"]

# Percentage of block not released by producer
failureRates = [0]

# Percentage of nodes that are considered malicious
maliciousNodes = [0]

# Parameter to determine whether to randomly assign malicious nodes or not
# If True, the malicious nodes will be assigned randomly; if False, a predefined pattern may be used
randomizeMaliciousNodes = True

# Per-topic mesh neighborhood size
netDegrees = range(8, 9, 2)

# ratio of class1 nodes (see below for parameters per class)
class1ratios = [0.8]

# Number of validators per beacon node
validatorsPerNode1 = [1]
validatorsPerNode2 = [1]

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

blockSizeR =[128]
blockSizeC = [64]
blockSizeRK = [64]
blockSizeCK = [64]
chiR = [2]
chiC = [2]

def nextShape():
    for blckSizeR, blckSizeRK, blckSizeC, blckSizeCK, run, fm, fr, mn, class1ratio, chR, chC, vpn1, vpn2, nn, netDegree, bwUplinkProd, bwUplink1, bwUplink2 in itertools.product(
        blockSizeR, blockSizeRK, blockSizeC, blockSizeCK, runs, failureModels, failureRates, maliciousNodes, class1ratios,  chiR, chiC, validatorsPerNode1, validatorsPerNode2, numberNodes, netDegrees, bwUplinksProd, bwUplinks1, bwUplinks2):
        # Network Degree has to be an even number
        if netDegree % 2 == 0:
            shape = Shape(blckSizeR, blckSizeRK, blckSizeC, blckSizeCK, nn, fm, fr, mn, class1ratio, chR, chC, vpn1, vpn2, netDegree, bwUplinkProd, bwUplink1, bwUplink2, run)
            yield shape