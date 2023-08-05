"""
This module contains entry points for pwatch

"""
import sys

from . import pwatch
from .defaults import defaults
from .log import setup_logger


def main():
    """
    Main entry point for pwatch

    """
    import argparse

    parser = argparse.ArgumentParser(
        description='This program is a simple process watcher daemon',
        epilog='Copyright Quanta 2015'
    )
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Switch to DEBUG log level')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Enable verbose mode')
    parser.add_argument('-i', '--interval', default=defaults.run_interval, type=float,
                        help='Polling interval')
    parser.add_argument('-m', '--memory', default=defaults.memory_trigger, type=int,
                        help='Report processes using more than n bytes')
    parser.add_argument('-c', '--cpu', default=defaults.cpu_trigger, type=float,
                        help='Report processes using more than n percent CPU')
    opts = parser.parse_args()
    setup_logger(debug=opts.debug, verbose=opts.verbose)
    pwatch(opts.interval, opts.memory, opts.cpu)


if __name__ == "__main__":
    main()
