#! /bin/python3

import time, sys, random, copy
import importlib
import subprocess
from joblib import Parallel, delayed
from DAS import *

# Parallel execution:
# The code currently uses 'joblib' to execute on multiple cores. For other options such as 'ray', see
# https://stackoverflow.com/questions/9786102/how-do-i-parallelize-a-simple-python-loop
# For fixing logging issues in parallel execution, see
# https://stackoverflow.com/questions/58026381/logging-nested-functions-using-joblib-parallel-and-delayed-calls
# and https://github.com/joblib/joblib/issues/1017

def initLogger(config):
    """It initializes the logger."""
    logger = logging.getLogger("Study")
    logger.setLevel(config.logLevel)
    ch = logging.StreamHandler()
    ch.setLevel(config.logLevel)
    ch.setFormatter(CustomFormatter())
    logger.addHandler(ch)
    return logger

def runOnce(config, shape, execID):

    if config.deterministic:
        shape.setSeed(config.randomSeed+"-"+str(shape))
        random.seed(shape.randomSeed)

    sim = Simulator(shape, config, execID)
    sim.initLogger()
    sim.initValidators()
    sim.initNetwork()
    result = sim.run()
    sim.logger.info("Shape: %s ... Block Available: %d in %d steps" % (str(sim.shape.__dict__), result.blockAvailable, len(result.missingVector)), extra=sim.format)

    if config.dumpXML:
        result.dump()

    if config.visualization:
        visual = Visualizor(execID, config, [result])
        visual.plotAll()

    return result

def study():
    if len(sys.argv) < 2:
        print("You need to pass a configuration file in parameter")
        exit(1)

    try:
        config = importlib.import_module(sys.argv[1])
    except ModuleNotFoundError as e:
        try:
            config = importlib.import_module(str(sys.argv[1]).replace(".py", ""))
        except ModuleNotFoundError as e:
            print(e)
            print("You need to pass a configuration file in parameter")
            exit(1)

    logger = initLogger(config)
    format = {"entity": "Study"}

    results = []

    now = datetime.now()
    execID = now.strftime("%Y-%m-%d_%H-%M-%S_")+str(random.randint(100,999))

    # save config and code state for reproducibility
    if not os.path.exists("results"):
        os.makedirs("results")
    dir = "results/"+execID
    if not os.path.exists(dir):
        os.makedirs(dir)
    if config.saveGit:
       with open(dir+"/git.diff", 'w') as f:
           subprocess.run(["git", "diff"], stdout=f)
       with open(dir+"/git.describe", 'w') as f:
           subprocess.run(["git", "describe", "--always"], stdout=f)
    subprocess.run(["cp", sys.argv[1], dir+"/"])

    logger.info("Starting simulations:", extra=format)
    start = time.time()
    results = Parallel(config.numJobs)(delayed(runOnce)(config, shape ,execID) for shape in config.nextShape())
    end = time.time()
    logger.info("A total of %d simulations ran in %d seconds" % (len(results), end-start), extra=format)

    if config.visualization:
        vis = Visualizer(execID, config)
        vis.plotHeatmaps()

        visual = Visualizor(execID, config, results)
        visual.plotHeatmaps("nn", "fr")
        visual.plotNWDegVsNodeOnRuntime()

if __name__ == "__main__":
    study()
