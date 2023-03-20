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
visualization = 1
logLevel = logging.INFO

# number of parallel workers. -1: all cores; 1: sequential
# for more details, see joblib.Parallel
numJobs = 3

# distribute rows/columns evenly between validators (True)
# or generate it using local randomness (False)
evenLineDistribution = False

# Number of simulation runs with the same parameters for statistical relevance
runs = range(10)

# Number of validators
numberNodes = range(256, 513, 128)

# Percentage of block not released by producer
failureRates = range(10, 91, 40)

# Block size in one dimension in segments. Block is blockSizes * blockSizes segments.
blockSizes = range(32,65,16)

# Per-topic mesh neighborhood size
netDegrees = range(6, 9, 2)

# number of rows and columns a validator is interested in
chis = range(1, 5, 2)

# ratio of class1 nodes (see below for parameters per class)
class1ratios = np.arange(0, 1, .2)

# Number of validators per beacon node
validatorsPerNode1 = [1]
validatorsPerNode2 = [2, 4, 8, 16, 32]

# Set uplink bandwidth. In segments (~560 bytes) per timestep (50ms?)
# 1 Mbps ~= 1e6 / 20 / 8 / 560 ~= 11
bwUplinksProd = [2200]
bwUplinks1 = [110]
bwUplinks2 = [2200]

# Set to True if you want your run to be deterministic, False if not
deterministic = False

# If your run is deterministic you can decide the random seed. This is ignore otherwise.
randomSeed = "DAS"

def nextShape():
    for run, fr, class1ratio, chi, vpn1, vpn2, blockSize, nn, netDegree, bwUplinkProd, bwUplink1, bwUplink2 in itertools.product(
        runs, failureRates, class1ratios, chis, validatorsPerNode1, validatorsPerNode2, blockSizes, numberNodes, netDegrees, bwUplinksProd, bwUplinks1, bwUplinks2):
        # Network Degree has to be an even number
        if netDegree % 2 == 0:
            shape = Shape(blockSize, nn, fr, class1ratio, chi, vpn1, vpn2, netDegree, bwUplinkProd, bwUplink1, bwUplink2, run)
            yield shape
