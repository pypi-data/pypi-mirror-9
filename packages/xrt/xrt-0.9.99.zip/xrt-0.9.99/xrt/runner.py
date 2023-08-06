# -*- coding: utf-8 -*-
"""
Module :mod:`runner` defines the entry point of xrt - :func:`run_ray_tracing`,
containers for job properties and functions for running the processes or
threads and accumulating the resulting histograms.
"""
__author__ = "Konstantin Klementiev, Roman Chernikov"
__date__ = "10 Apr 2015"

import os
import sys
import time
# import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import multiprocessing
import errno
import threading
import Queue
import uuid  # apparently is needed on some platforms with pyopencl

from . import multipro
from .backends import raycing

# _DEBUG = True
runCardVals = None
runCardProcs = None
_plots = []
needLimits = False


def retry_on_eintr(function, *args, **kw):
    """
    Suggested in:
    http://mail.python.org/pipermail/python-list/2011-February/1266462.html
    as a solution for `IOError: [Errno 4] Interrupted system call` in Linux.
    """
    while True:
        try:
            return function(*args, **kw)
        except IOError, e:
            if e.errno == errno.EINTR:
                continue
            else:
                raise


class RunCardVals(object):
    """
    Serves as a global container for a sub-set of run properties passed by the
    user to :func:`run_ray_tracing`. The sub-set is limited to pickleable
    objects for passing it to job processes or threads.
    """
    def __init__(self, threads, processes, repeats, updateEvery, backend,
                 globalNorm):
        if threads >= processes:
            self.Event = threading.Event
            self.Queue = Queue.Queue
        else:
            self.Event = multiprocessing.Event
            self.Queue = multiprocessing.Queue

        self.stop_event = self.Event()
        self.finished_event = self.Event()
        self.stop_event.clear()
        self.finished_event.clear()

        self.threads = threads
        self.processes = processes
        self.repeats = repeats
        self.updateEvery = updateEvery
        self.backend = backend
        self.globalNorm = globalNorm
        self.passNo = 0
        self.savedResults = []
        self.iteration = 0


class RunCardProcs(object):
    """
    Serves as a global container for a sub-set of run properties passed by the
    user to :func:`run_ray_tracing` limited to functions. These cannot be
    passed to job processes or threads (because are not pickleable) and have to
    be executed by the job server (this module).
    """
    def __init__(self, afterScript, afterScriptArgs, afterScriptKWargs):
        self.afterScript = afterScript
        self.afterScriptArgs = afterScriptArgs
        self.afterScriptKWargs = afterScriptKWargs
        self.generatorNorm = None
        self.generatorPlot = None


def _simple_generator():
    """
    The simplest generator for running only one ray-tracing study. Search
    examples for generators that run complex ray-tracing studies.
    """
    yield


def start_jobs():
    """
    Restores the plots if requested and if the persistent files exist and
    starts the qt timer of the 1st plot.
    """
    for plot in _plots:
        if plot.persistentName:
            plot.restore_plots()
        plot.fig.canvas.set_window_title(plot.title)

    runCardVals.iteration = long(0)
    noTimer = len(_plots) == 0 or\
        (plt.get_backend().lower() in (x.lower() for x in
                                       mpl.rcsetup.non_interactive_bk))
    if noTimer:
        print "The job is running... "
        while True:
            msg = '{0} of {1}'.format(
                runCardVals.iteration+1, runCardVals.repeats)
            if os.name == 'posix':
                sys.stdout.write("\r\x1b[K " + msg)
            else:
                sys.stdout.write("\r" + "  ")
                print msg, ' ',
            sys.stdout.flush()
            res = dispatch_jobs()
            if res:
                return
    else:
        plot = _plots[0]
        plot.areProcessAlreadyRunning = False
        plot.timer = plot.fig.canvas.new_timer()
        plot.timer.add_callback(plot.timer_callback)
        plot.timer.start()


def dispatch_jobs():
    """Runs the jobs in separate processes or threads and collects the resulted
    histograms from the output queues. One cannot run this function in a loop
    because the redrawing will not work. Instead, it is started from a timer
    event handler of a qt-graph."""
    if (runCardVals.iteration >= runCardVals.repeats) or \
            runCardVals.stop_event.is_set():
        on_finish()
        return True
    one_iteration()
    if (runCardVals.iteration >= runCardVals.repeats) or \
            runCardVals.stop_event.is_set():
        on_finish()
        return True
    if runCardVals.iteration % runCardVals.updateEvery == 0:
        for plot in _plots:
            plot.plot_plots()
    if len(_plots) > 0:
        _plots[0].areProcessAlreadyRunning = False


