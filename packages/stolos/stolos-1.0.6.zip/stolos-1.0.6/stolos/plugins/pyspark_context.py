import atexit
import functools
from pyspark import SparkConf, SparkContext
import sys
import os

from stolos import dag_tools as dt
from . import log


def receive_kwargs_as_dict(func):
    """A decorator that recieves a dict and passes the kwargs to wrapped func.
    It's very useful to use for spark functions:

        @receive_kwargs_as_dict
        def myfunc(a, b):
            return a > 1

        print myfunc({'a': 4, 'b': 6})
        sc.parallelize([{'a': 1, 'b': 2}, {'a': 3, 'b': 4}]).filter(myfunc)
    """
    @functools.wraps(func)
    def _partial(kwargs_dct, **kwargs):
        kwargs.update(kwargs_dct)
        return func(**kwargs)
    return _partial


def get_spark_context(conf={}, osenv={}, files=[], pyFiles=[], app_name=None):
    """Wrap pyspark.SparkContext.  If SparkContext has already been initialized,
    return the initialized Context

    There are two ways to call this function.  The simplest:

        sc = get_spark_context(app_name='myapp')

    The more complex:

        conf - (dict, required) a dictionary of key-value configuration
             - or, a pre-configured SparkConf instance
        osenv - (dict, optional) the environment variables to set on executors
        files - (list of str, optional) files to send to executors
        pyFiles - (list of str, optional) python files to send to executors

    If you wish to combine `app_name` with other kwargs, here's what happens:
        - the `osenv` is updated with env from app configuration if it exists
        - `conf`, if a dict, is treated like osenv and otherwise uses the app
        configuration data
        - files and pyFiles are extended to include app configuration


    An example configuration:
        conf = {
            "spark.app.name": "myapp",
            "spark.master": "local[30]",
            "spark.local.dir": "/tmp" }

    """
    if app_name:
        _conf, _osenv, _files, _pyFiles = get_spark_conf(app_name)
        # some stupid merge rules to support `app_name` and the other kwargs
        if isinstance(conf, dict):
            conf = dict(conf)
            conf.update(_conf)
        else:
            conf = _conf
        osenv = dict(osenv)
        osenv.update(_osenv)
        files = set(files)
        files.update(_files)
        files = list(files)
        pyFiles = set(pyFiles)
        pyFiles.update(_pyFiles)
        pyFiles = list(pyFiles)

    if not isinstance(conf, dict):
        assert isinstance(conf, SparkConf)
        conf = dict(conf.getAll())
    _spark_conf = SparkConf()
    for k, v in conf.items():
        _spark_conf.set(k, v)
    conf = _spark_conf

    if osenv:
        conf.setExecutorEnv(pairs=osenv.items())
    try:
        sc = SparkContext(conf=conf)
    except ValueError:
        log.warn("Another Spark Context is already active.  Using that one")
        return SparkContext._active_spark_context
    for method, lst in [(sc.addPyFile, pyFiles), (sc.addFile, files)]:
        for path in lst:
            if not path:
                continue
            method(path)
    atexit.register(sc.stop)
    return sc


def get_module_from_fp(fp):
    """Load a module from given file path
    The module's import path is guaranteed to be in the sys.path
    and therefore serializable by spark"""
    _parts = fp.split('/')
    paths = ('/'.join(_parts[:i]) for i in range(len(_parts) - 1, 0, -1))
    path = '.'  # basecase
    for path in paths:
        if path in sys.path:
            break
    from_package, import_name = (
        fp
        .replace(path + '/', '')
        .replace('/', '.')
        .rsplit('.', 1)
    )
    return __import__(from_package, fromlist=[import_name])


def get_spark_conf(app_name):
    """Query Stolos's dag graph for all information necessary to
    create a pyspark.SparkContext"""
    dg = dt.get_tasks_config()
    conf = dict(**dg[app_name].get('spark_conf', {}))
    conf['spark.app.name'] = app_name
    osenv = {k: os.environ[k] for k in dg[app_name].get('env_from_os', [])}
    osenv.update(dg[app_name].get('env', {}))
    pyFiles = dg[app_name].get('uris', [])
    files = []  # for now, we're ignoring files.
    return conf, osenv, files, pyFiles
