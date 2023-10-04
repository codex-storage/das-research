# Output Folders
csvsFolder = "csvs/retrieval_test"
imgFolder = "imgs/retrieval_test"

# Simulation
# Define the type of study that we want to perform: "retrieval"
studyType = "retrieval"

# Network
jobs = 8
nodeNumber = [12_000]
nodesRetrieving = [100]
samples = [100]
fastErrorRate = [10]
slowErrorRate = [0]
connectionDelayRange = [range(50, 76, 1)]  # ms
fastDelayRange = [range(50, 101, 1)]  # ms
slowDelays = [None]  # ms
gammas = [0.125]  # ms

# DHT config
ks = [20]
alphas = [3]
betas = [20]
stepsToStops = [3]
