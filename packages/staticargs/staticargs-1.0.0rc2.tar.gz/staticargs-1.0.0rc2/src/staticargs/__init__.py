import copy
from functools import wraps
import inspect

def staticargs(fn):
    @wraps(fn)
    def newfn(*args, **kwargs):
        kw = dict()
        (fnargs, _, _, defaults) = inspect.getargspec(fn)

        # Chop off arguments we already have
        num_of_args_passed = len(args)
        fnargs = fnargs[num_of_args_passed:]

        # Get the number of default arguments
        if len(defaults) < len(fnargs):
            num_of_def_args = len(defaults)
            defargs = fnargs[-num_of_def_args:]
        else:
            num_of_def_args_given = len(defaults) - len(fnargs)
            defargs = fnargs
            defaults = defaults[num_of_def_args_given:]

        # Get the arguments with defaults
        for (arg, default) in zip(defargs, defaults):
            kw[arg] = copy.copy(default)

        kw.update(kwargs)
        return fn(*args, **kw)
    return newfn
