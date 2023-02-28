# Copyright (C) 2016 Michele Segata <segata@ccs-labs.org>


class Events:
    """
    Defines event types for the simulation
    """

    # start transmission event
    START_TX = 0
    # end transmission event
    END_TX = 1
    # start reception event
    START_RX = 2
    # end reception event
    END_RX = 3
    # packet arrival event
    PACKET_ARRIVAL = 4
    # end of processing after reception or transmission. can start operations
    # again
    END_PROC = 5
    # timeout for RX state avoiding getting stuck into RX indefinitely
    RX_TIMEOUT = 6
