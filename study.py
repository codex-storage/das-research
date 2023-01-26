#! /bin/python3

import time, sys
from DAS import *


def study():
    if len(sys.argv) < 2:
        print("You need to pass a configuration file in parameter")
        exit(1)

    config = Configuration(sys.argv[1])
    sim = Simulator(config)
    sim.initLogger()
    results = []
    simCnt = 0

    sim.logger.info("Starting simulations:", extra=sim.format)
    start = time.time()

    for run in range(config.numberRuns):
        for fr in range(config.failureRateStart, config.failureRateStop+1, config.failureRateStep):
            for chi in range(config.chiStart, config.chiStop+1, config.chiStep):
                for blockSize in range(config.blockSizeStart, config.blockSizeStop+1, config.blockSizeStep):
                    for nv in range(config.nvStart, config.nvStop+1, config.nvStep):
                        for netDegree in range(config.netDegreeStart, config.netDegreeStop+1, config.netDegreeStep):

                            if not config.deterministic:
                                random.seed(datetime.now())

                            shape = Shape(blockSize, nv, fr, chi, netDegree)
                            sim.resetShape(shape)
                            sim.initValidators()
                            sim.initNetwork()
                            result = sim.run()
                            sim.logger.info("Run %d, FR: %d %%, Chi: %d, BlockSize: %d, Nb.Val: %d, netDegree: %d ... Block Available: %d" % (run, fr, chi, blockSize, nv, netDegree, result.blockAvailable), extra=sim.format)
                            results.append(result)
                            simCnt += 1

    end = time.time()
    sim.logger.info("A total of %d simulations ran in %d seconds" % (simCnt, end-start), extra=sim.format)



study()

