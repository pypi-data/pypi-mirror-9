"""
Fairly generic utility functions that have no knowledge of Stolos and
could just as well be in a third party library
"""
import collections
import functools
import inspect
import importlib
import argparse

from . import log
from .exceptions import _log_raise, DAGMisconfigured


def cached(_func=None, ignore_kwargs=(), memoize=1):
    """A function decorator to cache results of function call.
    Each cache is instantiated per function instance it decorates.
    If the cached function is redefined (ie the module is reloaded),
    its cache gets overwritten.

    ignore_kwargs: a list of kwargs to ignore

    This is solved in python3 via lru_cache
    """
    def cached_wrapper(func):
        @functools.wraps(func)
        def _cached(*args, **kwargs):
            if not hasattr(_cached, 'cache'):
                _cached.cache = {}
                cached.CACHES[(func.__module__,
                               func.func_name)] = _cached.cache
            params = inspect.getcallargs(func, *args, **kwargs)
            # drop certain keywords from cache key
            if isinstance(ignore_kwargs, str):
                del params[ignore_kwargs]
            else:
                for ign in ignore_kwargs:
                    del params[ign]
            # convert all dicts and lists to tuples
            for key in params:
                if isinstance(params[key], collections.Mapping):
                    params[key] = hash(tuple(sorted(params[key].items())))
                elif isinstance(params[key], collections.Sequence):
                    params[key] = hash(tuple(sorted(params[key])))
                elif isinstance(params[key], argparse.Namespace):
                    params[key] = hash(
                        tuple(sorted(params[key].__dict__.items())))
            key = (func.func_name, hash(tuple(sorted(params.items()))))
            if key not in _cached.cache:
                if memoize:
                    log.debug('STORE %s' % str(key))
                _cached.cache[key] = func(*args, **kwargs)
            if memoize == 2:
                log.debug('GET %s' % str(key))
            return _cached.cache[key]
        return _cached
    # Nifty trick to make @cached and @cached() both valid
    if _func:
        return cached_wrapper(_func)
    else:
        return cached_wrapper
cached.CACHES = {}


def pre_condition(validation_func):
    """A decorator that applies given validation_func just before calling
    the decorated func.

    Example:

        @pre_condition(lambda var1, var3: var1 == var3)
        def myfunc(var1, var2=99, var3=1):
            return "I ran"

        myfunc(1, 2, 3)  # raises
        myfunc(1, 2, 1)  # --> "I ran"
        myfunc(1, var3=1)  # --> "I ran"
        myfunc(1, var3=1, var2=2)  # --> "I ran"

        myfunc(1)  # raises  - it's not smart enough to extract default kwargs
    """
    def __decorator(func):
        @functools.wraps(func)
        def _decorator(*args, **kwargs):
            kws2 = dict(zip(func.func_code.co_varnames, args))
            kws2.update(kwargs)
            nargs = validation_func.func_code.co_argcount
            validation_args = (
                kws2[k] for k in validation_func.func_code.co_varnames[:nargs]
                if k in kws2)
            assert validation_func(*validation_args), (
                "validation_func %s did not return True"
                % validation_func.func_name)
            return func(*args, **kwargs)
        return _decorator
    return __decorator


def crossproduct(list_of_lists):
    try:
        first_lst = list_of_lists[0]
    except IndexError:  # Basecase
        yield []
        return
    for itm in first_lst:
        for combined_lst in crossproduct(list_of_lists[1:]):
            yield [itm] + combined_lst


def flatmap_with_kwargs(func, kwarg_name, list_or_value, **func_kwargs):
    """apply func(`kwarg_name`=elem, **`func_kwargs`) to every element
    of given `list_or_value` and return an iterator that flattens all results.

    `func` - a function that returns an iterable
    `kwarg_name` - a keyword argument to `func`
    `list_or_value` - a list of values to kwarg_name, or just a single value
    `func_kwargs` - any extra arguments to pass on
    """
    if isinstance(list_or_value, collections.Sequence):
        for _grp in list_or_value:
            func_kwargs[kwarg_name] = _grp
            for rv in func(**func_kwargs):
                yield rv
    else:
        func_kwargs[kwarg_name] = list_or_value
        for rv in func(**func_kwargs):
            yield rv


def lazy_set_default(dct, key, lazy_val_func, *args, **kwargs):
    """
    A variant of dict.set_default that requires a function instead of a value.

    >>> d = dict()
    >>> lazy_set_default(d, 'a', lambda val: val**2, 5)
    25
    >>> lazy_set_default(d, 'a', lambda val: val**3, 6)
    25
    >>> d
    {'a': 25}
    """
    try:
        val = dct[key]
    except KeyError:
        val = lazy_val_func(*args, **kwargs)
        dct[key] = val
    return val


@cached
def load_obj_from_path(import_path, ld=dict()):
    """
    import a python object from an import path like:

        mypackage.module.func
        or
        mypackage.module.class

    """
    log.debug(
        'attempting to load a python object from an import path',
        extra=dict(import_path=import_path, **ld))
    try:
        path, obj_name = import_path.rsplit('.', 1)
    except ValueError:
        _log_raise(
            ("import path needs at least 1 period in your import path."
             " An example import path is something like: module.obj"),
            extra=dict(import_path=import_path, **ld),
            exception_kls=DAGMisconfigured)
    mod = importlib.import_module(path)
    try:
        obj = getattr(mod, obj_name)
    except AttributeError:
        _log_raise(
            ("object does not exist in given module."
             " Your import path is not"
             " properly defined because the given `obj_name` does not exist"),
            extra=dict(import_path=import_path, obj_name=obj_name, **ld),
            exception_kls=DAGMisconfigured)
    return obj
