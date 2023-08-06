import sys
import mock_dt
old_dt = sys.modules['datetime']
sys.modules['datetime'] = mock_dt

# happy monkey time
import time
import mock_time
mocktime = mock_time.Time()
old_time = sys.modules['time']
for method in [m for m in dir(mocktime) if not m.startswith('_')]:
    setattr(time, method, getattr(mocktime, method))

ALL_PATCHED = {old_dt: mock_dt,
               # old_time: mock_time,
               mock_dt.original_datetime: mock_dt.datetime,
               # mock_time.original_time: mock_time.time
               }

# taking care of already imported modules
for modname, mod in sys.modules.items():
    if mod is mock_dt or mod is mock_time:
        continue

    for symb in dir(mod):

        # Unhashable types do not always give a TypeError: unhashable type
        # if used as dict keys.
        # Example: instances of weakref.WeakValueDictionary
        #          on this CPython 2.7.5 (but not on the CPython 2.6.8 the
        #          same box has).
        # Therefore we need to check before hand, rather than try and catch
        # exceptions.
        #
        # getattr(mod, symb) also fails for some modules such as dbm_gnu because of six
        try:
            ref = getattr(mod, symb)
            hash(ref)
        except:
            continue

        replacement = ALL_PATCHED.get(ref)
        if replacement is not None:
            setattr(mod, symb, replacement)


# registering sqlite3 adapter/converters
from . import sqlite3  # noqa
