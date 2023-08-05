import logging
import os
import sys

log = logging.getLogger(__name__)

FROZEN = getattr(sys, u'frozen', False)


def _app_cwd():
    if FROZEN:  # pragma: no cover
        # we are running in a |PyInstaller| bundle
        cwd = os.path.dirname(sys.argv[0])
        if cwd.endswith('MacOS') is True:
            log.debug('Looks like we\'re dealing with a Mac Gui')
            cwd = os.path.dirname(os.path.dirname(os.path.dirname(app_cwd)))

    else:
        # we are running in a normal Python environment
        cwd = os.getcwd()
    return app_cwd


app_cwd = _app_cwd()
