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
                        help='Report processes using more than MEMORY bytes of memory')
    parser.add_argument('-c', '--cpu', default=defaults.cpu_trigger, type=float,
                        help='Report processes using more than CPU percent CPU')
    parser.add_argument('-z', '--zombies', action='store_true',
                        help='Also watch zombie processes')
    parser.add_argument('-n', '--name', nargs='+',
                        help='Only watch processes named with one of the specified names')
    parser.add_argument('-e', '--exclude', nargs='+', default=[],
                        help='Exclude processes named with one of the specified names')
    opts = parser.parse_args()
    setup_logger(debug=opts.debug, verbose=opts.verbose)
    pwatch(opts.interval, opts.memory, opts.cpu, opts.name, opts.exclude, opts.zombies)


if __name__ == "__main__":
    main()
