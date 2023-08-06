# proc: Simple interface to Linux process information.
#
# Author: Peter Odding <peter@peterodding.com>
# Last Change: March 30, 2015
# URL: https://proc.readthedocs.org

"""
The :py:mod:`proc.core` module contains the core functionality of the `proc` package.

This module provides a simple interface to the process information available in
``/proc``. It takes care of the text parsing that's necessary to gather process
information from ``/proc`` but it doesn't do much more than that. The functions
in this module produce :py:class:`Process` objects.

If you're just getting started with this module I suggest you jump to the
documentation of :py:func:`find_processes()` because this function provides the
"top level entry point" into most of the functionality provided by this
module.
"""

# Standard library modules.
import logging
import os
import signal
import time

# External dependencies.
from cached_property import cached_property
from executor import which, quote

# Initialize a logger.
logger = logging.getLogger(__name__)

# Global counters to track the number of detected race conditions. This is only
# useful for the test suite, because I want the test suite to create race
# conditions and verify that they are properly handled.
num_race_conditions = dict(stat=0, cmdline=0)


class Process(object):

    """
    Process information based on ``/proc/[pid]/stat`` and similar files.

    :py:class:`Process` objects are constructed using
    :py:func:`find_processes()` and :py:func:`Process.from_path()`. You
    shouldn't be using the :py:class:`Process` constructor directly unless you
    know what you're doing.

    **Comparison to official /proc documentation**

    Quite a few of the instance properties of this class are based on (and
    named after) fields extracted from ``/proc/[pid]/stat``. The following
    table lists these properties and the *zero based index* of the
    corresponding field in ``/proc/[pid]/stat``:

    ====================  =====
    Property              Index
    ====================  =====
    :py:attr:`pid`            0
    :py:attr:`comm`           1
    :py:attr:`state`          2
    :py:attr:`ppid`           3
    :py:attr:`pgrp`           4
    :py:attr:`session`        5
    :py:attr:`starttime`     21
    :py:attr:`vsize`         22
    :py:attr:`rss`           23
    ====================  =====

    As you can see from the indexes in the table above quite a few fields from
    ``/proc/[pid]/stat`` are not currently exposed by :py:class:`Process`
    objects. In fact ``/proc/[pid]/stat`` contains 44 fields! Some of these
    fields are no longer maintained by the Linux kernel and remain only for
    backwards compatibility (so exposing them is not useful) while other fields
    are not exposed because I didn't consider them relevant to a Python API. If
    your use case requires fields that are not yet exposed, feel free to
    suggest additional fields to expose in the issue tracker.

    The documentation on the properties of this class quotes from and
    paraphrases the text in `man 5 proc`_ so if things are unclear and you're
    feeling up to it, dive into the huge manual page for clarifications :-).

    .. _man 5 proc: http://linux.die.net/man/5/proc
    """

    # Prevent unnecessary creation of instance dictionaries (helps to keep
    # memory requirements low).
    __slots__ = ('proc_tree', 'stat_fields', '_cache')

    @classmethod
    def from_path(cls, directory):
        """
        Construct a process information object from a numerical subdirectory of ``/proc``.

        :param directory: The absolute pathname of the numerical subdirectory
                          of ``/proc`` to get process information from (a
                          string).
        :returns: A process information object or ``None`` (in case the process
                  ends before its information can be read).

        This class method is used by :py:func:`find_processes()` to construct
        :py:class:`Process` objects. It's exposed as a separate method because
        it may sometimes be useful to call directly. For example:

        >>> from proc.core import Process
        >>> Process.from_path('/proc/self')
        Process(pid=1468,
                comm='python',
                state='R',
                ppid=21982,
                pgrp=1468,
                session=21982,
                vsize=40431616,
                rss=8212480,
                cmdline=['python'],
                exe='/home/peter/.virtualenvs/proc/bin/python')
        """
        fields = parse_process_status(directory)
        if fields:
            return cls(directory, fields)

    @classmethod
    def from_pid(cls, pid):
        """
        Construct a process information object based on a process ID.

        :param pid: The process ID (an integer).
        :returns: A process information object or ``None`` (in case the process
                  ends before its information can be read).
        """
        directory = os.path.join('/proc', str(pid))
        fields = parse_process_status(directory)
        if fields:
            return cls(directory, fields)

    def __init__(self, proc_tree, stat_fields):
        """
        Construct a process information object.

        :param proc_tree: The absolute pathname of the numerical subdirectory
                          of ``/proc`` on which the process information is
                          based (a string).
        :param stat_fields: The tokenized fields from ``/proc/[pid]/stat`` (a
                            list of strings).
        """
        self.proc_tree = proc_tree
        self.stat_fields = stat_fields

    def __repr__(self):
        """
        Create a human readable representation of a process information object.

        :returns: A string containing what looks like a :py:class:`Process`
                  constructor, but showing public properties instead of
                  internal properties.
        """
        fields = []
        for name, optional in (('pid', False),
                               ('comm', False),
                               ('state', False),
                               ('ppid', True),
                               ('pgrp', False),
                               ('session', False),
                               ('vsize', False),
                               ('rss', False),
                               ('cmdline', True),
                               ('exe', True)):
            value = getattr(self, name)
            if not (optional and not value):
                fields.append("%s=%r" % (name, value))
        return "%s(%s)" % (self.__class__.__name__, ", ".join(fields))

    @cached_property
    def pid(self):
        """
        The process ID (an integer).

        **Availability:** This property is parsed from the contents of
        ``/proc/[pid]/stat`` and is always available.
        """
        return int(self.stat_fields[0])

    @cached_property
    def comm(self):
        """
        The filename of the executable.

        **Availability:** This property is parsed from the contents of
        ``/proc/[pid]/stat`` and is always available.

        The filename is not enclosed in parentheses like it is in
        ``/proc/[pid]/stat`` because the parentheses are an implementation
        detail of the encoding of ``/proc/[pid]/stat`` and the whole point of
        :py:mod:`proc.core` is to hide ugly encoding details like this :-).

        .. note:: This field can be truncated by the Linux kernel so strictly
                  speaking you can't rely on this field unless you know that
                  the executables you're interested in have short names. Here's
                  an example of what I'm talking about:

                  >>> from proc.core import find_processes
                  >>> next(p for p in find_processes() if p.comm.startswith('console'))
                  Process(pid=2753,
                          comm='console-kit-dae',
                          state='S',
                          ppid=1,
                          pgrp=1632,
                          session=1632,
                          vsize=2144198656,
                          rss=733184,
                          cmdline=['/usr/sbin/console-kit-daemon', '--no-daemon'])

                  As you can see in the example above the executable name
                  ``console-kit-daemon`` is truncated to ``console-kit-dae``.
                  If you need a reliable way to find the executable name
                  consider using the :py:attr:`cmdline` and/or :py:attr:`exe`
                  properties.
        """
        return self.stat_fields[1]

    @cached_property
    def state(self):
        """
        A single uppercase character describing the state of the process (a string).

        Quoting from `man 5 proc`_:

         *One character from the string "RSDZTW" where R is running, S is
         sleeping in an interruptible wait, D is waiting in uninterruptible
         disk sleep, Z is zombie_, T is traced or stopped (on a signal), and W
         is paging.*

        **Availability:** This property is parsed from the contents of
        ``/proc/[pid]/stat`` and is always available.

        .. _zombie: http://en.wikipedia.org/wiki/Zombie_process
        """
        return self.stat_fields[2]

    @cached_property
    def ppid(self):
        """
        The process ID of the parent process (an integer).

        **Availability:** This property is parsed from the contents of
        ``/proc/[pid]/stat`` and is always available.

        This field is zero when the process doesn't have a parent process (same
        as in ``/proc/[pid]/stat``). Because Python treats the integer ``0`` as
        ``False`` this field can be used as follows to find processes without a
        parent process:

        >>> from proc.core import find_processes
        >>> pprint([p for p in find_processes() if not p.ppid])
        [Process(pid=1, comm='init', state='S', pgrp=1, session=1, vsize=25174016, rss=1667072, cmdline=['/sbin/init']),
         Process(pid=2, comm='kthreadd', state='S', pgrp=0, session=0, vsize=0, rss=0)]
        """
        return int(self.stat_fields[3])

    @cached_property
    def pgrp(self):
        """
        The process group ID of the process (an integer).

        **Availability:** This property is parsed from the contents of
        ``/proc/[pid]/stat`` and is always available.
        """
        return int(self.stat_fields[4])

    @cached_property
    def session(self):
        """
        The session ID of the process (an integer).

        **Availability:** This property is parsed from the contents of
        ``/proc/[pid]/stat`` and is always available.
        """
        return int(self.stat_fields[5])

    @cached_property
    def starttime(self):
        """
        The time at which the process was started (a float).

        Paraphrasing from `man 5 proc`_:

         *The time the process started after system boot. In kernels before
         Linux 2.6, this value was expressed in jiffies. Since Linux 2.6, the
         value is expressed in clock ticks.*

        This property translates *clock ticks* to *seconds* by dividing the
        value extracted from ``/proc/[pid]/stat`` with the result of:

        .. code-block:: python

           os.sysconf('SC_CLK_TCK')

        After the conversion to seconds the system's uptime is used to
        determine the absolute start time of the process (the number of seconds
        since the Unix epoch_).

        See also the :py:attr:`runtime` property.

        **Availability:** This property is calculated from the contents of
        ``/proc/[pid]/stat`` and ``/proc/uptime`` and is always available.

        .. _epoch: http://en.wikipedia.org/wiki/Unix_time
        """
        with open('/proc/uptime') as handle:
            contents = handle.read()
            fields = contents.split()
            system_uptime = float(fields[0])
        system_boot = time.time() - system_uptime
        ticks_after_boot = int(self.stat_fields[21])
        seconds_after_boot = ticks_after_boot / float(os.sysconf('SC_CLK_TCK'))
        return system_boot + seconds_after_boot

    @property
    def runtime(self):
        """
        The time in seconds since the process started (a float).

        This property is calculated based on :py:attr:`starttime` every time
        it's requested (so it will always be up to date).

        .. warning:: The runtime will not stop growing when the process ends
                     because doing so would require a background thread just to
                     monitor when the process ends... This is an unfortunate
                     side effect of the architecture of ``/proc`` -- processes
                     disappear from ``/proc`` the moment they end so the
                     information about when the process ended is lost!
        """
        return max(0, time.time() - self.starttime)

    @cached_property
    def vsize(self):
        """
        The virtual memory size of the process in bytes (an integer).

        **Availability:** This property is parsed from the contents of
        ``/proc/[pid]/stat`` and is always available.
        """
        return int(self.stat_fields[22])

    @cached_property
    def rss(self):
        """
        The resident set size of the process *in bytes* (an integer).

        Quoting from `man 5 proc`_:

         *Number of pages the process has in real memory. This is just the
         pages which count toward text, data, or stack space. This does not
         include pages which have not been demand-loaded in, or which are
         swapped out.*

        This property translates *pages* to *bytes* by multiplying the value
        extracted from ``/proc/[pid]/stat`` with the result of:

        .. code-block:: python

           os.sysconf('SC_PAGESIZE')

        **Availability:** This property is parsed from the contents of
        ``/proc/[pid]/stat`` and is always available.
        """
        return int(self.stat_fields[23]) * os.sysconf('SC_PAGESIZE')

    @cached_property
    def cmdline(self):
        """
        The complete command line for the process (a list of strings).

        **Availability:**

        - This property is parsed from the contents of ``/proc/[pid]/cmdline``
          the first time it is referenced, after that its value is cached so it
          will always be available (although by then it may no longer be up to
          date because processes can change their command line at runtime on
          Linux).

        - If this property is first referenced after the process turns into a
          zombie_ or the process ends then it's too late to read the contents
          of ``/proc/[pid]/cmdline`` and an empty list is returned.

        .. note:: In Linux it is possible for a process to change its command
                  line after it has started. Modern daemons tend to do this in
                  order to communicate their status. Here's an example of how
                  the Nginx web server uses this feature:

                  >>> from proc.core import find_processes
                  >>> from pprint import pprint
                  >>> pprint([(p.pid, p.cmdline) for p in find_processes() if p.comm == 'nginx'])
                  [(2662, ['nginx: master process /usr/sbin/nginx']),
                   (25100, ['nginx: worker process']),
                   (25101, ['nginx: worker process']),
                   (25102, ['nginx: worker process']),
                   (25103, ['nginx: worker process'])]

                  What this means is that (depending on the behavior of the
                  process in question) it may be impossible to determine the
                  effective command line that was used to start a process. If
                  you're just interested in the pathname of the executable
                  consider using the :py:attr:`exe` property instead:

                  >>> from proc.core import find_processes
                  >>> from pprint import pprint
                  >>> pprint([(p.pid, p.exe) for p in find_processes() if p.comm == 'nginx'])
                  [(2662, '/usr/sbin/nginx'),
                   (25100, '/usr/sbin/nginx'),
                   (25101, '/usr/sbin/nginx'),
                   (25102, '/usr/sbin/nginx'),
                   (25103, '/usr/sbin/nginx')]
        """
        return parse_process_cmdline(self.proc_tree)

    @cached_property
    def exe(self):
        """
        The actual pathname of the executed command (a string).

        **Availability:**

        - This property is constructed by dereferencing the symbolic link
          ``/proc/[pid]/exe`` the first time the property is referenced, after
          that its value is cached so it will always be available.

        - If this property is referenced after the process has ended then it's
          too late to dereference the symbolic link and ``None`` is returned.

        - If an exception is encountered while dereferencing the symbolic link
          (for example because you don't have permission to dereference the
          symbolic link) the exception is swallowed and an empty string is
          returned.
        """
        try:
            return os.readlink(os.path.join(self.proc_tree, 'exe'))
        except Exception:
            return ''

    @cached_property
    def exe_path(self):
        """
        The absolute pathname of the executable (a string).

        It can be tricky to reliably determine the pathname of the executable
        of an arbitrary process and this property tries to make it easier. Its
        value is based on the first of the following methods that works:

        1. If :py:attr:`exe` is available then this pathname is returned.

           - Pro: This method provides the most reliable way to determine the
             absolute pathname of the executed command because (as far as I
             know) it always provides an absolute pathname.
           - Con: This method can fail because you don't have permission to
             dereference the ``/proc/[pid]/exe`` symbolic link.

        2. If the first string in :py:attr:`cmdline` contains the absolute
           pathname of an executable file then this pathname is returned.

           - Pro: This method doesn't require the same permissions that method
             one requires.
           - Con: This method can fail because a process has changed its own
             command line (after it was started) or because the first string in
             the command line isn't an absolute pathname.

        3. If both of the methods above fail an empty string is returned.
        """
        if self.exe:
            return self.exe
        if self.cmdline:
            name = self.cmdline[0]
            if os.path.isabs(name) and os.access(name, os.X_OK):
                return name
        return ''

    @cached_property
    def exe_name(self):
        """
        The base name of the executable (a string).

        It can be tricky to reliably determine the name of the executable of an
        arbitrary process and this property tries to make it easier. Its value
        is based on the first of the following methods that works:

        1. If :py:attr:`exe_path` is available then the base name of this
           pathname is returned.

           - Pro: When the :py:attr:`exe_path` property is available it is
             fairly reliable.
           - Con: The :py:attr:`exe_path` property can be unavailable (refer to
             its documentation for details).

        2. If the first string in :py:attr:`cmdline` contains a name that is
           available on the executable search path (``$PATH``) then this name
           is returned.

           - Pro: As long as :py:attr:`cmdline` contains the name of an
             executable available on the ``$PATH`` this method works.
           - Con: This method can fail because a process has changed its own
             command line (after it was started).

        3. If both of the methods above fail :py:attr:`comm` is returned.

           - Pro: The :py:attr:`comm` field is always available.
           - Con: The :py:attr:`comm` field may be truncated.
        """
        if self.exe_path:
            return os.path.basename(self.exe_path)
        if self.cmdline:
            name = self.cmdline[0]
            if os.path.basename(name) == name and which(name):
                return name
        return self.comm

    @property
    def is_alive(self):
        """
        ``True`` if the process is still alive, ``False`` otherwise.

        This property reads the ``/proc/[pid]/stat`` file each time the
        property is referenced to make sure that the process still exists and
        has not turned into a zombie_ process.

        See also :py:func:`stop()`, :py:func:`cont()`, :py:func:`terminate()`
        and :py:func:`kill()`.
        """
        stat_fields = parse_process_status(self.proc_tree, silent=True)
        return bool(stat_fields and stat_fields[2] != 'Z')

    def stop(self):
        """
        Stop a process for later resumption.

        This sends a SIGSTOP_ signal to the process. This signal cannot be
        intercepted or ignored.

        See also :py:attr:`is_alive`, :py:func:`cont()`, :py:func:`terminate()`
        and :py:func:`kill()`.

        .. _SIGSTOP: http://en.wikipedia.org/wiki/Unix_signal#SIGSTOP
        """
        logger.info("Suspending process id %i (%s) ..", self.pid, quote(self.cmdline))
        os.kill(self.pid, signal.SIGSTOP)

    def cont(self):
        """
        Continue (restart) a process that was previously paused using :py:func:`stop()`.

        This sends a SIGCONT_ signal to the process. This signal cannot be
        intercepted or ignored.

        See also :py:attr:`is_alive`, :py:func:`stop()`, :py:func:`terminate()`
        and :py:func:`kill()`.

        .. _SIGCONT: http://en.wikipedia.org/wiki/Unix_signal#SIGCONT
        """
        logger.info("Resuming process id %i (%s) ..", self.pid, quote(self.cmdline))
        os.kill(self.pid, signal.SIGCONT)

    def terminate(self):
        """
        Request the (graceful) termination of the process.

        This sends a SIGTERM_ signal to the process. Processes are allowed to
        intercept this signal to allow for graceful termination (releasing
        resources, saving state).

        See also :py:attr:`is_alive`, :py:func:`stop()`, :py:func:`cont()` and
        :py:func:`kill()`.

        .. _SIGTERM: http://en.wikipedia.org/wiki/Unix_signal#SIGTERM
        """
        logger.info("Gracefully terminating process id %i (%s) ..", self.pid, quote(self.cmdline))
        os.kill(self.pid, signal.SIGTERM)

    def kill(self):
        """
        Immediately (non gracefully) terminate the process.

        This sends a SIGKILL_ signal to the process. This signal cannot be
        intercepted or ignored.

        See also :py:attr:`is_alive`, :py:func:`stop()`, :py:func:`cont()` and
        :py:func:`terminate()`.

        .. _SIGKILL: http://en.wikipedia.org/wiki/Unix_signal#SIGKILL
        """
        logger.info("Forcefully terminating process id %i (%s) ..", self.pid, quote(self.cmdline))
        os.kill(self.pid, signal.SIGKILL)


