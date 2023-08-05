# -*- coding: utf-8 -*-

""" pyi - cli for pyi """

# python std library
import logging

# 3rd party imports
from docopt import docopt


def parse_cli():
    """
    Parse cli and return the parsed arguments from docopt
    """

    __docopt__ = """
usage: pyi basic <package> ...
       pyi description <package> ...
       pyi downloads <package> ...
       pyi releases <package> ...
       pyi release <version> <package> ...
       pyi raw <package> ...

pyi - cli for pypi json endpoints

optional arguments:
  --version         display the version number and exit
  -h, --help        show this help message and exit
"""

    import pyi

    args = docopt(__docopt__, version=pyi.__version__)

    pyi.init_logging(2)
    log = logging.getLogger(__name__)

    log.debug("Init cli")
    log.debug(args)

    return args


def run(cli_args):
    """
    Split the functionality into 2 methods.

    One for parsing the cli and one that runs the application.
    """
    from .core import Core

    c = Core(
        cli_args["<package>"],
    )

    if cli_args["basic"]:
        c.basic()

    if cli_args["description"]:
        c.description()

    if cli_args["downloads"]:
        c.downloads()

    if cli_args["releases"]:
        c.releases()

    if cli_args["release"]:
        c.release(cli_args["<version>"])

    if cli_args["raw"]:
        c.raw()

    return c


if __name__ == '__main__':
    args = parse_cli()
    run(args)
