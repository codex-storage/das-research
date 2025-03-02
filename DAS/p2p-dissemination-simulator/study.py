#! /bin/python3

import datetime
from datetime import datetime
import time, sys, random
import importlib
import subprocess
from joblib import Parallel, delayed
import os

from src.simulator import Simulator
from src.visualizor import Visualizor


def runOnce(config, shape, execID):

    shape.setSeed(config.randomSeed+"-"+str(shape))
    random.seed(shape.randomSeed)
    
    sim = Simulator(shape, config, execID)
    result = sim.run()

    visual = Visualizor(execID, config, [result])
    visual.plotAll()

    return result


def start_simulation(execID, completed_files, completed_shapes, incomplete_files):
    config = importlib.import_module("conf")
    format = {"entity": "Study"}

    results = []
    if not os.path.exists("results"):
        os.makedirs("results")
    dir = "results/"+execID
    if not os.path.exists(dir):
        os.makedirs(dir)

    print("Starting simulations:", extra=format)
    start = time.time()
    for shape in config.nextShape():
        comparison_dict = shape.__dict__.copy()
        ignore_keys = ['randomSeed']
        for key in ignore_keys:
            del comparison_dict[key]

        results.append(delayed(runOnce)(config, shape, execID))

    results = Parallel(config.numJobs)(results)
    end = time.time()
    print("A total of %d simulations ran in %d seconds" % (len(results), end-start), extra=format)


def study():
    if len(sys.argv) < 2:
        print("You need to pass a configuration file in parameter")
        exit(1)

    config = importlib.import_module(sys.argv[1].replace('.py', ''))

    format = {"entity": "Study"}

    results = []

    now = datetime.now()
    execID = now.strftime("%Y-%m-%d_%H-%M-%S_")+str(random.randint(100,999))

    if not os.path.exists("results"):
        os.makedirs("results")
    dir = "results/"+execID
    if not os.path.exists(dir):
        os.makedirs(dir)
    
    subprocess.run(["cp", sys.argv[1], dir+"/"])

    print("Starting simulations:")
    start = time.time()
    results = Parallel(config.numJobs)(delayed(runOnce)(config, shape ,execID) for shape in config.nextShape())
    end = time.time()
    print("A total of %d simulations ran in %d seconds" % (len(results), end-start))

if __name__ == "__main__":
    study()
