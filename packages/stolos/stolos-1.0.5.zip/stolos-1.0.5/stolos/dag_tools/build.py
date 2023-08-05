import networkx as nx
import os
import tempfile

from stolos import util
from stolos.exceptions import _log_raise, _log_raise_if, DAGMisconfigured
from stolos.configuration_backend import (
    TasksConfigBaseMapping, TasksConfigBaseSequence)

from .constants import (DEPENDENCY_GROUP_DEFAULT_NAME, JOB_ID_VALIDATIONS)
from . import node


def _validate_dep_grp_metadata(dep_grp, ld, tasks_conf, dep_name):
    """
    Test that a dependency group correctly defined.

    `dep_grp` (obj) - Configuration data for a dependency group.  It is an
        instance that inherits from TasksConfigBaseMapping.
        Visualized as a dict or json, a dep_grp might look like:
            dep_grp = {"app_name": ["app2", "app3"]}
    `ld` (dict) - helpful info for error logs.  It also contains
        the app_name this dep_grp belongs to.
    `tasks_conf` (obj) - The configuration for all tasks. It is an instance
        that inherits from TasksConfigBaseMapping
    `dep_name` (str) - The name for this dependency group.

    """
    ld1 = ld
    _template, child_template = node.get_job_id_template(ld['app_name'])
    for parent_app_name in dep_grp['app_name']:
        ld = dict(
            parent_app_name=parent_app_name,
            dependency_group="depends_on.%s" % dep_name, **ld1)

        _log_raise_if(
            parent_app_name not in tasks_conf,
            "Unrecognized parent_app_name in a `depends_on` dependency group",
            extra=ld,
            exception_kls=DAGMisconfigured)
        _, parent_template = node.get_job_id_template(parent_app_name)
        if len(dep_grp) == 1:
            _log_raise_if(
                not set(child_template).issuperset(parent_template),
                ("If you choose specify a dependency group with no job_id"
                 " identifiers, then the"
                 " child task's job_id identifiers must be a superset of those"
                 " in the parent's job_id. Otherwise, there"
                 " are cases where you cannot identify"
                 " a parent job_id given a child job_id."),
                extra=dict(
                    parent_job_id_template=parent_template,
                    child_job_id_template=child_template,
                    **ld),
                exception_kls=DAGMisconfigured)
        # for every parent, does the dependency group define enough information
        # to support a bubble-up or bubble-down operation?
        required_keys = set(child_template
                            ).difference(parent_template)
        missing_keys = required_keys.difference(dep_grp)
        _log_raise_if(
            missing_keys,
            ("This app's dependency group is missing some required"
             " job_id identifiers"), extra=dict(
                 missing_job_id_identifiers=missing_keys,
                 job_id_template=_template, **ld),
            exception_kls=DAGMisconfigured)
    for k, v in dep_grp.items():
        _log_raise_if(
            len(set(v)) != len(v),
            "You have duplicate metadata in dependency group metadata",
            extra=dict(key=k, value=v, **ld),
            exception_kls=DAGMisconfigured)


def _validate_dependency_groups_part2(dep_name, dep_grp, ld, tasks_conf):
    _log_raise_if(
        ("app_name" not in dep_grp
         or not isinstance(dep_grp["app_name"], TasksConfigBaseSequence)),
        ("Each dependency group the task depends on must specify"
         " an app_name key whose value is a sequence of items"
         " (ie a TasksConfigBaseSequence)"),
        extra=dict(
            key="depends_on", invalid_dependency_group=dep_name,
            dep_grp=str(dict(dep_grp)), **ld),
        exception_kls=DAGMisconfigured)
    _validate_dep_grp_metadata(
        dep_grp, ld=ld, tasks_conf=tasks_conf, dep_name=dep_name)
    _validate_dep_grp_with_job_id_validations(dep_grp, ld=ld)


def _validate_dep_grp_with_job_id_validations(dep_grp, ld):
    """Do the user defined job_id validations, if they exist,
    apply to each individual value of the relevant key in the dep group?"""
    for k, v in dep_grp.items():
        func = JOB_ID_VALIDATIONS.get(k)
        if not func:
            continue
        for vv in v:
            try:
                res = func(vv)
            except Exception as err:
                _log_raise((
                    "The job_id_validation you created did not like a value"
                    " in your task configuration. Your error was: "
                ) + err.message,
                    extra=dict(key='%s.%s' % (k, v), value=vv, **ld),
                    exception_kls=DAGMisconfigured)

            _log_raise_if(
                vv != res,
                ("The job_id_validation you created modified a value"
                 " in your task configuration."),
                extra=dict(key='%s.%s' % (k, v), value=vv, **ld),
                exception_kls=DAGMisconfigured)


