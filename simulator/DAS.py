#! /bin/python3

import time
from simulator import *


def study():
    sim = Simulator(0)
    sim.initLogger()
    maxTries = 2
    step = 25
    frRange = []
    resultRange = []
    simCnt = 0
    sim.logger.info("Starting simulations:", extra=sim.format)
    start = time.time()
    for fr in range(0, 100, step):
        if fr % 10 == 0:
            sim.logger.info("Failure rate %d %% ..." % fr, extra=sim.format)
        sim.resetFailureRate(fr)
        result = 0
        for i in range(maxTries):
            sim.initValidators()
            result += sim.run()
            simCnt += 1
        frRange.append(fr)
        resultRange.append(100-result)
    end = time.time()
    sim.logger.info("A total of %d simulations ran in %d seconds" % (simCnt, end-start), extra=sim.format)
    for i in range(len(frRange)):
        sim.logger.info("For failure rate of %d we got %d %% success rate in DAS!" % (frRange[i], resultRange[i]), extra=sim.format)


study()

