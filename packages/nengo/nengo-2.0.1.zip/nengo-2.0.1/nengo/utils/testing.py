from __future__ import absolute_import

import inspect
import itertools
import os
import re
import sys
import time
import warnings

import numpy as np
import pytest

from .compat import is_string


class Plotter(object):
    class Mock(object):
        def __init__(self, *args, **kwargs):
            pass

        def __call__(self, *args, **kwargs):
            return Plotter.Mock()

        def __mul__(self, other):
            return 1.0

        @classmethod
        def __getattr__(cls, name):
            if name in ('__file__', '__path__'):
                return '/dev/null'
            elif name[0] == name[0].upper():
                mockType = type(name, (), {})
                mockType.__module__ = __name__
                return mockType
            else:
                return Plotter.Mock()

    def __init__(self, simulator, module, function, nl=None, plot=None):
        if plot is None:
            self.plot = int(os.getenv("NENGO_TEST_PLOT", 0))
        else:
            self.plot = plot

        self.dirname = "%s.plots" % simulator.__module__
        if nl is not None:
            self.dirname = os.path.join(self.dirname, nl.__name__)

        modparts = module.__name__.split('.')
        modparts = modparts[1:]
        modparts.remove('tests')
        self.filename = "%s.%s.pdf" % ('.'.join(modparts), function.__name__)

    def __enter__(self):
        if self.plot:
            import matplotlib.pyplot as plt
            self.plt = plt
            if not os.path.exists(self.dirname):
                os.makedirs(self.dirname)
        else:
            self.plt = Plotter.Mock()
        return self.plt

    def __exit__(self, type, value, traceback):
        if self.plot:
            if hasattr(self.plt, 'saveas') and self.plt.saveas is None:
                del self.plt.saveas
                self.plt.close('all')
                return
            elif hasattr(self.plt, 'saveas'):
                self.filename = self.plt.saveas
                del self.plt.saveas

            if len(self.plt.gcf().get_axes()) > 0:
                # tight_layout errors if no axes are present
                self.plt.tight_layout()
            self.plt.savefig(os.path.join(self.dirname, self.filename))
            self.plt.close('all')


class Timer(object):
    """A context manager for timing a block of code.

    Attributes
    ----------
    duration : float
        The difference between the start and end time (in seconds).
        Usually this is what you care about.
    start : float
        The time at which the timer started (in seconds).
    end : float
        The time at which the timer ended (in seconds).

    Example
    -------
    >>> import time
    >>> with Timer() as t:
    ...    time.sleep(1)
    >>> assert t.duration >= 1
    """

    TIMER = time.clock if sys.platform == "win32" else time.time

    def __init__(self):
        self.start = None
        self.end = None
        self.duration = None

    def __enter__(self):
        self.start = Timer.TIMER()
        return self

    def __exit__(self, type, value, traceback):
        self.end = Timer.TIMER()
        self.duration = self.end - self.start


class WarningCatcher(object):
    def __enter__(self):
        self.catcher = warnings.catch_warnings(record=True)
        self.record = self.catcher.__enter__()

    def __exit__(self, type, value, traceback):
        self.catcher.__exit__(type, value, traceback)


class warns(WarningCatcher):
    def __init__(self, warning_type):
        self.warning_type = warning_type

    def __exit__(self, type, value, traceback):
        if not any(r.category is self.warning_type for r in self.record):
            pytest.fail("DID NOT RAISE")

        super(warns, self).__exit__(type, value, traceback)