def _validate_dependency_groups(tasks_conf, metadata, ld):
    if "depends_on" not in metadata:
        return

    for dep_name, dep_grp in metadata["depends_on"].items():
        _log_raise_if(
            dep_name in tasks_conf,
            ("Task's depends_on value has a naming conflict. You cannot"
             " identify a dependency group with the same name as an"
             " app_name."),
            extra=dict(
                key="depends_on",
                invalid_dependency_group=dep_name,
                **ld),
            exception_kls=DAGMisconfigured)
        # validate scenario where the dep_grp is made up of subgrpA AND subgrpB
        if isinstance(dep_grp, TasksConfigBaseSequence):
            for _dep_grp in dep_grp:
                _validate_dependency_groups_part2(
                    dep_name, _dep_grp, ld, tasks_conf)
            # check job_id template identifiers are consistently defined
            # across the dependency group
            for identifier in node.get_job_id_template(ld['app_name'])[1]:
                values = [_dep_grp.get(identifier) for _dep_grp in dep_grp
                          if 'job_id' not in _dep_grp]
                _log_raise_if(
                    not reduce(lambda x, y: x == y, values),
                    ("You specified inconsistent values for job_id"
                     " metadata.  Each sub-dependency in your dependency"
                     " group must specify the exact same metadata value"
                     " for each identifier in your app's job_id template."),
                    # because otherwise, users could easily create unexpected
                    # dependence relations
                    extra=dict(
                        key="depends_on", invalid_dependency_group=dep_name,
                        invalid_identifier=identifier,
                        values=values, **ld),
                    exception_kls=DAGMisconfigured)
        else:
            _validate_dependency_groups_part2(
                dep_name, dep_grp, ld, tasks_conf)


def validate_depends_on(app_name1, metadata, dg, tasks_conf, ld):
    if "depends_on" not in metadata:
        return

    _log_raise_if(
        not isinstance(metadata["depends_on"], TasksConfigBaseMapping),
        ("Configuration Error: Task's value at the depends_on key"
         " must subclass TasksConfigBaseMapping"),
        extra=dict(key="depends_on",
                   received_value_type=type(metadata["depends_on"]),
                   **ld),
        exception_kls=DAGMisconfigured)
    # depends_on  - are we specifying only one unnamed dependency group?
    if "app_name" in metadata["depends_on"]:
        _validate_dep_grp_metadata(
            dep_grp=metadata['depends_on'],
            ld=ld, tasks_conf=tasks_conf,
            dep_name=DEPENDENCY_GROUP_DEFAULT_NAME)
    # depends_on  - are we specifying specific dependency_groups?
    else:
        _validate_dependency_groups(tasks_conf, metadata, ld)
        # depends_on  -  are dependent tasks listed properly?
        for parent in dg.pred[app_name1]:
            _log_raise_if(
                parent not in tasks_conf,
                "Task defines an unrecognized parent dependency",
                extra=dict(parent_app_name=parent, **ld),
                exception_kls=DAGMisconfigured)


def validate_if_or(app_name1, metadata, dg, tasks_conf, ld):
    # valid_if_or  -  are we specifying what makes a job valid correctly?
    if 'valid_if_or' not in metadata:
        return

    for k, v in metadata['valid_if_or'].items():
        if k == '_func':
            continue
        location = "%s.valid_if_or.%s" % (app_name1, k)
        _log_raise_if(
            not isinstance(v, TasksConfigBaseSequence),
            "Task is misconfigured.  Wrong value type. Expected a sequence",
            extra=dict(wrong_value_type=type(v), key=location, **ld),
            exception_kls=DAGMisconfigured)
        templ = node.get_job_id_template(app_name1)[1]
        _log_raise_if(
            k not in templ,
            "valid_if_or contains a key that isn't in its job_id template",
            extra=dict(key=k, job_id_template=templ, **ld),
            exception_kls=DAGMisconfigured)
        try:
            validation_func = JOB_ID_VALIDATIONS[k]
        except KeyError:
            continue
        for vv in v:
            try:
                validation_func(vv)
            except Exception as err:
                _log_raise(
                    ("valid_if_or contains a value that wasn't validated"
                     " by your job_id_validations. err: %s(%s)")
                    % (err.__class__, err),
                    extra=dict(key=location, wrong_value_type=type(vv), **ld),
                    exception_kls=DAGMisconfigured)


