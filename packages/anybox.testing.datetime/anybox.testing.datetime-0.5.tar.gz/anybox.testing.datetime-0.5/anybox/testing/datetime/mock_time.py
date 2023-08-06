"""Patch of time module to follow datetime.set_now

Note: monkey-patching time.time works within a module or interactive session,
but not in subsequent imports from other modules.
Replacing the whole time module by this one does work.
"""

from time import *  # noqa
from time import time as original_time
from datetime import datetime


class Time(object):
    def time(self):
        if datetime._current_now is None:
            return time()
        now = datetime.now()
        return mktime(now.timetuple()) + now.microsecond / 1000000

    def localtime(self, *a):
        if datetime._current_now is None or len(a) == 1:
            return localtime(*a)
        return datetime.now().timetuple()

    def strftime(self, *a):
        if datetime._current_now is None or len(a) == 2:
            return strftime(*a)
        return strftime(a[0], datetime.now().timetuple())

    def ctime(self, *a):
        if datetime._current_now is None or len(a) == 1:
            return ctime(*a)
        return datetime.now().ctime()

    def asctime(self, *a):
        if datetime._current_now is None or len(a) == 1:
            return asctime(*a)
        return asctime(datetime.now().timetuple())

    def gmtime(self, *a):
        if datetime._current_now is None or len(a) == 1:
            return gmtime(*a)
        return datetime.now().timetuple()
