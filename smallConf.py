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

# How many copies are sent out by the block producer
# Note, previously this was set to match netDegree
proposerPublishToR = "shape.netDegree"
proposerPublishToC = "shape.netDegree"

# number of rows and columns a validator is interested in
chis = range(2, 3, 2)

# ratio of class1 nodes (see below for parameters per class)
class1ratios = [0.8]

# Number of validators per beacon node
validatorsPerNode1 = [1]
validatorsPerNode2 = [500]

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

# configure Node options
repairOnTheFly = True
sendLineUntilR = "shape.blockSizeRK" # stop sending on a p2p link if at least this amount of samples passed
sendLineUntilC = lambda shape : shape.blockSizeCK # stop sending on a p2p link if at least this amount of samples passed
perNeighborQueue = True # queue incoming messages to outgoing connections on arrival (as typical GossipSub impl)
shuffleQueues = True # shuffle the order of picking from active queues of a sender node
perNodeQueue = "self.amIproposer" # keep a global queue of incoming messages for later sequential dispatch
shuffleLines = True # shuffle the order of rows/columns in each iteration while trying to send
shuffleNeighbors = True # shuffle the order of neighbors when sending the same segment to each neighbor
dumbRandomScheduler = False # dumb random scheduler
segmentShuffleScheduler = False # send each segment that's worth sending once in shuffled order, then repeat
segmentShuffleSchedulerPersist = True # Persist scheduler state between timesteps
queueAllOnInit = True # queue up everything in the block producer, without shuffling, at the very beginning
forwardOnReceive = False # forward segments as soon as received
forwardOnRepair = True # forward all segments when full line available (repaired segments are always forwarded)

def nextShape():
    for run, fm, fr, class1ratio, chi, vpn1, vpn2, blockSize, nn, netDegree, bwUplinkProd, bwUplink1, bwUplink2 in itertools.product(
        runs, failureModels, failureRates, class1ratios, chis, validatorsPerNode1, validatorsPerNode2, blockSizes, numberNodes, netDegrees, bwUplinksProd, bwUplinks1, bwUplinks2):
        # Network Degree has to be an even number
        if netDegree % 2 == 0:
            blockSizeR = blockSizeC = blockSize
            blockSizeRK = blockSizeCK = blockSize // 2
            chiR = chiC = chi
            shape = Shape(blockSizeR, blockSizeRK, blockSizeC, blockSizeCK, nn, fm, fr, class1ratio, chiR, chiC, vpn1, vpn2, netDegree, bwUplinkProd, bwUplink1, bwUplink2, run)
            yield shape

def evalConf(self, param, shape = None):
    '''Allow lazy evaluation of params in various forms

    Examples:
      sendLineUntilR = "shape.blockSizeRK"
      sendLineUntilC = lambda shape : shape.blockSizeCK
      perNodeQueue = "self.amIproposer"
    '''
    if callable(param):
        return param(shape)
    elif isinstance(param, str):
        return eval(param)
    else:
        return param
