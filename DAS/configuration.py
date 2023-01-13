#!/bin/python3

class Configuration:

    blockSize = 0
    failureRateStep = 0
    maxTries = 0
    numberValidators = 0
    chi = 0
    failureRate = 0
    deterministic = 0

    def __init__(self, blockSize, failureRateStep, maxTries, numberValidators, chi, failureRate, deterministic):
        if numberValidators < (blockSize*4):
            print("ERROR: The number of validators cannot be lower than the block size * 4")
            exit(1)
        if chi < 1:
            print("Chi has to be greater than 0")
            exit(1)
        if chi > blockSize:
            print("Chi has to be smaller than %d" % blockSize)
            exit(1)

        self.blockSize = blockSize
        self.failureRateStep = failureRateStep
        self.maxTries = maxTries
        self.numberValidators = numberValidators
        self.chi = chi
        self.failureRate = failureRate
        self.deterministic = deterministic