def one_iteration():
    """The body of :func:`dispatch_jobs`."""
    global needLimits
    plots2Pickle = [plot.card_copy() for plot in _plots]
    outPlotQueues = [runCardVals.Queue() for plot in _plots]
    alarmQueue = runCardVals.Queue()

# in the 1st iteration the plots may require some of x, y, e limits to be
# calculated and thus this case is special:
    cpus = max(runCardVals.threads, runCardVals.processes)
    if runCardVals.iteration == 0:
        for plot in _plots:
            xLimitsDefined = (plot.xaxis.limits is not None) and\
                (not isinstance(plot.xaxis.limits, str))
            yLimitsDefined = (plot.yaxis.limits is not None) and\
                (not isinstance(plot.yaxis.limits, str))
            cLimitsDefined = (plot.caxis.limits is not None) and\
                (not isinstance(plot.caxis.limits, str)) or plot.ePos == 0
            if not (xLimitsDefined and yLimitsDefined and cLimitsDefined):
                needLimits = True
                break
        if needLimits:
            cpus = 1
    elif runCardVals.iteration == 1:  # balances the 1st one
        if needLimits:
            cpus -= 1
    if cpus < 1:
        cpus = 1

    if runCardVals.threads >= runCardVals.processes:
        BackendOrProcess = multipro.BackendThread
    else:
        BackendOrProcess = multipro.BackendProcess
    processes = [BackendOrProcess(runCardVals, plots2Pickle, outPlotQueues,
                                  alarmQueue, icpu) for icpu in range(cpus)]
#    print('top process:', os.getpid())
    for p in processes:
        p.start()

    for p in processes:
        if runCardVals.backend.startswith('raycing'):
            runCardVals.beamLine.alarms = retry_on_eintr(alarmQueue.get)
            for alarm in runCardVals.beamLine.alarms:
                print alarm
        outList = [0, ]
        for plot, queue in zip(_plots, outPlotQueues):
            outList = retry_on_eintr(queue.get)

            if len(outList) == 0:
                continue
            if (runCardVals.iteration >= runCardVals.repeats) or \
                    runCardVals.stop_event.is_set():
                continue
            plot.textStatus.set_text("{0} of {1} (right click to stop)".format(
                runCardVals.iteration+1, runCardVals.repeats))

            plot.nRaysAll += outList[12]
            if runCardVals.backend.startswith('shadow'):
                plot.nRaysNeeded += outList[13]
            elif runCardVals.backend.startswith('raycing'):
                nRaysVarious = outList[13]
                plot.nRaysAlive += nRaysVarious[0]
                plot.nRaysGood += nRaysVarious[1]
                plot.nRaysOut += nRaysVarious[2]
                plot.nRaysOver += nRaysVarious[3]
                plot.nRaysDead += nRaysVarious[4]
                plot.nRaysAccepted += nRaysVarious[5]
                plot.nRaysAcceptedE += nRaysVarious[6]
                plot.nRaysSeeded += nRaysVarious[7]
                plot.nRaysSeededI += nRaysVarious[8]
                plot.displayAsAbsorbedPower = outList[14]

            for iaxis, axis in enumerate(
                    [plot.xaxis, plot.yaxis, plot.caxis]):
                if (iaxis == 2) and (not plot.ePos):
                    continue
                axis.total1D += outList[0+iaxis*3]
                axis.total1D_RGB += outList[1+iaxis*3]
                if runCardVals.iteration == 0:
                    axis.binEdges = outList[2+iaxis*3]
            plot.total2D += outList[9]
            plot.total2D_RGB += outList[10]
            plot.intensity += outList[11]

            if runCardVals.iteration == 0:  # needed for multiprocessing
                plot.set_axes_limits(*outList.pop())
#            queue.task_done()
        if len(outList) > 0:
            runCardVals.iteration += 1
    for p in processes:
        p.join(60.)


