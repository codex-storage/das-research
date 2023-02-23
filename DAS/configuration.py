#!/bin/python3

import configparser, logging, sys

class Configuration:
    """This class stores all the configuration parameters for the given run."""

    def __init__(self, fileName):
        """It initializes the configuration based on the given configuration."""

        config = configparser.RawConfigParser()
        config.read(fileName)

        try:
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
        except:
            sys.exit("Configuration Error: It seems some of the [Simulation Space] parameters are missing. Cannot continue :( ")



        try:
            self.numberRuns = int(config.get("Advanced", "numberRuns"))
            self.deterministic = config.get("Advanced", "deterministic")
            self.dumpXML = config.get("Advanced", "dumpXML")
            self.logLevel = config.get("Advanced", "logLevel")
            self.visualization = config.get("Advanced", "visualization")
        except:
            sys.exit("Configuration Error: It seems some of the [Advanced] parameters are missing. Cannot continue :( ")
        self.test()

    def test(self):

        print("Testing configuration...")
        if self.logLevel == "INFO":
            self.logLevel = logging.INFO
        elif self.logLevel == "DEBUG":
            self.logLevel = logging.DEBUG
        else:
            self.logLevel = logging.INFO

        if self.nvStart >= self.nvStop:
            sys.exit("Configuration Error: numberValidatorStart has to be smaller than numberValidatorStop")

        if self.failureRateStart >= self.failureRateStop:
            sys.exit("Configuration Error: failureRateStart has to be smaller than failureRateStop")

        if self.blockSizeStart >= self.blockSizeStop:
            sys.exit("Configuration Error: blockSizeStart has to be smaller than blockSizeStop")

        if self.netDegreeStart >= self.netDegreeStop:
            sys.exit("Configuration Error: netDegreeStart has to be smaller than netDegreeStop")

        if self.chiStart >= self.chiStop:
            sys.exit("Configuration Error: chiStart has to be smaller than chiStop")


        if self.nvStart < self.blockSizeStop:
            sys.exit("Configuration Error: numberValidatorStart hast to be larger than blockSizeStop.")

        if self.chiStart < 2:
            sys.exit("Configuration Error: Chi has to be greater than 1.")

        if self.chiStop > self.blockSizeStart:
            sys.exit("Configuration Error: Chi (%d) has to be smaller or equal to block the size (%d)" % (self.chiStop, self.blockSizeStart))



