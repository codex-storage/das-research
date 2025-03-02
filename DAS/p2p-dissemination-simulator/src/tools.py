import sys
import random
from bitarray.util import zeros

def shuffled(lis, shuffle=True):
    """Generator yielding list in shuffled order."""
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