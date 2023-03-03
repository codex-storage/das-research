#!/bin/python3

import logging
import sys
import random
from bitarray.util import zeros
class CustomFormatter():
    """This class defines the terminal output formatting."""

    def __init__(self):
        """Initializes 5 different formats for logging with different colors."""
        self.blue = "\x1b[34;20m"
        self.grey = "\x1b[38;20m"
        self.yellow = "\x1b[33;20m"
        self.red = "\x1b[31;20m"
        self.bold_red = "\x1b[31;1m"
        self.reset = "\x1b[0m"
        self.reformat = "%(levelname)s : %(entity)s : %(message)s"
        self.FORMATS = {
            logging.DEBUG: self.grey + self.reformat + self.reset,
            logging.INFO: self.blue + self.reformat + self.reset,
            logging.WARNING: self.yellow + self.reformat + self.reset,
            logging.ERROR: self.red + self.reformat + self.reset,
            logging.CRITICAL: self.bold_red + self.reformat + self.reset
        }

    def format(self, record):
        """Returns the formatter with the format corresponding to record."""
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

def shuffled(lis, shuffle=True):
    """Generator yielding list in shuffled order."""
    # based on https://stackoverflow.com/a/60342323
    if shuffle:
        for index in random.sample(range(len(lis)), len(lis)):
            yield lis[index]
    else:
        for v in lis:
            yield v
def shuffledDict(d, shuffle=True):
    """Generator yielding dictionary in shuffled order.

        Shuffle, except if not (optional parameter useful for experiment setup).
    """
    if shuffle:
        lis = list(d.items())
        for index in random.sample(range(len(d)), len(d)):
            yield lis[index]
    else:
        for kv in d.items():
            yield kv

def sampleLine(line, limit):
    """Sample up to 'limit' bits from a bitarray.

        Since this is quite expensive, we use a number of heuristics to get it fast.
    """
    if limit == sys.maxsize :
        return line
    else:
        w = line.count(1)
        if limit >= w :
            return line
        else:
            l = len(line)
            r = zeros(l)
            if w < l/10 or limit > l/2 :
                indices = [ i for i in range(l) if line[i] ]
                sample = random.sample(indices, limit)
                for i in sample:
                    r[i] = 1
                return r
            else:
                while limit:
                    i = random.randrange(0, l)
                    if line[i] and not r[i]:
                        r[i] = 1
                        limit -= 1
                return r
