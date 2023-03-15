#! /bin/python3

import time, sys, random, copy
import importlib
from joblib import Parallel, delayed
from DAS import *

# Parallel execution:
# The code currently uses 'joblib' to execute on multiple cores. For other options such as 'ray', see
# https://stackoverflow.com/questions/9786102/how-do-i-parallelize-a-simple-python-loop
# For fixing logging issues in parallel execution, see
# https://stackoverflow.com/questions/58026381/logging-nested-functions-using-joblib-parallel-and-delayed-calls
# and https://github.com/joblib/joblib/issues/1017

def runOnce(sim, config, shape):
    if config.deterministic:
        shape.setSeed(config.randomSeed+"-"+str(shape))
        random.seed(shape.randomSeed)

    sim.initLogger()
    sim.resetShape(shape)
    sim.initValidators()
    sim.initNetwork()
    result = sim.run()
    sim.logger.info("Shape: %s ... Block Available: %d in %d steps" % (str(sim.shape.__dict__), result.blockAvailable, len(result.missingVector)), extra=sim.format)
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

    shape = Shape(0, 0, 0, 0, 0, 0)
    sim = Simulator(shape, config)
    sim.initLogger()
    results = []

    now = datetime.now()
    execID = now.strftime("%Y-%m-%d_%H-%M-%S_")+str(random.randint(100,999))

    sim.logger.info("Starting simulations:", extra=sim.format)
    start = time.time()
    results = Parallel(config.numJobs)(delayed(runOnce)(sim, config, shape) for shape in config.nextShape())
    end = time.time()
    sim.logger.info("A total of %d simulations ran in %d seconds" % (len(results), end-start), extra=sim.format)

    if config.dumpXML:
        for res in results:
            res.dump(execID)
        sim.logger.info("Results dumped into results/%s/" % (execID), extra=sim.format)

    if config.visualization:
        vis = Visualizer(execID)
        vis.plotHeatmaps()


study()