def validate_job_type(app_name1, metadata, dg, tasks_conf, ld):

    # job_type  -  Is this a recognized job_type and does it exist?
    _log_raise_if(
        metadata.get('job_type') not in ['pyspark', 'bash'],
        ("Invalid job_type. All tasks must define one."
         " Valid job_types are 'pyspark' or 'bash'"), extra=dict(
             job_type=metadata.get('job_type', 'no job_type specified'), **ld),
        exception_kls=DAGMisconfigured)


def validate_bash_opts(app_name1, metadata, dg, tasks_conf, ld):
    # bash_opts  -  Is job_type specified if has bash_opts?
    if 'bash_opts' not in metadata:
        return

    _log_raise_if(
        metadata.get('job_type') != 'bash',
        ('If you specify bash_opts in task config, you must also set'
         ' job_type="bash"'), extra=dict(**ld), exception_kls=DAGMisconfigured)

    _log_raise_if(
        not isinstance(metadata['bash_opts'], (str, unicode)),
        ('bash_opts must be a string'),
        extra=dict(**ld), exception_kls=DAGMisconfigured)


def validate_spark_conf(app_name, metadata, dg, tasks_conf, ld):
    if 'spark_conf' not in metadata:
        return

    # spark_conf - Is it a dict of str: str pairs?
    _log_raise_if(
        not isinstance(metadata["spark_conf"], TasksConfigBaseMapping),
        "spark_conf, if supplied, must be a key:value mapping.",
        extra=dict(**ld),
        exception_kls=DAGMisconfigured)

    for k, v in metadata["spark_conf"].items():
        _log_raise_if(
            not isinstance(k, (unicode, str)),
            "Key in spark_conf must be a string",
            extra=dict(key=k, key_type=type(k), **ld),
            exception_kls=DAGMisconfigured)
        _log_raise_if(
            isinstance(v, (TasksConfigBaseSequence, TasksConfigBaseMapping,
                           list, dict, tuple)),
            "Value for given key in spark_conf must be an int, string or bool",
            extra=dict(key=k, value_type=type(v), **ld),
            exception_kls=DAGMisconfigured)


def validate_env(app_name, metadata, dg, tasks_conf, ld):
    if 'env' not in metadata:
        return

    _log_raise_if(
        not isinstance(metadata["env"], TasksConfigBaseMapping),
        "env, if supplied, must be a key: value mapping",
        extra=dict(**ld),
        exception_kls=DAGMisconfigured
    )
    for k, v in metadata['env'].items():
        _log_raise_if(
            not isinstance(k, (str, unicode)),
            "invalid key.  expected string", extra=dict(key=k, **ld),
            exception_kls=DAGMisconfigured)
        _log_raise_if(
            not isinstance(k, (str, unicode)),
            "invalid value.  expected string", extra=dict(value=v, **ld),
            exception_kls=DAGMisconfigured)


def validate_env_from_os(app_name, metadata, dg, tasks_conf, ld):
    if 'env_from_os' not in metadata:
        return

    _log_raise_if(
        not isinstance(metadata["env_from_os"], TasksConfigBaseSequence),
        "env_from_os, if supplied, must be sequence of environment variables",
        extra=dict(**ld),
        exception_kls=DAGMisconfigured
    )
    for key in metadata["env_from_os"]:
        _log_raise_if(
            not os.environ.get(key),
            "key not in os environment but expected it to be there",
            extra=dict(key=key, **ld),
            exception_kls=DAGMisconfigured)


def validate_uris(app_name, metadata, dg, tasks_conf, ld):
    key = "uris"
    if key not in metadata:
        return
    msg = ("%s, if supplied, must be a list of hadoop-compatible filepaths"
           % key)
    _log_raise_if(
        not isinstance(metadata[key], TasksConfigBaseSequence),
        msg, extra=dict(**ld), exception_kls=DAGMisconfigured)
    _log_raise_if(
        not all(isinstance(x, (unicode, str)) for x in metadata[key]),
        msg, extra=dict(**ld), exception_kls=DAGMisconfigured)


def validate_dag(dg, tasks_conf):
    assert nx.algorithms.dag.is_directed_acyclic_graph(dg)

    for app_name1, metadata in tasks_conf.items():
        ld = dict(app_name=app_name1)
        validate_depends_on(app_name1, metadata, dg, tasks_conf, ld)
        validate_if_or(app_name1, metadata, dg, tasks_conf, ld)
        validate_job_type(app_name1, metadata, dg, tasks_conf, ld)
        validate_bash_opts(app_name1, metadata, dg, tasks_conf, ld)
        validate_spark_conf(app_name1, metadata, dg, tasks_conf, ld)
        validate_env(app_name1, metadata, dg, tasks_conf, ld)
        validate_env_from_os(app_name1, metadata, dg, tasks_conf, ld)
        validate_uris(app_name1, metadata, dg, tasks_conf, ld)


