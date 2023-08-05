"""
Pwatch is a process watcher to detect memory/CPU consuming processes and report
about them.

Author: Matthieu 'Korrigan' Rosinski <mro@quanta-computing.com>

"""

from .watcher import PWatch
from .log import get_logger
from .defaults import defaults


def pwatch(interval=defaults.run_interval,
           memory_trigger=defaults.memory_trigger,
           cpu_trigger=defaults.cpu_trigger):
    """
    The main function for pwatch: it looks each active process and report those
    who are using excessive memory
    This function will run forever until the process is killed

    """
    p = PWatch(interval, memory_trigger, cpu_trigger)
    p.loop()
