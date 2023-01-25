#!/bin/python3

class Shape:
    run = 0
    numberValidators = 0
    blockSize = 0
    failureRate = 0
    netDegree = 0
    chi = 0

    def __init__(self, blockSize, numberValidators, failureRate, chi, netDegree, run):
        self.run = run
        self.numberValidators = numberValidators
        self.blockSize = blockSize
        self.failureRate = failureRate
        self.netDegree = netDegree
        self.chi = chi




