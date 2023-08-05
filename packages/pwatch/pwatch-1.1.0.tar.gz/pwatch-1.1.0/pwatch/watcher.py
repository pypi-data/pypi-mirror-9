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
                except Exception as e:
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

        try:
            io_counters = process.io_counters()
        except:
            from collections import namedtuple
            IOCounters = namedtuple("IOCounters", 'read_count write_count read_bytes write_bytes')
            io_counters= IOCounters(read_count=-1, write_count=-1,
                                    read_bytes=0, write_bytes=0)

        r = ("Process {name}({pid}) detected excessive: "
             "mem: {mem:.2f} MB | "
             "cpu: {cpu:.2f}% | "
             "uptime: {uptime}s | "
             "threads: {thr} | "
             "FDs: {fds} | "
             "IO reads: {ior} ({ior_sz:.2f} kB) | "
             "IO writes: {iow} ({iow_sz:.2f} kB) | "
             "context switches: {ctx_switches} | "
             "command: {cmd}"
             ).format(
                name=process.name(),
                pid=process.pid,
                mem=float(process.memory_info().rss) / 1024 / 1024,
                cpu=process.last_cpu_percent,
                uptime=int(time.time() - process.create_time()),
                thr=process.num_threads(),
                fds=process.num_fds(),
                ior=io_counters.read_count,
                iow=io_counters.write_count,
                ior_sz=float(io_counters.read_bytes) / 1024,
                iow_sz=float(io_counters.write_bytes) / 1024,
                ctx_switches=process.num_ctx_switches().voluntary,
                cmd=' '.join(process.cmdline()),
             )
        self.logger.error(r)


    def check_memory(self, process):
        """
        Check if process is above memory usage trigger

        """
        if self.memory_trigger is None:
            return False
        try:
            return process.memory_info().rss >= self.memory_trigger
        except Exception as e:
            self.logger.warning("Error occured while checking memory info for {} ({}): {}"
                                .format(process.name(), process.pid, e))
            return False


    def check_cpu(self, process):
        """
        Check if process is above CPU usage trigger

        """
        if self.cpu_trigger is None:
            return False
        try:
            process.last_cpu_percent = process.cpu_percent()
            return process.last_cpu_percent >= self.cpu_trigger
        except Exception as e:
            self.logger.warning("Error occured while checking CPU info for {} ({}): {}"
                                .format(process.name(), process.pid, e))
            return False


    def check_process(self, process):
        """
        Check a process against memory and cpu triggers

        """
        return self.check_memory(process) or self.check_cpu(process)
