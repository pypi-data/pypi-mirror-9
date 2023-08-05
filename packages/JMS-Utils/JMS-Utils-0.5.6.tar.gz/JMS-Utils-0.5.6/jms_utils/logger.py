import logging


def log_format_string():
    return logging.Formatter('[%(levelname)s] %(name)s '
                             '%(lineno)d: %(message)s')
