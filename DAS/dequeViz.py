#!/bin/python3

import matplotlib.pyplot as plt
import numpy as np
import os

class DQ:
    def __init__(self, sdq, rdq, tt):
        self.sdq = sdq
        self.rdq = rdq
        self.tt = tt

class DequeViz:
    """This class helps the visualization of time taken for various deque size"""

    def __init__(self, execID, config):
        """Initialize the visualizer module"""
        self.execID = execID
        self.config = config
        os.makedirs("results/"+self.execID+"/dequePlot", exist_ok=True)
        self.data = []
    
    def addData(self, sdq, rdq, tt):
        self.data.append(DQ(sdq, rdq, tt))
        self.data.sort(key=lambda x: (x.sdq, x.rdq))
    
    def plotIt(self):
        t = ""
        for d in self.data:
            t += f"{d.sdq}, {d.rdq}: {d.tt}\n"
        with open("results/"+self.execID+"/dequePlot" + "/pt.txt", "w") as f:
            f.write(t)
            
