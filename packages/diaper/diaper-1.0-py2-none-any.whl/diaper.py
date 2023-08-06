"""Diaper pattern

Args:
    f: Function to be called.
    *args: Arguments to pass to the function to be called.
    **kwargs: Keywords to pass to the function to be called.

Returns: Result of the function call if no exception is raised. Otherwise it returns None.

Usage:
    # an instance of DiaperType has been created for your convenience:
    import diaper

    # call it directly
    diaper(function, *function_args, **function_kwargs)

    # as a context manager
    with diaper:
        do_terrible_things_here()

"""

import sys
from types import ModuleType

class Diaper(ModuleType):
    def __call__(self, f, *args, **kwargs):
        try:
            return f(*args, **kwargs)
        except:
            pass

    def __enter__(self):
        # Do nothing
        pass

    def __exit__(self, exctype, excinst, exctb):
        return True

# Well, the diaper pattern's already pretty shitty,
# let's go ahead and just do some module impersonation
sys.modules[__name__] = Diaper(__name__, __doc__)
