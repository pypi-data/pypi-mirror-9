import logging
import os


def _get_switch(name, default):
    value = os.environ.get(name, default)
    try:
        value = int(value)
    except Exception:
        raise Exception("invalid setting %s=%r" % (name, value))
    return value


def get_logger(obj=None):

    log_to_file = _get_switch("PACER_LOG_TO_FILE", "0")
    log_to_console = _get_switch("PACER_LOG_TO_CONSOLE", "1")

    if 0 and obj is not None:
        if hasattr(obj, "__name__"):
            name = "%s.%s" % (obj.__module__, obj.__name__)
        else:
            module = obj.__class__.__module__
            clzname = obj.__class__.__name__
            name = "%s.%s" % (module, clzname)
    else:
        name = __package__

    logger = logging.getLogger(name)
    if os.environ.get("LOGLEVEL", "").upper() == "DEBUG":
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    if not(len(logger.handlers)):
        fmt = "%%(asctime)s:%%(processName)-14s: %s : %%(levelname)-6s:%%(message)s" % name
        default_formatter = logging.Formatter(fmt)
        if log_to_console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(default_formatter)
            logger.addHandler(console_handler)
        if log_to_file:
            file_handler = logging.FileHandler("pacer%d.log" % os.getpid(), "a")
            file_handler.setFormatter(default_formatter)
            logger.addHandler(file_handler)
        if not log_to_console and not log_to_file:
            # avoids warnigs becausee logger has not handler at all unless we set NullHandler:
            logger.addHandler(logging.NullHandler())

    return logger
