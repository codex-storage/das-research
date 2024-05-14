#! /bin/python3

import time, sys, random, copy
import importlib
import subprocess
from joblib import Parallel, delayed
from DAS import *
import os
import pickle
import uuid

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

    backup_folder = f"results/{execID}/backup"
    if not os.path.exists(backup_folder):
        os.makedirs(backup_folder)
    backup_file = os.path.join(backup_folder, f"simulation_data_{shape}.pkl")
    with open(backup_file, 'ab') as f:
        pickle.dump(shape.__dict__, f)
    
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

    with open(backup_file, 'ab') as f:
        pickle.dump("completed", f)

    return result


def check_simulation_completion(state_file):
    backup_dir = os.path.join(os.path.dirname(state_file), "backup")
    if not os.path.exists(backup_dir):
        return False

    all_completed = True
    incomplete_files = []
    completed_files = []
    completed_shapes = []
    for filename in sorted(os.listdir(backup_dir), reverse=True):
        if not filename.endswith(".pkl"):
            continue
        full_path = os.path.join(backup_dir, filename)
        try:
            with open(full_path, 'rb') as f:
                items = []
                while True:
                    try:
                        item = pickle.load(f)
                        items.append(item)
                    except EOFError:
                        break
                last_item = items[-1]
                if last_item != "completed":
                    all_completed = False
                    incomplete_files.append(full_path)
                else:
                    completed_files.append(full_path)
                    completed_shapes.append(items[0])
        except (OSError, pickle.UnpicklingError) as e:
            print(f"Error loading state from {full_path}: {e}")
            all_completed = False
            break
    return all_completed, incomplete_files, completed_files, completed_shapes


def start_simulation(execID, completed_files, completed_shapes, incomplete_files):
    config = importlib.import_module("smallConf")
    logger = initLogger(config)
    format = {"entity": "Study"}

    results = []
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

    logger.info("Starting simulations:", extra=format)
    start = time.time()
    for shape in config.nextShape():
        comparison_dict = shape.__dict__.copy()
        ignore_keys = ['randomSeed']
        for key in ignore_keys:
            del comparison_dict[key]

        if any(all(comparison_dict[key] == completed_shape[key] for key in comparison_dict.keys() if key not in ignore_keys) for completed_shape in completed_shapes):
            logger.info("Skipping simulation for shape (already completed): %s"  % (str(shape.__dict__)), extra=format)
        else:
            results.append(delayed(runOnce)(config, shape, execID))

    results = Parallel(config.numJobs)(results)
    end = time.time()
    logger.info("A total of %d simulations ran in %d seconds" % (len(results), end-start), extra=format)

    if config.visualization:
        vis = Visualizer(execID, config)
        vis.plotHeatmaps()

        visual = Visualizor(execID, config, results)
        visual.plotHeatmaps("nn", "fr")


def study():
    restart_path = None
    for arg in sys.argv[1:]:
        if arg.startswith("--restart="):
            restart_path = arg[len("--restart="):]

    if restart_path:
        execID = restart_path.split("/")[1]
        state_file = f"results/{execID}/backup"
        all_completed, incomplete_files, completed_files, completed_shapes = check_simulation_completion(state_file)

        current_shapes = []
        config = importlib.import_module("smallConf")

        completed_shapes_without_seed = completed_shapes
        for shape in config.nextShape():
            shape_dict = copy.deepcopy(shape.__dict__)
            del shape_dict['randomSeed']
            current_shapes.append(shape_dict)
        for shape in completed_shapes_without_seed:
            if 'randomSeed' in shape:
                del shape['randomSeed']

        completed_set = {frozenset(shape.items()) for shape in completed_shapes_without_seed}
        current_set = {frozenset(shape.items()) for shape in current_shapes}

        if all_completed and completed_set == current_set:
            print("Simulation is already completed.")
            sys.exit(0)
        else:
            print("Restarting simulations.")
            start_simulation(execID, completed_files, completed_shapes, incomplete_files)
            sys.exit(0)
        
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

if __name__ == "__main__":
    study()
