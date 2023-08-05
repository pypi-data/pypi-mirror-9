"""
This module contains all the logic for pwatch

"""
import psutil

from .defaults import defaults


class PWatch:
    """
    The main class for pwatch

    """

    def __init__(self, interval=None, memory_trigger=None, cpu_trigger=None):
        """
        Initialize the process watcher

        """
        from .log import get_logger

        self.logger = get_logger()
        self.run_interval = interval or defaults.run_interval
        self.memory_trigger = memory_trigger
        self.cpu_trigger = cpu_trigger


    def run(self):
        """
        Process all pids and report those who are using excessive resources

        """
        self.logger.debug('Processing...')
        for p in psutil.process_iter():
            if self.check_process(p):
                try:
                    self.report(p)
                except:
                    self.logger.warning("Cannot generate report for process {} ({}): {}"
                                        .format(p.name(), p.pid, e))


    def loop(self):
        """
        Run the process watcher forever

        """
        import time

        start_log = 'Started pwatch with limits: '
        if self.cpu_trigger is not None:
            start_log += 'cpu: {:.2f}% '.format(self.cpu_trigger)
        if self.memory_trigger is not None:
            start_log += 'mem: {:.2f} MB '.format(float(self.memory_trigger) / 1024 / 1024)
        self.logger.info(start_log)
        while 42:
            self.run()
            time.sleep(self.run_interval)


    def report(self, process):
        """
        Generate a report for the process and write it to the logger

        """
        import time

        r = ("Process {name}({pid}) detected excessive: "
             "mem: {mem:.2f} MB | "
             "cpu: {cpu:.2f}% | "
             "uptime: {uptime}s | "
             "command: {cmd}"
             ).format(
                name=process.name(),
                pid=process.pid,
                mem=float(process.memory_info().rss) / 1024 / 1024,
                cpu=process.cpu_percent(interval=0.1),
                uptime=int(time.time() - process.create_time()),
                cmd=' '.join(process.cmdline()),
             )
        self.logger.error(r)


    def check_memory(self, process):
        if self.memory_trigger is None:
            return False
        try:
            return process.memory_info().rss >= self.memory_trigger
        except Exception as e:
            self.logger.warning("Error occured while checking memory info for {} ({}): {}"
                                .format(process.name(), process.pid, e))
            return False


    def check_cpu(self, process):
        if self.cpu_trigger is None:
            return False
        try:
            return process.cpu_percent() >= self.cpu_trigger
        except Exception as e:
            self.logger.warning("Error occured while checking CPU info for {} ({}): {}"
                                .format(process.name(), process.pid, e))
            return False


    def check_process(self, process):
        """
        Check a process against memory and cpu trigger

        """
        return self.check_memory(process) or self.check_cpu(process)
