#!/bin/python3

import configparser

class Configuration:

    deterministic = 0

    def __init__(self, fileName):

        config = configparser.RawConfigParser()
        config.read(fileName)

        self.nvStart = int(config.get("Simulation Space", "numberValidatorStart"))
        self.nvStop = int(config.get("Simulation Space", "numberValidatorStop"))
        self.nvStep = int(config.get("Simulation Space", "numberValidatorStep"))

        self.blockSizeStart = int(config.get("Simulation Space", "blockSizeStart"))
        self.blockSizeStop = int(config.get("Simulation Space", "blockSizeStop"))
        self.blockSizeStep = int(config.get("Simulation Space", "blockSizeStep"))

        self.netDegreeStart = int(config.get("Simulation Space", "netDegreeStart"))
        self.netDegreeStop = int(config.get("Simulation Space", "netDegreeStop"))
        self.netDegreeStep = int(config.get("Simulation Space", "netDegreeStep"))

        self.failureRateStart = int(config.get("Simulation Space", "failureRateStart"))
        self.failureRateStop = int(config.get("Simulation Space", "failureRateStop"))
        self.failureRateStep = int(config.get("Simulation Space", "failureRateStep"))

        self.chiStart = int(config.get("Simulation Space", "chiStart"))
        self.chiStop = int(config.get("Simulation Space", "chiStop"))
        self.chiStep = int(config.get("Simulation Space", "chiStep"))

        self.numberRuns = int(config.get("Advanced", "numberRuns"))
        self.deterministic = config.get("Advanced", "deterministic")

        if self.nvStop < (self.blockSizeStart*4):
            print("ERROR: The number of validators cannot be lower than the block size * 4")
            exit(1)
        if self.chiStart < 1:
            print("Chi has to be greater than 0")
            exit(1)
        if self.chiStop > self.blockSizeStart:
            print("Chi (%d) has to be smaller or equal to block the size (%d)" % (self.chiStop, self.blockSizeStart))
            exit(1)



