import logging
import os
import warnings

from jms_utils.app import _app_cwd

log = logging.getLogger(__name__)


def warn():
    warnings.warn('app_cwd moved to jms_utils.app.app_cwd',
                  DeprecationWarning)
    return _app_cwd()

app_cwd = warn()


class ChDir(object):
    # Step into a directory temporarily. Then return to
    # orignal directory.
    def __init__(self, path):
        self.old_dir = os.getcwd()
        self.new_dir = path

    def __enter__(self):
        log.debug(u'Changing to Directory --> {}'.format(self.new_dir))
        os.chdir(self.new_dir)

    def __exit__(self, *args, **kwargs):
        log.debug(u'Moving back to Directory --> {}'.format(self.old_dir))
        os.chdir(self.old_dir)
