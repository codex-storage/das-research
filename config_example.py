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

dumpXML = 1

# save progress vectors to XML
saveProgress = 1
visualization = 1
logLevel = logging.INFO

# number of parallel workers. -1: all cores; 1: sequential
# for more details, see joblib.Parallel
numJobs = -1

# distribute rows/columns evenly between validators (True)
# or generate it using local randomness (False)
evenLineDistribution = True

# Number of simulation runs with the same parameters for statistical relevance
runs = range(2)

# Number of validators
numberNodes = range(256, 513, 128)

# Percentage of block not released by producer
failureRates = range(10, 91, 40)

# Block size in one dimension in segments. Block is blockSizes * blockSizes segments.
blockSizes = range(32,65,16)

# Per-topic mesh neighborhood size
netDegrees = range(6, 9, 2)

# percentage of GossipSub mesh link failures
gsEdgeFailureRate = 0

# number of rows and columns a validator is interested in
chis = range(2, 5, 2)

# ratio of class1 nodes (see below for parameters per class)
class1ratios = [0.8, 0.9]

# Number of validators per beacon node
validatorsPerNode1 = [1]
validatorsPerNode2 = [500]

# Set uplink bandwidth. In segments (~560 bytes) per timestep (50ms?)
# 1 Mbps ~= 1e6 / 20 / 8 / 560 ~= 11
bwUplinksProd = [2200]
bwUplinks1 = [110]
bwUplinks2 = [2200]

# Step duration in miliseconds (Classic RTT is about 100ms)
stepDuration = 50

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

def nextShape():
    for run, fr, class1ratio, chi, vpn1, vpn2, blockSize, nn, netDegree, bwUplinkProd, bwUplink1, bwUplink2 in itertools.product(
        runs, failureRates, class1ratios, chis, validatorsPerNode1, validatorsPerNode2, blockSizes, numberNodes, netDegrees, bwUplinksProd, bwUplinks1, bwUplinks2):
        # Network Degree has to be an even number
        if netDegree % 2 == 0:
            shape = Shape(blockSize, nn, fr, class1ratio, chi, vpn1, vpn2, netDegree, bwUplinkProd, bwUplink1, bwUplink2, run)
            yield shape
