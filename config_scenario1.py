"""Example configuration file

This file aims to set parameters to realistic values
"""

import logging
import itertools
import numpy as np
from DAS.shape import Shape

dumpXML = 1
visualization = 1
logLevel = logging.INFO

# number of parallel workers. -1: all cores; 1: sequential
# for more details, see joblib.Parallel
numJobs = -1

# distribute rows/columns evenly between validators (True)
# or generate it using local randomness (False)
evenLineDistribution = False

# Number of simulation runs with the same parameters for statistical relevance
runs = range(1)

# Number of validators
numberNodes = [8000]

# Percentage of block not released by producer
failureRates = [0]

# Block size in one dimension in segments. Block is blockSizes * blockSizes segments.
blockSizes = [512]

# Per-topic mesh neighborhood size
netDegrees = [6]

# number of rows and columns a validator is interested in
chis = [2]

# ratio of class1 nodes (see below for parameters per class)
class1ratios = [0.8]

# number of validators per beacon node
validatorsPerNode1 = [1]
validatorsPerNode2 = [100]

# Set uplink bandwidth. In segments (~560 bytes) per timestep (50ms?)
# 1 Mbps ~= 1e6 / 20 / 8 / 560 ~= 11
bwUplinksProd = [11000]
bwUplinks1 = [110]
bwUplinks2 = [11000]

deterministic = True
# If your run is deterministic you can decide the random seed. This is ignore otherwise.
randomSeed = "DAS"

def nextShape():
    for run, fr, class1ratio, chi, vpn1, vpn2, blockSize, nn, netDegree, bwUplinkProd, bwUplink1, bwUplink2 in itertools.product(
        runs, failureRates, class1ratios, chis, validatorsPerNode1, validatorsPerNode2, blockSizes, numberNodes, netDegrees, bwUplinksProd, bwUplinks1, bwUplinks2):
        # Network Degree has to be an even number
        if netDegree % 2 == 0:
            shape = Shape(blockSize, nn, fr, class1ratio, chi, vpn1, vpn2, netDegree, bwUplinkProd, bwUplink1, bwUplink2, run)
            yield shape