def allclose(t, targets, signals,  # noqa:C901
             atol=1e-8, rtol=1e-5, buf=0, delay=0,
             plt=None, show=False, labels=None, individual_results=False):
    """Ensure all signal elements are within tolerances.

    Allows for delay, removing the beginning of the signal, and plotting.

    Parameters
    ----------
    t : array_like (T,)
        Simulation time for the points in `target` and `signals`.
    targets : array_like (T, 1) or (T, N)
        Reference signal or signals for error comparison.
    signals : array_like (T, N)
        Signals to be tested against the target signals.
    atol, rtol : float
        Absolute and relative tolerances.
    buf : float
        Length of time (in seconds) to remove from the beginnings of signals.
    delay : float
        Amount of delay (in seconds) to account for when doing comparisons.
    plt : matplotlib.pyplot or mock
        Pyplot interface for plotting the results, unless it's mocked out.
    show : bool
        Whether to show the plot immediately.
    labels : list of string, length N
        Labels of each signal to use when plotting.
    individual_results : bool
        If True, returns a separate `allclose` result for each signal.
    """
    t = np.asarray(t)
    dt = t[1] - t[0]
    assert t.ndim == 1
    assert np.allclose(np.diff(t), dt)

    targets = np.asarray(targets)
    signals = np.asarray(signals)
    if targets.ndim == 1:
        targets = targets.reshape((-1, 1))
    if signals.ndim == 1:
        signals = signals.reshape((-1, 1))
    assert targets.ndim == 2 and signals.ndim == 2
    assert t.size == targets.shape[0]
    assert t.size == signals.shape[0]
    assert targets.shape[1] == 1 or targets.shape[1] == signals.shape[1]

    buf = int(np.round(buf / dt))
    delay = int(np.round(delay / dt))
    slice1 = slice(buf, len(t) - delay)
    slice2 = slice(buf + delay, None)

    if plt is not None:
        if labels is None:
            labels = [None] * len(signals)
        elif is_string(labels):
            labels = [labels]

        colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']

        def plot_target(ax, x, b=0, c='k'):
            bound = atol + rtol * np.abs(x)
            y = x - b
            ax.plot(t[slice2], y[slice1], c + ':')
            ax.plot(t[slice2], (y + bound)[slice1], c + '--')
            ax.plot(t[slice2], (y - bound)[slice1], c + '--')

        # signal plot
        ax = plt.subplot(2, 1, 1)
        for y, label in zip(signals.T, labels):
            ax.plot(t, y, label=label)

        if targets.shape[1] == 1:
            plot_target(ax, targets[:, 0], c='k')
        else:
            color_cycle = itertools.cycle(colors)
            for x in targets.T:
                plot_target(ax, x, c=next(color_cycle))

        ax.set_ylabel('signal')
        if labels[0] is not None:
            ax.legend(loc='upper left', bbox_to_anchor=(1., 1.))

        ax = plt.subplot(2, 1, 2)
        if targets.shape[1] == 1:
            x = targets[:, 0]
            plot_target(ax, x, b=x, c='k')
            for y, label in zip(signals.T, labels):
                ax.plot(t[slice2], y[slice2] - x[slice1])
        else:
            color_cycle = itertools.cycle(colors)
            for x, y, label in zip(targets.T, signals.T, labels):
                c = next(color_cycle)
                plot_target(ax, x, b=x, c=c)
                ax.plot(t[slice2], y[slice2] - x[slice1], c, label=label)

        ax.set_xlabel('time')
        ax.set_ylabel('error')

        if show:
            plt.show()

    if individual_results:
        if targets.shape[1] == 1:
            return [np.allclose(y[slice2], targets[slice1, 0],
                                atol=atol, rtol=rtol) for y in signals.T]
        else:
            return [np.allclose(y[slice2], x[slice1], atol=atol, rtol=rtol)
                    for x, y in zip(targets.T, signals.T)]
    else:
        return np.allclose(signals[slice2, :], targets[slice1, :],
                           atol=atol, rtol=rtol)


def find_modules(root_path, prefix=[], pattern='^test_.*\\.py$'):
    """Find matching modules (files) in all subdirectories of a given path.

    Parameters
    ----------
    root_path : string
        The path of the directory in which to begin the search.
    prefix : string or list, optional
        A string or list of strings to append to each returned modules list.
    pattern : string, optional
        A regex pattern for matching individual file names. Defaults to
        looking for all testing scripts.

    Returns
    -------
    modules : list
        A list of modules. Each item in the list is a list of strings
        containing the module path.
    """
    if is_string(prefix):
        prefix = [prefix]
    elif not isinstance(prefix, list):
        raise TypeError("Invalid prefix type '%s'" % type(prefix).__name__)

    modules = []
    for path, dirs, files in os.walk(root_path):
        base = prefix + os.path.relpath(path, root_path).split(os.sep)
        for filename in files:
            if re.search(pattern, filename):
                name, ext = os.path.splitext(filename)
                modules.append(base + [name])

    return modules


def load_functions(modules, pattern='^test_', arg_pattern='^Simulator$'):
    """Load matching functions from a list of modules.

    Parameters
    ----------
    modules : list
        A list of testing modules to load, generated by `find_testmodules`.
    pattern : string, optional
        A regex pattern for matching the function names. Defaults to looking
        for all testing functions.
    arg_pattern : string, optional
        A regex pattern for matching the argument names. At least one argument
        must match the pattern. Defaults to selecting tests with
        a 'Simulator' argument.

    Returns
    -------
    tests : dict
        A dictionary of test functions, where the key is composed of the
        module and function name, and the value is the function handle.

    Examples
    --------
    To load all Nengo tests and add them to the current namespace, do

        nengo_dir = os.path.dirname(nengo.__file__)
        modules = find_modules(nengo_dir, prefix='nengo')
        tests = load_functions(modules)
        locals().update(tests)

    Notes
    -----
    - This was created to load py.test tests. Therefore, this function also
      loads functions that start with `pytest`, since these functions act as
      hooks into py.test.
    - TODO: currently, all `pytest` functions are loaded into the same
      namespace, which means that if two different files imlement the same
      py.test hook, only the latter of these will be respected.
    - TODO: py.test also allows test functions to be implemented in classes;
      these tests cannot currently be loaded by this function.
    """
    tests = {}
    for module in modules:
        m = __import__('.'.join(module), globals(), locals(), ['*'])
        for k in dir(m):
            if re.search(pattern, k):
                test = getattr(m, k)
                args = inspect.getargspec(test).args
                if any(re.search(arg_pattern, arg) for arg in args):
                    tests['.'.join(['test'] + module + [k])] = test
            if k.startswith('pytest'):  # automatically load py.test hooks
                # TODO: different files with different implementations of the
                #   same pytest hook will break here!
                tests[k] = getattr(m, k)

    return tests