def find_processes(obj_type=Process):
    """
    Scan the numerical subdirectories of ``/proc`` for process information.

    :param obj_type: The type of process objects to construct (expected to be
                     :py:class:`Process` or a subclass of :py:class:`Process`).
    :returns: A generator of :py:class:`Process` objects.
    """
    if not issubclass(obj_type, Process):
        raise TypeError("Custom process types should inherit from proc.core.Process!")
    root = '/proc'
    num_processes = 0
    logger.debug("Scanning for process information in %r ..", root)
    for entry in os.listdir(root):
        if entry.isdigit():
            process = obj_type.from_path(os.path.join(root, entry))
            if process:
                num_processes += 1
                yield process
    logger.debug("Finished scanning %r, found %i processes.", root, num_processes)


def sorted_by_pid(processes):
    """
    Sort the given processes by their process ID.

    :param processes: An iterable of :py:class:`Process` objects.
    :returns: A list of :py:class:`Process` objects sorted by their process ID.
    """
    return sorted(processes, key=lambda p: p.pid)


def parse_process_status(directory, silent=False):
    """
    Read and tokenize a ``/proc/[pid]/stat`` file.

    :param directory: The absolute pathname of the numerical subdirectory of
                      ``/proc`` to get process information from (a string).
    :returns: A list of strings containing the tokenized fields or ``None`` if
              the ``/proc/[pid]/stat`` file disappears before it can be read
              (in this case a warning is logged).
    """
    # Read the /proc/[pid]/stat file. This can raise an exception if the
    # process ends before we can open and read the file (a race condition). In
    # this case we'll return None to our caller.
    pathname = os.path.join(directory, 'stat')
    try:
        with open(pathname) as handle:
            contents = handle.read()
        # If a process ends after we've successfully opened the corresponding
        # /proc/[pid]/stat file but before we've read the file contents I'm not
        # 100% sure if a nonempty read is guaranteed, so we'll just make sure
        # we actually got a nonempty read (I'd rather err on the side of
        # caution :-).
        assert contents
    except Exception:
        num_race_conditions['stat'] += 1
        if not silent:
            logger.warning("Failed to read process status, most likely due to a race condition! (%s)", pathname)
        return None
    # This comment is here to justify the gymnastics with str.partition()
    # and str.rpartition() below:
    #
    # The second field in /proc/[pid]/stat (called `comm' in `man 5 proc')
    # is the executable name. It's enclosed in parentheses and may contain
    # spaces. Due to the very sparse documentation about this _obscure_
    # encoding I got curious and experimented a bit:
    #
    # Nothing prevents an executable name from containing parentheses and
    # because these are just arbitrary characters without any meaning they
    # don't need to be balanced. When such an executable name is embedded in
    # /proc/[pid]/stat no further encoding is applied, you'll just get
    # something like '((python))'.
    #
    # Fortunately the `comm' field is the only field that can contain
    # arbitrary text, so if you take the text between the left most and
    # right most parenthesis in /proc/[pid]/stat you'll end up with the
    # correct answer!
    before_comm, _, remainder = contents.partition('(')
    comm, _, after_comm = remainder.rpartition(')')
    # Combine the tokenized fields into a list of strings. All of the
    # fields except `comm' are integers or a single alphabetic character
    # (the state field) so using str.split() is okay here.
    fields = before_comm.split()
    fields.append(comm)
    fields.extend(after_comm.split())
    return fields


