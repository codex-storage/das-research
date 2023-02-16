#!/bin/python3

import logging

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

