import logging
import warnings


def log_format_string():
    warnings.warn(u'Use log_formater', DeprecationWarning)
    return logging.Formatter('[%(levelname)s] %(name)s '
                             '%(lineno)d: %(message)s')


def log_formatter():
    return logging.Formatter('[%(levelname)s] %(name)s '
                             '%(lineno)d: %(message)s')
