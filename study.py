#! /bin/python3

import time, sys, random, copy
from DAS import *


def study():
    if len(sys.argv) < 2:
        print("You need to pass a configuration file in parameter")
        exit(1)

    config = Configuration(sys.argv[1])
    shape = Shape(0, 0, 0, 0, 0, 0)
    sim = Simulator(shape)
    sim.initLogger()
    results = []
    simCnt = 0

    now = datetime.now()
    execID = now.strftime("%Y-%m-%d_%H-%M-%S_")+str(random.randint(100,999))

    sim.logger.info("Starting simulations:", extra=sim.format)
    start = time.time()

    for run in range(config.numberRuns):
        for nv in range(config.nvStart, config.nvStop+1, config.nvStep):
            for blockSize in range(config.blockSizeStart, config.blockSizeStop+1, config.blockSizeStep):
                for fr in range(config.failureRateStart, config.failureRateStop+1, config.failureRateStep):
                    for netDegree in range(config.netDegreeStart, config.netDegreeStop+1, config.netDegreeStep):
                        for chi in range(config.chiStart, config.chiStop+1, config.chiStep):

                            if not config.deterministic:
                                random.seed(datetime.now())

                            # Network Degree has to be an even number
                            if netDegree % 2 == 0:
                                shape = Shape(blockSize, nv, fr, chi, netDegree, run)
                                sim.resetShape(shape)
                                sim.initValidators()
                                sim.initNetwork()
                                result = sim.run()
                                sim.logger.info("Shape: %s ... Block Available: %d" % (str(sim.shape.__dict__), result.blockAvailable), extra=sim.format)
                                results.append(copy.deepcopy(result))
                                simCnt += 1

    end = time.time()
    sim.logger.info("A total of %d simulations ran in %d seconds" % (simCnt, end-start), extra=sim.format)

    if config.dumpXML:
        for res in results:
            res.dump(execID)
        sim.logger.info("Results dumped into results/%s/" % (execID), extra=sim.format)

    visualization = 1
    if visualization:
        vis = Visualizer(execID)
        vis.plotHeatmaps()


study()

