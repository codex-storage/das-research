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

# Number of simulation runs with the same parameters for statistical relevance
runs = range(3)

# Number of validators
numberNodes = range(128, 513, 128)

# select failure model between: "random, sequential, MEP, MEP+1, DEP, DEP+1, MREP, MREP-1"
failureModels = ["random"]

# Percentage of block not released by producer
failureRates = range(40, 81, 20)

# Percentage of nodes that are considered malicious
maliciousNodes = range(40,41,20)

# Parameter to determine whether to randomly assign malicious nodes or not
# If True, the malicious nodes will be assigned randomly; if False, a predefined pattern may be used
randomizeMaliciousNodes = True

# When set to True, nodes will use the Gossipsub protocol for communication
gossip = True

# Heartbeat interval for gossip messages in simulation steps
heartbeat = 20

# Per-topic mesh neighborhood size
netDegrees = range(8, 9, 2)

# How many copies are sent out by the block producer
# Note, previously this was set to match netDegree
proposerPublishToR = "shape.netDegree"
proposerPublishToC = "shape.netDegree"

# the overall number of row/columns taken into custody by a node is determined by
# a base number (custody) and a class specific multiplier (validatorsPerNode).
# We support two models:
#  - validatorsBasedCustody: each validator has a unique subset of size custody,
#    and custody is the union of these. I.e. VPN is a "probabilistic multiplier"
#  - !validatorsBasedCustody: VPN is interpreted as a simple custody multiplier
validatorBasedCustody = False
custodyRows = range(2, 3, 2)
custodyCols = range(2, 3, 2)

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

# configure Node options
repairOnTheFly = True
sendLineUntilR = "shape.nbColsK" # stop sending on a p2p link if at least this amount of samples passed
sendLineUntilC = lambda shape : shape.nbRowsK # stop sending on a p2p link if at least this amount of samples passed
perNeighborQueue = True # queue incoming messages to outgoing connections on arrival (as typical GossipSub impl)
shuffleQueues = True # shuffle the order of picking from active queues of a sender node
perNodeQueue = False # keep a global queue of incoming messages for later sequential dispatch
shuffleLines = True # shuffle the order of rows/columns in each iteration while trying to send
shuffleNeighbors = True # shuffle the order of neighbors when sending the same segment to each neighbor
dumbRandomScheduler = False # dumb random scheduler
segmentShuffleScheduler = True # send each segment that's worth sending once in shuffled order, then repeat
segmentShuffleSchedulerPersist = True # Persist scheduler state between timesteps
queueAllOnInit = False # queue up everything in the block producer, without shuffling, at the very beginning
forwardOnReceive = True # forward segments as soon as received
forwardWhenLineReceived = False # forward all segments when full line available (repaired segments are always forwarded)

cols = range(64, 113, 128)
rows = range(32, 113, 128)
colsK = range(32, 65, 128)
rowsK = range(32, 65, 128)

def nextShape():
    for nbCols, nbColsK, nbRows, nbRowsK, run, fm, fr, mn, class1ratio, chR, chC, vpn1, vpn2, nn, netDegree, bwUplinkProd, bwUplink1, bwUplink2 in itertools.product(
        cols, colsK, rows, rowsK, runs, failureModels, failureRates, maliciousNodes, class1ratios,  custodyRows, custodyCols, validatorsPerNode1, validatorsPerNode2, numberNodes, netDegrees, bwUplinksProd, bwUplinks1, bwUplinks2):
        # Network Degree has to be an even number
        if netDegree % 2 == 0:
            shape = Shape(nbCols, nbColsK, nbRows, nbRowsK, nn, fm, fr, mn, class1ratio, chR, chC, vpn1, vpn2, netDegree, bwUplinkProd, bwUplink1, bwUplink2, run)
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
