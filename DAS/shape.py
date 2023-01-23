#!/bin/python3

class Shape:
    numberValidators = 0
    failureRate = 0
    blockSize = 0
    netDegree = 0
    chi = 0

    def __init__(self, blockSize, numberValidators, failureRate, chi, netDegree):
        self.numberValidators = numberValidators
        self.failureRate = failureRate
        self.blockSize = blockSize
        self.netDegree = netDegree
        self.chi = chi




