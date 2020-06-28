import logging
import os


class Logger:
    @classmethod
    def get_format(cls, level):
        log_format = None
        if level == "DEBUG":
            log_format = "%(levelname)-7s: [%(name)s] %(message)s"
        else:
            log_format = "%(levelname)-7s: %(message)s"

        return log_format

    @classmethod
    def create_logger(cls, name, level=os.environ.get("LOG_LEVEL") or "INFO"):
        logger = logging.getLogger(name)
        logger.setLevel(level)
        logFormatter = logging.Formatter(cls.get_format(level))
        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(logFormatter)

        logger.addHandler(consoleHandler)
        return logger
