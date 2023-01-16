#!/bin/python3

class Configuration:

    deterministic = 0
    blockSize = 0
    numberValidators = 0
    failureRate = 0
    failureRateStart = 0
    failureRateStop = 0
    failureRateStep = 0
    chio = 0
    chiStart = 0
    chiStop = 0
    chiStep = 0
    run =0
    runStart = 0
    runStop = 0
    runStep = 0

    def __init__(self, deterministic, blockSize, numberValidators,\
                 failureRateStart, failureRateStop, failureRateStep,\
                 chiStart, chiStop, chiStep,\
                 runStart, runStop, runStep):

        if numberValidators < (blockSize*4):
            print("ERROR: The number of validators cannot be lower than the block size * 4")
            exit(1)
        if chiStart < 1:
            print("Chi has to be greater than 0")
            exit(1)
        if chiStop > blockSize:
            print("Chi has to be smaller than %d" % blockSize)
            exit(1)

        self.deterministic = deterministic
        self.blockSize = blockSize
        self.numberValidators = numberValidators
        self.failureRateStart = failureRateStart
        self.failureRateStop = failureRateStop
        self.failureRateStep = failureRateStep
        self.failureRate = failureRateStart
        self.chiStart = chiStart
        self.chiStop = chiStop
        self.chiStep = chiStep
        self.chi = chiStart
        self.runStart = runStart
        self.runStop = runStop
        self.runStep = runStep
        self.run = runStart
