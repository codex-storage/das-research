#!/bin/python3


class Result:

    config = []
    missingVector = []
    blockAvailable = -1

    def __init__(self, config):
        self.config = config
        self.blockAvailable = -1
        self.missingVector = []


    def addMissing(self, missingVector):
        self.missingVector = missingVector
