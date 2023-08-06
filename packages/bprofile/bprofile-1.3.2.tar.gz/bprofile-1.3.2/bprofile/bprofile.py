#####################################################################
#                                                                   #
# profile.py                                                        #
#                                                                   #
# Copyright 2014, Chris Billington                                  #
#                                                                   #
# This file is part of the bprofile project (see                    #
# https://bitbucket.org/cbillington/bprofile) and is licensed under #
# the Simplified BSD License. See the LICENSE.txt file in the root  #
# of the project for the full license.                              #
#                                                                   #
#####################################################################

import sys
import os
import subprocess
import pstats
import threading
import time
import atexit
import weakref
import uuid
import tempfile
import functools
import cProfile

this_folder = os.path.dirname(os.path.realpath(__file__))
gprof2dot = os.path.join(this_folder, 'gprof2dot.py')


# Startupinfo, for ensuring subprocesses don't launch with a visible cmd.exe
# window on Windows:
if os.name == 'nt':
    startupinfo = subprocess.STARTUPINFO()
    try:
        STARTF_USESHOWWINDOW = subprocess.STARTF_USESHOWWINDOW
    except AttributeError:
        # Above is absent in some versions of Python, but for them it is here:
        STARTF_USESHOWWINDOW = subprocess._subprocess.STARTF_USESHOWWINDOW
    startupinfo.dwFlags |= STARTF_USESHOWWINDOW
else:
    startupinfo = None


def find_dot():
    devnull = open(os.devnull)
    if os.name == 'nt':
        program_files = os.environ["ProgramFiles"]
        program_files_x86 = os.environ["ProgramFiles(x86)"]
        for folder in [program_files, program_files_x86]:
            for subfolder in os.listdir(folder):
                if 'graphviz' in subfolder.lower():
                    dot = os.path.join(folder, subfolder, 'bin', 'dot.exe')
                    if os.path.exists(dot):
                        return dot
        else:
            raise OSError('dot.exe not found, please install graphviz')
    else:
        if subprocess.call(['type', 'dot'], shell=True, stdout=devnull, stderr=devnull):
            raise OSError('\'dot\' not found, please install graphviz')
        return 'dot'


DOT_PATH = find_dot()

