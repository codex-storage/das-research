#! /bin/python3

import time
from DAS import *


def study():
    config = Configuration(0, 64, 256, 0, 100, 20, 8, 16, 4, 0, 10, 1)
    sim = Simulator(config)
    sim.initLogger()
    frRange = []
    results = []
    resultRange = []
    simCnt = 0
    sim.logger.info("Starting simulations:", extra=sim.format)
    start = time.time()
    for fr in range(config.failureRateStart, config.failureRateStop+1, config.failureRateStep):
        sim.resetFailureRate(fr)
        for chi in range(config.chiStart, config.chiStop+1, config.chiStep):
            sim.resetChi(chi)
            blockAvailable = 0
            for run in range(config.runStart, config.runStop, config.runStep):
                sim.logger.info("FR: %d %%, Chi: %d %%, Run: %d ..." % (fr, chi, run), extra=sim.format)
                sim.initValidators()
                sim.initNetwork()
                result = sim.run()
                blockAvailable += result.blockAvailable
                results.append(result)
                simCnt += 1
        frRange.append(fr)
        resultRange.append((blockAvailable)*100/config.runStop)
    end = time.time()
    sim.logger.info("A total of %d simulations ran in %d seconds" % (simCnt, end-start), extra=sim.format)
    #for i in range(len(frRange)):
    #    sim.logger.info("For failure rate of %d we got %d %% success rate in DAS!" % (frRange[i], resultRange[i]), extra=sim.format)


study()

