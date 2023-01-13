#! /bin/python3

import time
from DAS import *


def study():
    config = Configuration(64, 20, 10, 256, 8, 0, 0)
    sim = Simulator(config)
    sim.initLogger()
    frRange = []
    resultRange = []
    simCnt = 0
    sim.logger.info("Starting simulations:", extra=sim.format)
    start = time.time()
    for fr in range(0, 100, config.failureRateStep):
        if fr % 10 == 0:
            sim.logger.info("Failure rate %d %% ..." % fr, extra=sim.format)
        sim.resetFailureRate(fr)
        result = 0
        for i in range(config.maxTries):
            sim.initValidators()
            sim.initNetwork()
            result += sim.run()
            simCnt += 1
        frRange.append(fr)
        resultRange.append((config.maxTries-result)*100/config.maxTries)
    end = time.time()
    sim.logger.info("A total of %d simulations ran in %d seconds" % (simCnt, end-start), extra=sim.format)
    for i in range(len(frRange)):
        sim.logger.info("For failure rate of %d we got %d %% success rate in DAS!" % (frRange[i], resultRange[i]), extra=sim.format)


study()

