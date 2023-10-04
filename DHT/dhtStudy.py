import gc
import os
import sys
import time
import importlib
import itertools
from dhtRetrievals import SingleDHTretrievalStudy


def study(config):
    studyStartTime = time.time()

    for nn, nr, samples, fastErrR, slowErrR, connDelayR, fastDelayR, slowD, k, a, b, y, steps4stop in itertools.product(
            config.nodeNumber,
            config.nodesRetrieving,
            config.samples,
            config.fastErrorRate,
            config.slowErrorRate,
            config.connectionDelayRange,
            config.fastDelayRange,
            config.slowDelays,
            config.ks,
            config.alphas,
            config.betas,
            config.gammas,
            config.stepsToStops):

        if config.studyType == "retrieval":
            singleStudy = SingleDHTretrievalStudy(
                config.csvsFolder,
                config.imgFolder,
                config.jobs,
                nn,
                nr,
                samples,
                fastErrR,
                slowErrR,
                connDelayR,
                fastDelayR,
                slowD,
                k,
                a,
                b,
                y,
                steps4stop)
        else:
            print(f"study type not recognized: {config.studyType}")
            exit(1)

        # if the study type is correct, run the simulation
        singleStudy.run()

        # clean up memory
        del singleStudy
        _ = gc.collect()
        
    print(f"done with the studies in {time.time() - studyStartTime}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("please provide a configuration file")

    try:
        config = importlib.import_module(sys.argv[1])
    except ModuleNotFoundError as e:
        try:
            config = importlib.import_module(str(sys.argv[1]).replace(".py", ""))
        except ModuleNotFoundError as e:
            print(e)
            print("You need to pass a configuration file in parameter")
            exit(1)

    # Make sure that the output folders exist
    for folder in [config.csvsFolder, config.imgFolder]:
        os.makedirs(folder, exist_ok=True)
    study(config)
