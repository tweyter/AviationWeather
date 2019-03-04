# coding=utf-8
import configparser
import os
import logging


def configure_logging(*handlers: logging.Handler):
    """
    Set up logging for each type of logging handler.

    Handler types will vary with the environment and whether we are using Sentry.io
    or not.

    :param handlers: the various logging.Handler objects
    """
    log_format = "[%(asctime)s][%(levelname)s] %(name)s %(filename)s:%(funcName)s:%(lineno)d | %(message)s\n"
    root_logger = logging.getLogger()
    for handler in handlers:
        if isinstance(handler, logging.FileHandler):
            formatter = logging.Formatter(log_format)
            handler.setFormatter(formatter)
            handler.setLevel(logging.ERROR)
            root_logger.addHandler(handler)
        elif isinstance(handler, logging.StreamHandler):
            formatter = logging.Formatter(log_format)
            handler.setFormatter(formatter)
            handler.setLevel(logging.DEBUG)
            root_logger.addHandler(handler)

    root_logger.propagate = False
    return


def setup():
    config = configparser.ConfigParser()
    config.read(
        os.path.join(
            os.path.dirname(__file__),
            "config.ini",
        )
    )

    if config['logging']['environment'] == 'development':
        configure_logging(logging.StreamHandler())
    else:
        if not os.path.exists(config['logging']['logpath']):
            os.mkdir(config['logging']['logpath'])
        configure_logging(
            logging.FileHandler(os.path.join(config['logging']['logpath'], 'errors.log'))
        )