def on_finish():
    """Executed on exit from the ray-tracing iteration loop."""
    if len(_plots) > 0:
        plot = _plots[0]
        if plt.get_backend().lower() not in (
                x.lower() for x in mpl.rcsetup.non_interactive_bk):
            plot.timer.stop()
            plot.timer.remove_callback(plot.timer_callback)
        plot.areProcessAlreadyRunning = False
    for plot in _plots:
        plot.textStatus.set_text('')
        plot.fig.canvas.mpl_disconnect(plot.cidp)
        plot.plot_plots()
        plot.save()
    runCardVals.tstop = time.time()
    print 'The ray tracing with {0} iteration{1} took {2:0.1f} s'.format(
        runCardVals.iteration, 's' if runCardVals.iteration > 1 else '',
        runCardVals.tstop-runCardVals.tstart)
    runCardVals.finished_event.set()
    for plot in _plots:
        if runCardVals.globalNorm or plot.persistentName:
            plot.store_plots()
    if runCardVals.stop_event.is_set():
        print 'Interrupted by user after iteration {0}'.format(
            runCardVals.iteration)
        return
    try:
        if runCardProcs.generatorPlot is not None:
            runCardProcs.generatorPlot.next()
    except StopIteration:
        pass
    else:
        for plot in _plots:
            plot.clean_plots()
        start_jobs()
        return

    if runCardVals.globalNorm:
        aSavedResult = -1
        print 'normalizing ...',
        for aRenormalization in runCardProcs.generatorNorm:
            for plot in _plots:
                aSavedResult += 1
                saved = runCardVals.savedResults[aSavedResult]
                saved.restore(plot)
                plot.fig.canvas.set_window_title(plot.title)
#                if _DEBUG:
#                    print plot.title
                for runCardVals.passNo in [1, 2]:
                    plot.plot_plots()
#                    if _DEBUG:
#                        print plot.saveName
                    plot.save('_norm' + str(runCardVals.passNo))

    print 'finished'
#    plt.close('all')
    if runCardProcs.afterScript:
        runCardProcs.afterScript(
            *runCardProcs.afterScriptArgs, **runCardProcs.afterScriptKWargs)


def normalize_sibling_plots(plots):
    print 'normalization started'
    max1Dx = 0
    max1Dy = 0
    max1Dc = 0
    max1Dx_RGB = 0
    max1Dy_RGB = 0
    max1Dc_RGB = 0
    max2D_RGB = 0
    for plot in plots:
        if max1Dx < plot.xaxis.max1D:
            max1Dx = plot.xaxis.max1D
        if max1Dy < plot.yaxis.max1D:
            max1Dy = plot.yaxis.max1D
        if max1Dc < plot.caxis.max1D:
            max1Dc = plot.caxis.max1D
        if max1Dx_RGB < plot.xaxis.max1D_RGB:
            max1Dx_RGB = plot.xaxis.max1D_RGB
        if max1Dy_RGB < plot.yaxis.max1D_RGB:
            max1Dy_RGB = plot.yaxis.max1D_RGB
        if max1Dc_RGB < plot.caxis.max1D_RGB:
            max1Dc_RGB = plot.caxis.max1D_RGB
        if max2D_RGB < plot.max2D_RGB:
            max2D_RGB = plot.max2D_RGB

    for plot in plots:
        plot.xaxis.globalMax1D = max1Dx
        plot.yaxis.globalMax1D = max1Dy
        plot.caxis.globalMax1D = max1Dc
        plot.xaxis.globalMax1D_RGB = max1Dx_RGB
        plot.yaxis.globalMax1D_RGB = max1Dy_RGB
        plot.caxis.globalMax1D_RGB = max1Dc_RGB
        plot.globalMax2D_RGB = max2D_RGB

    for runCardVals.passNo in [1, 2]:
        for plot in plots:
            plot.plot_plots()
            plot.save('_norm' + str(runCardVals.passNo))
    print 'normalization finished'


