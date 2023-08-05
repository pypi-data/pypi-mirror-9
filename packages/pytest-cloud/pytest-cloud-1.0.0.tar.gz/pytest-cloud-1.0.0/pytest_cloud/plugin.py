"""Distributed tests planner plugin for pytest testing framework.

Provides an easy way of running tests amoung several test nodes (slaves).
"""
from __future__ import division
import itertools
import math

import execnet
import six


class SplinterXdistPlugin(object):

    """Plugin class to defer pytest-xdist hook handler."""

    def pytest_configure_node(self, node):
        """Configure node information before it gets instantiated.

        Acivate the virtual env, so the node is able to import dependencies.
        """
        virtualenv_path = node.config.option.cloud_virtualenv_path
        node.gateway.remote_exec(activate_env, virtualenv_path=virtualenv_path).waitclose()


def pytest_configure(config):
    """Register pytest-cloud's deferred plugin."""
    if (
        getattr(config, 'slaveinput', {}).get('slaveid', 'local') == 'local'
            and config.option.cloud_nodes
            and config.pluginmanager.getplugin('xdist')):
        config.pluginmanager.register(SplinterXdistPlugin())


def pytest_addoption(parser):  # pragma: no cover
    """Pytest hook to add custom command line option(s)."""
    group = parser.getgroup("cloud", "distributed tests scheduler")
    group.addoption(
        "--cloud-node",
        help="test node to use for distributed testing", type='string', action="append",
        dest='cloud_nodes', metavar="USER@HOST", default=[])
    group.addoption(
        "--cloud-virtualenv-path",
        help="relative path to the virtualenv to be used on the remote test nodes.", type='string', action="store",
        dest='cloud_virtualenv_path', metavar="PATH", default=None)
    group.addoption(
        "--cloud-mem-per-process",
        help="amount of memory roughly needed for test process, in megabytes", type='int', action="store",
        dest='cloud_mem_per_process', metavar="NUMBER", default=None)
    group.addoption(
        "--cloud-max-processes",
        help="maximum number of processes per test node", type='int', action="store",
        dest='cloud_max_processes', metavar="NUMBER", default=None)


def pytest_cmdline_main(config):
    """Custom cmd line manipulation for pytest-cloud."""
    check_options(config)


def activate_env(channel, virtualenv_path):
    """Activate virtual environment.

    Executed on the remote side.
    """
    import os.path
    if virtualenv_path:
        activate_script = os.path.abspath(os.path.normpath(os.path.join(virtualenv_path, 'bin', 'activate_this.py')))
        if six.PY3:
            exec(compile(open(activate_script).read()))
        else:
            execfile(activate_script, {'__file__': activate_script})  # NOQA


def get_node_capabilities(channel):
    """Get node capabilities.

    Executed on the remote side.
    """
    import psutil
    memory = psutil.virtual_memory()
    caps = dict(cpu_count=psutil.cpu_count(), virtual_memory=dict(free=memory.free, total=memory.total))
    channel.send(caps)


def get_node_specs(node, host, caps, mem_per_process=None, max_processes=None):
    """Get single node specs."""
    count = min(max_processes or six.MAXSIZE, caps['cpu_count'])
    if mem_per_process:
        count = min(int(math.floor(caps['virtual_memory']['free'] / mem_per_process)), count)
    return (
        '1*ssh={node}//id={host}:{index}'.format(
            count=count,
            node=node,
            host=host,
            index=index)
        for index in range(count))


def get_nodes_specs(nodes, virtualenv_path=None, mem_per_process=None, max_processes=None):
    """Get nodes specs."""
    group = execnet.Group()
    if virtualenv_path:
        rsync = execnet.RSync(virtualenv_path)
    node_specs = []
    node_caps = {}
    for node in nodes:
        host = node.split('@')[1] if '@' in node else node
        spec = 'ssh={node}//id={host}'.format(
            node=node,
            host=host)
        try:
            gw = group.makegateway(spec)
        except Exception:
            continue
        if virtualenv_path:
            rsync.add_target(gw, virtualenv_path)
        node_specs.append((node, host))
    if virtualenv_path:
        rsync.send()
    try:
        group.remote_exec(activate_env, virtualenv_path=virtualenv_path).waitclose()
        multi_channel = group.remote_exec(get_node_capabilities)
        try:
            caps = multi_channel.receive_each(True)
            for ch, cap in caps:
                node_caps[ch.gateway.id] = cap
        finally:
            multi_channel.waitclose()
        return list(itertools.chain.from_iterable(
            get_node_specs(node, hst, node_caps[hst], mem_per_process=mem_per_process, max_processes=max_processes)
            for node, hst in node_specs)
        )
    finally:
        group.terminate()


def check_options(config):
    """Process options to manipulate (produce other options) important for pytest-cloud."""
    if getattr(config, 'slaveinput', {}).get('slaveid', 'local') == 'local' and config.option.cloud_nodes:
        mem_per_process = config.option.cloud_mem_per_process
        if mem_per_process:
            mem_per_process = mem_per_process * 1024 * 1024
        node_specs = get_nodes_specs(
            config.option.cloud_nodes,
            virtualenv_path=config.option.cloud_virtualenv_path,
            max_processes=config.option.cloud_max_processes,
            mem_per_process=mem_per_process)
        config.option.tx += node_specs
        config.option.dist = 'load'
