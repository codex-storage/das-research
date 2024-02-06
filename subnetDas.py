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
runs = [1]

# Number of validators
numberNodes = [1000]

# select failure model between: "random, sequential, MEP, MEP+1, DEP, DEP+1, MREP, MREP-1"
failureModels = ["random"]

# Percentage of block not released by producer
failureRates = [0]

# Block size parameters. 
## columnsN: number of columns (or row size)
## columnsK: original row size, before erasure coding
## BlockSizeC: number of rows (or column size)
## BlockSizeCK: original number of rows, before erasure coding            
columnsK = 1024
columnsN = 2 * columnsK
rowsK = 128
rowsN = rowsK

# Per-topic mesh neighborhood size
netDegrees = [8]

# number of rows and columns a validator is interested in
chiR = 1 # Number of rows observed by validators (not Beacon nodes with validators, but individual validators)
chiC = 16 # Number of columns observed by full nodes

# ratio of class1 nodes (see below for parameters per class)
class1ratios = [.5]

# Number of validators per beacon node
validatorsPerNode1 = [0] # Full nodes, without validators 
validatorsPerNode2 = [500] # Nodes with validators

# Set uplink bandwidth in megabits/second
bwUplinksProd = [200]
bwUplinks1 = [10] # Full nodes
bwUplinks2 = [200] # Nodes with validators

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

# Number of validators ready to assume block is available
successCondition = 0.9

# If True, print diagnostics when the block is not available
diagnostics = False

# True to save git diff and git commit
saveGit = False

def nextShape():
    for run, fm, fr, class1ratio, vpn1, vpn2, nn, netDegree, bwUplinkProd, bwUplink1, bwUplink2 in itertools.product(
        runs, failureModels, failureRates, class1ratios, validatorsPerNode1, validatorsPerNode2, numberNodes, netDegrees, bwUplinksProd, bwUplinks1, bwUplinks2):
        # Network Degree has to be an even number
        if netDegree % 2 == 0:

            shape = Shape(columnsN, columnsK, rowsN, rowsK, nn, fm, fr, class1ratio, chiR, chiC, vpn1, vpn2, netDegree, bwUplinkProd, bwUplink1, bwUplink2, run)
            yield shape