def run_ray_tracing(
    plots, repeats=1, updateEvery=1, energyRange=None, backend='raycing',
    beamLine=None, threads=1, processes=1, generator=None, globalNorm=0,
        afterScript=None, afterScriptArgs=[], afterScriptKWargs={}):
    """
    This function is the entry point of xrt.
    Parameters are all optional except the 1st one.

        *plots*: instance of :class:`~xrt.plotter.XYCPlot` or a sequence of
            instances or an empty sequence if no graphical output is wanted.

        *repeats*: int
            The number of ray tracing runs. It should be stressed that
            accumulated are not rays, which would be limited by the physical
            memory, but rather the histograms from each run are summed up. In
            this way the number of rays is unlimited.

        *updateEvery*: int
            Redrawing rate. Redrawing happens when the current iteration index
            is divisible by *updateEvery*.

        *energyRange*: [*eMin*: float, *eMax*: float]
            Only in `shadow` backend: If not None, sets the energy range of
            shadow source. Alternatively, this can be done directly inside
            the *generator*.

        *backend*: str
            so far supported: {'shadow' | 'raycing' | 'dummy'}

        *beamLine*: instance of :class:`~xrt.backends.raycing.BeamLine`, used
        with `raycing` backend.

        *threads*, *processes*: int or str
            The number of parallel threads or processes, should not be greater
            than the number of cores in your computer, otherwise it gives no
            gain. The bigger of the two will be used as a signal for using
            either :mod:`threading` or :mod:`multiprocessing`. If they are
            equal, :mod:`threading` is used. See also
            :ref:`performance tests<tests>`. If 'all' is given then the number
            returned by multiprocessing.cpu_count() will be used.

            .. warning::
                You cannot use multiprocessing in combination with OpenCL
                because the resources (CPU or GPU) are already shared by
                OpenCL. You will get an error if *processes* > 1. You can still
                use *threads* > 1 but with a little gain.

            .. note::
                For the :mod:`shadow` backend you must create ``tmp0``,
                ``tmp1`` etc. directories (counted by *threads* or *processes*)
                in your working directory. Even if the execution is not
                parallelized, there must be ``tmp0`` with the shadow files
                prepared in it.

        *generator*: generator object
            A generator for running complex ray-tracing studies. It must modify
            the optics, specify the graph limits, define the output file names
            etc. in a loop and return to xrt by ``yield``.
            See the supplied examples.

        .. _globalNorm:

        *globalNorm*: bool
            If True, the intensity of the histograms will be normalized to the
            global maximum throughout the series of graphs. There are two
            flavors of normalization:

            1) only the heights of 1D histograms are globally normalized while
               the brightness is kept with the normalization to the local
               maximum (i.e. the maximum in the given graph).
            2) both the heights of 1D histograms and the brightness of 1D and
               2D histograms are globally normalized.

            The second way is physically more correct but sometimes is less
            visual: some of the normalized pictures may become too dark, e.g.
            when you compare focused and strongly unfocused images. Both
            normalizations are saved with suffixes ``_norm1`` and ``_norm2``
            for you to select the better one.

            Here is a normalization example where the intensity maximum was
            found throughout a series of images for filters of different
            thickness. The brightest image was for the case of no filter (not
            shown here) and the normalization shown below was done relative to
            that image:

            +------------------------------+----------------+
            | normalized to local maximum  | |image_nonorm| |
            +------------------------------+----------------+
            | global normalization, type 1 | |image_norm1|  |
            +------------------------------+----------------+
            | global normalization, type 2 | |image_norm2|  |
            +------------------------------+----------------+

            .. |image_nonorm| image:: _images/filterFootprint2_I400mum.*
               :scale: 50 %
            .. |image_norm1| image:: _images/filterFootprint2_I400mum_norm1.*
               :scale: 50 %
            .. |image_norm2| image:: _images/filterFootprint2_I400mum_norm2.*
               :scale: 50 %

        *afterScript*: function object
            This function is executed at the end of the current script. For
            example, it may run the next ray-tracing script.
    """
    global runCardVals, runCardProcs, _plots
    if isinstance(plots, (list, tuple)):
        _plots = plots
    else:
        _plots = [plots, ]
    for plot in _plots:
        if backend == 'raycing':
            if plot.caxis.useCategory:
                plot.caxis.limits = [raycing.hueMin, raycing.hueMax]
            if isinstance(plot.rayFlag, int):
                plot.rayFlag = plot.rayFlag,

    if updateEvery < 1:
        updateEvery = 1
    if (repeats > 1) and (updateEvery > repeats):
        updateEvery = repeats
    cpuCount = multiprocessing.cpu_count()
    if isinstance(processes, str):
        if processes.startswith('a'):  # all
            processes = cpuCount
        else:
            processes = max(cpuCount // 2, 1)
    if isinstance(threads, str):
        if threads.startswith('a'):  # all
            threads = cpuCount
        else:
            threads = max(cpuCount // 2, 1)
    runCardVals = RunCardVals(
        threads, processes, repeats, updateEvery, backend, globalNorm)
    runCardProcs = RunCardProcs(
        afterScript, afterScriptArgs, afterScriptKWargs)

    runCardVals.cwd = os.getcwd()
    cpus = max(threads, processes)
    if backend.startswith('shadow'):
        from .backends import shadow
        shadow.check_shadow_dirs(cpus, runCardVals.cwd)
        runCardVals.fWiggler, runCardVals.fPolar, runCardVals.blockNRays = \
            shadow.init_shadow(cpus, runCardVals.cwd, energyRange)
    elif backend == 'raycing':
        runCardVals.beamLine = beamLine

    if generator is None:
        runCardProcs.generatorPlot = _simple_generator()
    else:
        runCardProcs.generatorPlot = generator()
        if globalNorm:
            runCardProcs.generatorNorm = generator()

    if runCardProcs.generatorPlot is not None:
        runCardProcs.generatorPlot.next()

    runCardVals.tstart = time.time()
    start_jobs()
    plt.show()
