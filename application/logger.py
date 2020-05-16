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
        format = cls.get_format(level)
        logger.setLevel(level)
        logging.basicConfig(format=format)
        return logger
