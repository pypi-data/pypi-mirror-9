"""
This module contains logging utilities for pwatch

"""

_logger = None


def get_logger():
    """
    Returns the logging instance

    """
    import logging
    global _logger

    if _logger is None:
        _logger = logging.getLogger('pwatch')
    return _logger


def setup_logger(debug=False, verbose=False, logger=None):
    """
    Create a logger object and configure it with different handlers

    """
    import logging
    from logging import handlers as lhandlers

    logger = logger or get_logger()
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    if verbose:
        logger.addHandler(logging.StreamHandler())
    try:
        handler = logging.handlers.SysLogHandler('/dev/log')
        handler.setFormatter(logging.Formatter(
            '%(asctime)s %(name)s: %(message)s',
            '%b %e %H:%M:%S'
        ))
        logger.addHandler(handler)
    except Exception as e:
        logger.error("Cannot attach syslog handler to logger: {}".format(e.strerror))
    return logger
