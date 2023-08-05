# -*- coding: utf-8 -*-

""" pyi """

# import sys
import os

# init python std logging
import logging
import logging.config


__author__ = 'Johan Andersson <Grokzen@gmail.com>'
__version__ = (0, 1, 0)
__version_str__ = '.'.join(map(str, __version__))

# Set to True to have revision from Version Control System in version string
__devel__ = True


PACKAGE_NAME = "pyi"


log_level_to_string_map = {
    5: "DEBUG",
    4: "INFO",
    3: "WARNING",
    2: "ERROR",
    1: "CRITICAL",
    0: "WARNING"
}


def init_logging(log_level):
    """
    Init logging settings with default set to INFO
    """
    l = log_level_to_string_map[log_level]

    msg = "%(levelname)s - %(name)s:%(lineno)s - %(message)s" if l in os.environ else "%(levelname)s - %(message)s"

    logging_conf = {
        "version": 1,
        "root": {
            "level": l,
            "handlers": ["console"]
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": l,
                "formatter": "simple",
                "stream": "ext://sys.stdout"
            }
        },
        "formatters": {
            "simple": {
                "format": " {}".format(msg)
            }
        }
    }

    logging.config.dictConfig(logging_conf)