def parse_process_cmdline(directory):
    """
    Read and tokenize a ``/proc/[pid]/cmdline`` file.

    :param directory: The absolute pathname of the numerical subdirectory of
                      ``/proc`` to get process information from (a string).
    :returns: A list of strings containing the tokenized command line. If the
              ``/proc/[pid]/cmdline`` file disappears before it can be read an
              empty list is returned (in this case a warning is logged).
    """
    # Read the /proc/[pid]/cmdline file. This can raise an exception if the
    # process ends before we can open and read the file (a race condition). In
    # this case we'll return None to our caller.
    pathname = os.path.join(directory, 'cmdline')
    try:
        with open(pathname) as handle:
            contents = handle.read()
    except Exception:
        num_race_conditions['cmdline'] += 1
        logger.warning("Failed to read process command line, most likely due to a race condition! (%s)", pathname)
        contents = ''
    # Strip the trailing null byte so we don't report every command line with a
    # trailing empty string (our callers should not be bothered with obscure
    # details about the encoding of /proc/[pid]/cmdline).
    if contents.endswith('\0'):
        contents = contents[:-1]
    # Python's str.split() implementation splits empty strings into a list
    # containing a single empty string. This is an incorrect representation of
    # a parsed command line so we explicitly guard against this.
    return contents.split('\0') if contents else []
