from nose.plugins.base import Plugin
from nose import util
import os
import test_steps

class AutoCheckLog(Plugin):
    """
    This plugin log helper for test_steps module in nose.

    Usage examples:
      > nosetests --with-autochecklog
    """

    name = 'autochecklog'

    def options(self, parser, env=os.environ):
        super(AutoCheckLog, self).options(parser, env=env)

    def configure(self, options, conf):
        super(AutoCheckLog, self).configure(options, conf)
        if not self.enabled:
            return

        test_steps.auto_func_detection(False)

    def prepareTestCase(self, test):
        path, name, func = util.test_address(test)
        test_steps.log_new_func(func, path)

