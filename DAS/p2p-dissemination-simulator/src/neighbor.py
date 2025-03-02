from bitarray.util import zeros
from collections import deque

class Neighbor:
    """This class implements a node neighbor to monitor sent and received data.

    It represents one side of a P2P link in the overlay. Sent and received
    segments are monitored to avoid sending twice or sending back what was
    received from a link.
    """

    def __repr__(self):
        """It returns the amount of sent and received data."""
        return "%d:%d/%d, q:%d" % (self.node.ID, self.sent.count(1), self.received.count(1), len(self.sendQueue))

    def __init__(self, v, dim, blockSize):
        """It initializes the neighbor with the node and sets counters to zero."""
        self.node = v
        self.dim = dim # 0:row 1:col
        self.receiving = zeros(blockSize)
        self.received = zeros(blockSize)
        self.sent = zeros(blockSize)
        self.sendQueue = deque()