class BProfile(object):

    """A profiling context manager.

    A context manager that after it exits, outputs a .png file of a graph made
    via cProfile, gprof2dot and graphviz. The context manager can be used
    multiple times, and if used repeatedly, regularly updates its output to
    include cumulative results.
    
    An instance can also be used as a decorator, it will simply wrap calls to
    the decorated method in the profiling context.

    Parameters
    ----------

    output_path: str
        The name of the .png report file you would like to output. '.png' will
        be appended if not present.

    threshold_percent: int or float
        Nodes in which execution spends less than this percentage of the total
        profiled execution time will not be included in the output.

    report_interval: int or float
        The minimum time, in seconds, in between output file generation. If
        the context manager exits and it has not been at least this long since
        the last output was generated, output generation will be delayed until
        it has been. More profiling can run in the meantime. This is to
        decrease overhead on your program, (even though this overhead will
        only be incurred when no code is being profiled), while allowing you
        to have ongoing results of the profiling while your code is still
        running. If you only use the context manager once, then this argument
        has no effect. If you set it to zero, output will be produced after
        every exit of the context.
        
    enabled: bool
        Whether the profiler is enabled or not. Equivalent to calling
        :func:`~bprofile.BProfile.set_enabled` with this argument after
        instantiation. Useful for enabling and disabling profiling with
        a global flag when you do not have easy access to the instance
        - for example when using as a decorator.


    Notes
    -----

    The profiler will return immediately after the context manager, and will
    generate its .png report in a separate thread. If the same context manager
    is used multiple times output will be generated at most every
    ``report_interval`` seconds (default: 5). The delay is to allow blocks to
    execute many times in between reports, rather than slowing your program
    down with generating graphs all the time. This means that if your profile
    block is running rapidly and repeatedly, a new report will be produced
    every ``report_interval`` seconds.

    Pending reports will be generated at interpreter shutdown.

    Note that even if ``report_interval`` is short, reporting will not
    interfere with the profiling results themselves, as a lock is acquired
    that will prevent profiled code from running at the same time as the
    report generation code. So the overhead produced by report generation does
    not affect the results of profiling - this overhead will only affect
    portions of your code that are not being profiled.

    The lock is shared between instances, and so you can freely instantiate
    many :class:`BProfile` instances to profile different parts of your code.
    Instances with the same ``output_path`` will share an underlying cProfile
    profiler, and so their reports will be combined. Profile objects are
    thread safe, so a single instance can be shared as well anywhere in your
    program.

    .. warning::

        Since only one profiler can be running at a time, two profiled pieces
        of code in different threads waiting on each other in any way will
        deadlock.
    """

    _class_lock = threading.Lock()
    _report_required = threading.Event()
    _report_thread = None
    _reporting_lock = threading.RLock()
    _instances_requiring_reports = set()
    _profilers = weakref.WeakValueDictionary()
    _threadlocal = threading.local()
    
    def __init__(self, output_path, threshold_percent=2.5, report_interval=5, enabled=True):
        if not output_path.lower().endswith('.png'):
            output_path += '.png'
        output_path = os.path.abspath(os.path.realpath(output_path))
        with self._class_lock:
            self.output_path = output_path
            self.threshold_percent = threshold_percent
            self.report_interval = report_interval
            self.time_of_last_report = time.time() - report_interval
            self.enabled = True
            self.running = False
            self._instance_lock = threading.Lock()
            # Only one profiler per output file:
            try:
                self.profiler = self._profilers[self.output_path]
            except KeyError:
                self.profiler = cProfile.Profile()
                self._profilers[self.output_path] = self.profiler
            # only one reporting thread to be shared between instances:
            if self._report_thread is None:
                report_thread = threading.Thread(target=self._report_loop, name='bprofile.Bprofile._report_loop')
                report_thread.daemon = True
                report_thread.start()
                self.__class__._report_thread = report_thread

    def __call__(self, function):
        """Returns a wrapped version of ``function`` with profiling.
        Intended for use as a decorator."""
        @functools.wraps(function)
        def function_with_profiling(*args, **kwargs):
            with self:
                return function(*args, **kwargs)
        return function_with_profiling
        
    def __enter__(self):
        self.start()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.stop()

    def set_enabled(self, enabled):
        """Set whether profiling is enabled.

        if enabled==True, all methods work as normal. Otherwise
        :func:`~bprofile.BProfile.start`, :func:`~bprofile.BProfile.stop`, and
        :func:`~bprofile.BProfile.do_report` become dummy methods that do
        nothing. This is useful for having a global variable to turn
        profiling on or off, based on whether one is debugging or not, or
        to enable or disable profiling of different parts of code selectively.

        If profiling is running when this method is called to disable it, the
        profiling will be stopped."""
        with self._instance_lock:
            self.enabled = bool(enabled)
            if not enabled and self.running:
                self.profiler.disable()
                self._class_lock.release()

    def start(self):
        """Begin profiling."""
        with self._instance_lock:
            if not self.enabled:
                return
            if getattr(self._threadlocal, 'is_profiling', False):
                message = ('Profiling is already running in this thread. ' + 
                           'Only one profiler can be running at a time, ' +
                           'and since we are in the same thread we cannot simply ' +
                           'wait until it finishes, as that would deadlock. ' +
                           'I thought you would prefer an error message to a deadlock.')
                raise RuntimeError(message)
            self._class_lock.acquire()
            self._threadlocal.is_profiling = True
            self.profiler.enable()

    def stop(self):
        """Stop profiling.

        Stop profiling and outptut a profiling report, if at least
        ``report_interval`` has elapsed since the last report. Otherwise
        output the report after a delay.

        Does not preclude starting profiling again at a  later time. Results
        are cumulative."""
        with self._instance_lock:
            if not self.enabled:
                return
            try:
                self.profiler.disable()
                self._instances_requiring_reports.add(self)
                self._report_required.set()
            finally:
                self._class_lock.release()
                self._threadlocal.is_profiling = False

    def do_report(self):
        """Collect statistics and output a .png file of the profiling report.

        Notes
        -----

        This occurs automatically at a rate of ``report_interval``, but one
        can call this method to report results sooner. The report will include
        results from all :class:`BProfile` instances that have the same
        ``output_path`` and no more automatic reports (if further profiling is
        done) will be produced until after the minimum ``report_interval`` of
        those instances.

        This method can be called at any time and is threadsafe. It is not
        advisable to call it during profiling however as this will incur
        overhead that will affect the profiling results. Only automatic
        reports are guaranteed to be generated when no profiling is taking
        place."""
        if not self.enabled:
            return
        # Randomly named tempfiles, we don't use NamedTemporaryFile as we
        # don't want to create the files - just pass the names as command line
        # arguments to other programs:
        tempfile_prefix = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))
        pstats_file = tempfile_prefix + '.pstats'
        dot_file = tempfile_prefix + '.dot'
        with self._reporting_lock:
            pstats.Stats(self.profiler).dump_stats(pstats_file)

            # All instances with this output file that have a pending report:
            instances = set(o for o in self._instances_requiring_reports.copy() if o.output_path == self.output_path)
            instances.add(self)
            threshold_percent = str(min(o.threshold_percent for o in instances))
            try:
                subprocess.check_call([sys.executable, gprof2dot, '-n', threshold_percent, '-f', 'pstats',
                                       '-o', dot_file, pstats_file], startupinfo=startupinfo)
                subprocess.check_call([DOT_PATH, '-o', self.output_path, '-Tpng', dot_file], startupinfo=startupinfo)
                os.unlink(dot_file)
                os.unlink(pstats_file)
            except subprocess.CalledProcessError:
                sys.stderr.write('gprof2dot or dot returned nonzero exit code\n')

            for instance in instances:
                instance.time_of_last_report = time.time()
                try:
                    self._instances_requiring_reports.remove(instance)
                except KeyError:
                    # Another thread already removed it:
                    pass

    @classmethod
    def _atexit(cls):
        # Finish pending reports:
        with cls._reporting_lock:
            while True:
                try:
                    instance = cls._instances_requiring_reports.pop()
                except KeyError:
                    break
                else:
                    instance.do_report()

    @classmethod
    def _report_loop(cls):
        atexit.register(cls._atexit)
        timeout = None
        while True:
            cls._report_required.wait(timeout)
            with cls._class_lock:
                cls._report_required.clear()
                if not cls._instances_requiring_reports:
                    timeout = None
                    continue
                with cls._reporting_lock:
                    for instance in cls._instances_requiring_reports.copy():
                        if instance not in cls._instances_requiring_reports:
                            # Instance has already had a report run on it,
                            # because it shares a profiler with another
                            # instance we just reported on. So it has been
                            # removed from the set. Do not run an extra report
                            # on it.
                            continue
                        else:
                            next_report_time = instance.time_of_last_report + instance.report_interval
                            time_until_report = next_report_time - time.time()
                            if time_until_report < 0:
                                instance.do_report()
                            elif timeout is None:
                                timeout = time_until_report
                            else:
                                timeout = min(timeout, time_until_report)


if __name__ == '__main__':
    # Test:
    profiler = BProfile('test.png')

    @profiler
    def decorator_test():
        with profiler:
            time.sleep(10)
        
    # decorator_test() # this should raise an exception saying it would deadlock
    
    def foo():
        time.sleep(0.05)

    def bar():
        time.sleep(0.1)

    start_time = time.time()
    for i in range(100):
        print(i)
        with profiler:
            time.sleep(0.1)
            # profiler.do_report()
            foo()
            bar()
    print(time.time() - start_time)