def visualize_dag(dg=None, plot=True, write_dot=False, delete_plot=True):
    """For interactive use"""
    if not dg:
        dg = build_dag_cached()
    tmpf = tempfile.mkstemp(suffix='.dot')[1]
    try:
        if plot:
            nx.draw_graphviz(dg, prog='dot')
        if write_dot:
            nx.write_dot(dg, '{0}'.format(tmpf))
            os.popen(
                'dot {0} -Tpng > {0}.png ; open {0}.png ; sleep 5'
                .format(tmpf))
    finally:
        if delete_plot:
            if os.path.exists(tmpf):
                os.remove(tmpf)
            if os.path.exists(tmpf + '.png'):
                os.remove(tmpf + '.png')


def _add_nodes(tasks_conf, dg):
    """Add nodes to a networkx graph
    `tasks_conf` a subclass of TasksConfigBaseMapping
    `dg` a networkx.MultiDiGraph instance (or something compatible)
    """
    for app_name, _attr_conf in tasks_conf.items():
        attr_dict = dict(_attr_conf)
        dg.add_node(app_name, attr_dict)
        deps = attr_dict.get('depends_on')
        if deps:
            yield (app_name, deps)


def _add_edges(dg, app_name, dep_name, dep_grp, log_details):
    """Add edge(s) to a networkx graph instance

    `dg` is an instance of a nx.MultiDiGraph, which means we can have
        multiple edges between two nodes
    `dep_name` (str) - the name of a dependency group
    `dep_grp` (obj) - dependency group data.  Subclass of
        TasksConfigBaseMapping.  An example of what this may look like is:
            dep_grp = {
                "app_name": ["test_app"],
                "date": [20140601],
                "client_id": [123, 140, 150],
                ...
            }
    """
    parent = dep_grp['app_name']
    if isinstance(parent, (unicode, str)):
        dg.add_edge(parent, app_name, key=dep_name, label=dep_name)
    elif isinstance(parent, TasksConfigBaseSequence):
        for _parent in parent:
            dg.add_edge(_parent, app_name, key=dep_name, label=dep_name)
    else:
        _log_raise((
            "Unrecognized type:"
            " I found a child that doesn't properly define parents."
            " Children should have the parent app_name"
            " define a string or sequence"
            " of strings that represent the child's parents."),
            dict(parent_app_name=parent, parent_app_name_type=type(parent),
                 **log_details),
            exception_kls=DAGMisconfigured)


def _build_dict_deps(dg, app_name, deps):
    """Build edges between dependent nodes

    `dg` (nx.MultiDiGraph instance) - the Tasks configuration as a graph
    `app_name` (str) - the name of a scheduled application
    `deps` (obj) - the dependencies for given `app_name`.  Should be a subclass
        of TasksConfigBaseMapping
    """
    log_details = dict(app_name=app_name, key='depends_on', deps=dict(deps))
    if "app_name" in deps:
        _add_edges(
            dg, app_name=app_name, dep_name=DEPENDENCY_GROUP_DEFAULT_NAME,
            dep_grp=deps, log_details=log_details)
    else:
        for dep_name, dep_grp in deps.items():
            if isinstance(dep_grp, TasksConfigBaseMapping):
                _add_edges(
                    dg=dg, app_name=app_name, dep_name=dep_name,
                    dep_grp=dep_grp, log_details=log_details)
            elif isinstance(dep_grp, TasksConfigBaseSequence):
                for _dep_grp in dep_grp:
                    _add_edges(
                        dg=dg, app_name=app_name, dep_name=dep_name,
                        dep_grp=_dep_grp, log_details=log_details)
            else:
                _log_raise(
                    "Unrecognized dependency.  Expected a list or dict",
                    dict(dep_name=dep_name, dep_grp=dep_grp, **log_details),
                    exception_kls=DAGMisconfigured)


@util.cached
def build_dag_cached(*args, **kwargs):
    return build_dag(*args, **kwargs)


def build_dag(tasks_conf=None, validate=True):
    return _build_dag(tasks_conf, validate)


def _build_dag(tasks_conf, validate):
    if tasks_conf is None:
        tasks_conf = node.get_tasks_config()
    dg = nx.MultiDiGraph()
    for app_name, deps in _add_nodes(tasks_conf, dg):
        _build_dict_deps(
            dg=dg, app_name=app_name, deps=deps)

    if validate:
        validate_dag(dg, tasks_conf)
    return dg
