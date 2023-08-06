# proc: Simple interface to Linux process information.
#
# Author: Peter Odding <peter@peterodding.com>
# Last Change: March 29, 2015
# URL: https://proc.readthedocs.org

"""
The :py:mod:`proc.tree` module builds tree data structures based on process trees.

This module builds on top of :py:mod:`proc.core` to provide a tree data
structure that mirrors the process tree implied by the process information
reported by :py:func:`~proc.core.find_processes()` (specifically the
:py:attr:`~proc.core.Process.ppid` attributes). Here's a simple example that
shows how much code you need to find the `cron daemon`_, it's workers and the
children of those workers (cron jobs):

>>> from proc.tree import get_process_tree
>>> init = get_process_tree()
>>> cron_daemon = init.find(exe_name='cron')
>>> cron_workers = cron_daemon.children
>>> cron_jobs = cron_daemon.grandchildren

After the above five lines the ``cron_jobs`` variable will contain a collection
of :py:class:`ProcessNode` objects, one for each cron job that ``cron`` is
executing. The :py:mod:`proc.cron` module contains a more full fledged example
of using the :py:mod:`proc.tree` module.

.. _cron daemon: http://en.wikipedia.org/wiki/Cron
.. _flatten a list of lists: http://stackoverflow.com/questions/406121/flattening-a-shallow-list-in-python
"""

# Standard library modules.
import logging

# Modules provided by our package.
from proc.core import find_processes, Process

# Initialize a logger.
logger = logging.getLogger(__name__)


def get_process_tree():
    """
    Construct a process tree from the result of :py:func:`~proc.core.find_processes()`.

    :returns: A :py:class:`ProcessNode` object that forms the root node of the
              constructed tree (this node represents init_).

    .. _init: http://en.wikipedia.org/wiki/init
    """
    mapping = dict((p.pid, p) for p in find_processes(obj_type=ProcessNode))
    for obj in mapping.values():
        if obj.ppid != 0:
            obj.parent = mapping[obj.ppid]
            obj.parent.children.append(obj)
    return mapping[1]


class ProcessNode(Process):

    """
    Process information including relationships that model the process tree.

    :py:class:`ProcessNode` is a subclass of :py:class:`~proc.core.Process`
    that adds relationships between processes to model the process tree as a
    tree data structure. This makes it easier and more intuitive to extract
    information from the process tree by analyzing the relationships:

    - To construct a tree you use :py:func:`get_process_tree()`. This function
      connects all of the nodes in the tree before returning the root node
      (this node represents init_).

    - To navigate the tree you can use the :py:attr:`parent`,
      :py:attr:`children`, :py:attr:`grandchildren` and :py:attr:`descendants`
      properties.

    - If you're looking for specific descendant processes consider using
      :py:func:`find()` or :py:func:`find_all()`.

    .. py:attribute:: parent

       The :py:class:`ProcessNode` object of the parent process of this process
       (``None`` when the process doesn't have a parent). Based on the
       :py:attr:`~proc.core.Process.ppid` attribute.

    .. py:attribute:: children

       A list of :py:class:`ProcessNode` objects with the children of this
       process.
    """

    # Prevent unnecessary creation of instance dictionaries (helps to keep
    # memory requirements low).
    __slots__ = ('parent', 'children')

    def __init__(self, *args, **kw):
        """
        Construct a process node.

        This constructor accepts the same arguments as the
        :py:class:`~proc.core.Process` constructor.
        """
        super(ProcessNode, self).__init__(*args, **kw)
        self.parent = None
        self.children = []

    @property
    def grandchildren(self):
        """
        Find the grandchildren of this process.

        :returns: A generator of :py:class:`ProcessNode` objects.
        """
        for child in self.children:
            for grandchild in child.children:
                yield grandchild

    @property
    def descendants(self):
        """
        Find the descendants of this process.

        :returns: A generator of :py:class:`ProcessNode` objects.
        """
        stack = list(self.children)
        while stack:
            process = stack.pop(0)
            stack.extend(process.children)
            yield process

    def find(self, *args, **kw):
        """
        Find the first child process of this process that matches one or more criteria.

        This method accepts the same parameters as the :py:func:`find_all()` method.

        :returns: The :py:class:`ProcessNode` object of the first process that
                  matches the given criteria or ``None`` if no processes match.
        """
        for process in self.find_all(*args, **kw):
            return process

    def find_all(self, pid=None, exe_name=None, exe_path=None, recursive=False):
        """
        Find child processes of this process that match one or more criteria.

        :param pid: If this parameter is given, only processes with the given
                    :py:attr:`~proc.core.Process.pid` will be returned.
        :param exe_name: If this parameter is given, only processes with the
                         given :py:attr:`~proc.core.Process.exe_name` will be
                         returned.
        :param exe_path: If this parameter is given, only processes with the
                         given :py:attr:`~proc.core.Process.exe_path` will be
                         returned.
        :param recursive: If this is ``True`` (not the default) all processes
                          in :py:attr:`descendants` will be searched, otherwise
                          only the processes in :py:attr:`children` are
                          searched (the default).
        :returns: A generator of :py:class:`ProcessNode` objects.
        """
        for process in (self.descendants if recursive else self.children):
            if ((pid is None or process.pid == pid)
                    and (exe_name is None or process.exe_name == exe_name)
                    and (exe_path is None or process.exe_path == exe_path)):
                yield process
