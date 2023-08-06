﻿# -*- coding: utf-8 -*-
r"""
.. _synchrotron-sources:

Synchrotron sources
-------------------
The images below are produced by
`\\tests\\raycing\\test_sources.py` and by
`\\examples\\withRaycing\\01_SynchrotronSources\\synchrotronSources.py`.

Bending magnet
~~~~~~~~~~~~~~

On a transversal screen the image is unlimited horizontally (practically
limited by the front end). The energy distribution is red-shifted for off-plane
photons. The polarization is primarily horizontal. The off-plane radiation has
non-zero projection to the vertical polarization plane.

+----------+--------------+------------------+-----------------+
| source   | total flux   | horiz. pol. flux | vert. pol. flux |
+==========+==============+==================+=================+
| using    |              |                  |                 |
| WS       |  |bmTotalWS| |   |bmHorizWS|    |   |bmVertWS|    |
+----------+--------------+------------------+-----------------+
| internal |              |                  |                 |
| xrt      | |bmTotalXRT| |   |bmHorizXRT|   |   |bmVertXRT|   |
+----------+--------------+------------------+-----------------+

.. |bmTotalWS| image:: _images/3bm_ws1-n-wideE-1TotalFlux.png
   :scale: 50 %
.. |bmHorizWS| image:: _images/3bm_ws1-n-wideE-2horizFlux.png
   :scale: 50 %
.. |bmVertWS| image:: _images/3bm_ws1-n-wideE-3vertFlux.png
   :scale: 50 %
.. |bmTotalXRT| image:: _images/3bm_xrt1-n-wideE-1TotalFlux.png
   :scale: 50 %
.. |bmHorizXRT| image:: _images/3bm_xrt1-n-wideE-2horizFlux.png
   :scale: 50 %
.. |bmVertXRT| image:: _images/3bm_xrt1-n-wideE-3vertFlux.png
   :scale: 50 %

The off-plane radiation is in fact left and right polarized:

+----------+-----------------------------+
| source   | circular polarization rate  |
+==========+=============================+
| using    |                             |
| WS       |     |bmCircPolRateWS|       |
+----------+-----------------------------+
| internal |                             |
| xrt      |     |bmCircPolRateXRT|      |
+----------+-----------------------------+

.. |bmCircPolRateWS| image:: _images/3bm_ws1-n-wideE-5CircPolRate.png
   :scale: 50 %
.. |bmCircPolRateXRT| image:: _images/3bm_xrt1-n-wideE-5CircPolRate.png
   :scale: 50 %

The horizontal phase space projected to a transversal plane at the origin is
parabolic:

+-------------------------+---------------------+
| zero electron beam size | σ\ :sub:`x` = 49 µm |
+=========================+=====================+
|         |bmPhaseSp0|    |     |bmPhaseSpN|    |
+-------------------------+---------------------+

.. |bmPhaseSp0| image:: _images/3bm_xrt1-0-wideE-horPhaseSpace.png
   :scale: 50 %
.. |bmPhaseSpN| image:: _images/3bm_xrt1-n-wideE-horPhaseSpace.png
   :scale: 50 %

Multipole wiggler
~~~~~~~~~~~~~~~~~

The horizontal image size is determined by the parameter K. The energy
distribution is red-shifted for off-plane photons. The polarization is
primarily horizontal. The off-plane radiation has non-zero projection to the
vertical polarization plane.

+----------+--------------+------------------+-----------------+
| source   | total flux   | horiz. pol. flux | vert. pol. flux |
+==========+==============+==================+=================+
| using    |              |                  |                 |
| WS       |  |wTotalWS|  |    |wHorizWS|    |    |wVertWS|    |
+----------+--------------+------------------+-----------------+
| internal |              |                  |                 |
| xrt      |  |wTotalXRT| |    |wHorizXRT|   |    |wVertXRT|   |
+----------+--------------+------------------+-----------------+

.. |wTotalWS| image:: _images/2w_ws1-n-wideE-1TotalFlux.png
   :scale: 50 %
.. |wHorizWS| image:: _images/2w_ws1-n-wideE-2horizFlux.png
   :scale: 50 %
.. |wVertWS| image:: _images/2w_ws1-n-wideE-3vertFlux.png
   :scale: 50 %
.. |wTotalXRT| image:: _images/2w_xrt1-n-wideE-1TotalFlux.png
   :scale: 50 %
.. |wHorizXRT| image:: _images/2w_xrt1-n-wideE-2horizFlux.png
   :scale: 50 %
.. |wVertXRT| image:: _images/2w_xrt1-n-wideE-3vertFlux.png
   :scale: 50 %

The horizontal longitudinal cross-section reveals a sinusoidal shape of the
source. The horizontal phase space projected to the transversal plane at the
origin has individual branches for each pole.

+-------------------------+---------------------+
| zero electron beam size | σ\ :sub:`x` = 49 µm |
+=========================+=====================+
|           |wYX0|        |        |wYXN|       |
+-------------------------+---------------------+
|        |wPhaseSp0|      |     |wPhaseSpN|     |
+-------------------------+---------------------+

.. |wYX0| image:: _images/2w_xrt1-0-wideE-crossectionYX.png
   :scale: 50 %
.. |wYXN| image:: _images/2w_xrt1-n-wideE-crossectionYX.png
   :scale: 50 %
.. |wPhaseSp0| image:: _images/2w_xrt1-0-wideE-horPhaseSpace.png
   :scale: 50 %
.. |wPhaseSpN| image:: _images/2w_xrt1-n-wideE-horPhaseSpace.png
   :scale: 50 %

Undulator
~~~~~~~~~
The module :mod:`~tests.raycing.test_sources` has functions for
visualization of the angular and energy distributions of the implemented
sources in 2D and 3D. This is especially useful for undulators because they
have sharp peaks, which requires a proper selection of angular and energy
meshes (not important in the new versions of xrt (>0.9), where there are no
angular and energy meshes and the intensity is calculated *for each* ray).

.. image:: _images/I0_x'E_mode4-1-und-urgent.png
   :scale: 50 %
.. image:: _images/I0_z'E_mode4-1-und-urgent.png
   :scale: 50 %

+--------------------+
|  |IpPol|  |IpPolZ| |
+--------------------+

.. |IpPol| image:: _images/IpPol.swf
   :width: 420
   :height: 200
.. |IpPolZ| image:: _images/zoomIcon.png
   :width: 20
   :target: _images/IpPol.swf

The ray traced images of an undulator source are feature-rich. The polarization
is primarily horizontal. The off-plane radiation has non-zero projection to the
vertical polarization plane.

+----------+-------------+------------------+-----------------+--------------+
| source   | total flux  | horiz. pol. flux | vert. pol. flux | deg. of pol. |
+==========+=============+==================+=================+==============+
| using    |             |                  |                 |              |
| Urgent   | |uTotalUr|  |    |uHorizUr|    |    |uVertUr|    | |uDegPolUr|  |
+----------+-------------+------------------+-----------------+--------------+
| internal |             |                  |                 |              |
| xrt      | |uTotalXRT| |   |uHorizXRT|    |    |uVertXRT|   | |uDegPolXRT| |
+----------+-------------+------------------+-----------------+--------------+

.. |uTotalUr| image:: _images/1u_urgent3-n-monoE-1TotalFlux.png
   :scale: 50 %
.. |uHorizUr| image:: _images/1u_urgent3-n-monoE-2horizFlux.png
   :scale: 50 %
.. |uVertUr| image:: _images/1u_urgent3-n-monoE-3vertFlux.png
   :scale: 50 %
.. |uDegPolUr| image:: _images/1u_urgent3-n-monoE-4DegPol.png
   :scale: 50 %
.. |uTotalXRT| image:: _images/1u_xrt3-n-monoE-1TotalFlux-Espread.png
   :scale: 50 %
.. |uHorizXRT| image:: _images/1u_xrt3-n-monoE-2horizFlux-Espread.png
   :scale: 50 %
.. |uVertXRT| image:: _images/1u_xrt3-n-monoE-3vertFlux-Espread.png
   :scale: 50 %
.. |uDegPolXRT| image:: _images/1u_xrt3-n-monoE-4DegPol-Espread.png
   :scale: 50 %

Elliptical undulator
~~~~~~~~~~~~~~~~~~~~

An elliptical undulator gives circular images with a higher circular
polarization rate in the inner rings:

+----------+--------------+------------------+-----------------+
| source   |  total flux  | horiz. pol. flux | vert. pol. flux |
+==========+==============+==================+=================+
| using    |              |                  |                 |
| Urgent   | |euTotalUr|  |    |euHorizUr|   |   |euVertUr|    |
+----------+--------------+------------------+-----------------+
| internal |              |                  |                 |
| xrt      | |euTotalXRT| |   |euHorizXRT|   |   |euVertXRT|   |
+----------+--------------+------------------+-----------------+

.. |euTotalUr| image:: _images/4eu_urgent3-n-monoE-1TotalFlux.png
   :scale: 50 %
.. |euHorizUr| image:: _images/4eu_urgent3-n-monoE-2horizFlux.png
   :scale: 50 %
.. |euVertUr| image:: _images/4eu_urgent3-n-monoE-3vertFlux.png
   :scale: 50 %
.. |euTotalXRT| image:: _images/4eu_xrt3-n-monoE-1TotalFlux.png
   :scale: 50 %
.. |euHorizXRT| image:: _images/4eu_xrt3-n-monoE-2horizFlux.png
   :scale: 50 %
.. |euVertXRT| image:: _images/4eu_xrt3-n-monoE-3vertFlux.png
   :scale: 50 %

+----------+---------------+----------------------------+
| source   |  deg. of pol. | circular polarization rate |
+==========+===============+============================+
| using    |               |                            |
| Urgent   | |euDegPolUr|  |     |euCircPolRateUr|      |
+----------+---------------+----------------------------+
| internal |               |                            |
| xrt      | |euDegPolXRT| |    |euCircPolRateXRT|      |
+----------+---------------+----------------------------+

.. |euDegPolUr| image:: _images/4eu_urgent3-n-monoE-4DegPol.png
   :scale: 50 %
.. |euCircPolRateUr| image:: _images/4eu_urgent3-n-monoE-5CircPolRate.png
   :scale: 50 %
.. |euDegPolXRT| image:: _images/4eu_xrt3-n-monoE-4DegPol.png
   :scale: 50 %
.. |euCircPolRateXRT| image:: _images/4eu_xrt3-n-monoE-5CircPolRate.png
   :scale: 50 %

.. _THz:

Terahertz undulator
~~~~~~~~~~~~~~~~~~~

This is a computationally difficult example that is hardly possible to
calculate with other commonly used codes. To achieve good convergence in a
reasonable calculation time, we have introduced a new undulator parameter
*gIntervals* that controls the underlying Gauss-Legendre mesh. The user may
want to modify it in extreme cases (wigglers, near field, wide angles etc.).


+------------------+-----------------+
| horiz. pol. flux | vert. pol. flux |
+==================+=================+
|     |uTHzH|      |     |uTHzV|     |
+------------------+-----------------+

.. |uTHzH| image:: _images/2THzU_xrt1-n-narrowE-2horizFlux-U_code.png
   :scale: 50 %
.. |uTHzV| image:: _images/2THzU_xrt1-n-narrowE-3vertFlux-U_code.png
   :scale: 50 %
"""
__author__ = "Konstantin Klementiev", "Roman Chernikov"
__date__ = "10 Apr 2015"

#import matplotlib
#matplotlib.use('agg')

import sys
#sys.path.append(r"c:\xrt-0.9.4")
sys.path.append(r"c:\Ray-tracing")
import time
#import matplotlib
#matplotlib.use("Agg")
import xrt.backends.raycing as raycing
import xrt.backends.raycing.sources as rs
import xrt.backends.raycing.screens as rsc
import xrt.backends.raycing.run as rr
import xrt.plotter as xrtp
import xrt.runner as xrtr

sourceType = 'u'
suffix = '-U_code'
isInternalSource = True  # xrt source or (Urgent or WS)
limitsFSM0X = 'symmetric'
limitsFSM0Z = 'symmetric'
R0 = 25000.
E00 = 0.002

if sourceType == 'u':
    whose = '_xrt' if isInternalSource else '_urgent'
    pprefix = '1'+sourceType+whose
    Source = rs.Undulator if isInternalSource else rs.UndulatorUrgent
    kwargs = dict(
        period=30., K=1.45, n=40, eE=3., eI=0.5,
        xPrimeMax=0.25, zPrimeMax=0.25, eSigmaX=48.65, eSigmaZ=6.197,
        #uniformRayDensity=True,
        #R0=R0,
        eEpsilonX=0.263, eEpsilonZ=0.008)
#    xlimits = [-1, 1]
#    zlimits = [-1, 1]
#    xlimitsZoom = [-0.2, 0.2]
#    zlimitsZoom = [-0.2, 0.2]
    xlimits = [-5, 5]
    zlimits = [-5, 5]
    xlimitsZoom = [-1, 1]
    zlimitsZoom = [-1, 1]
    xPrimelimits = [-0.3, 0.3]
    if isInternalSource:
#        kwargs['distE'] = 'BW'
#        kwargs['eEspread'] = 8e-4
        kwargs['xPrimeMaxAutoReduce'] = False
        kwargs['zPrimeMaxAutoReduce'] = False
        kwargs['targetOpenCL'] = (0, 0)
        kwargs['precisionOpenCL'] = 'float64'
elif sourceType == 'THzU':
    R0 = 0.5*800*3 + 100
    whose = '_xrt' if isInternalSource else '_ws'
    pprefix = '2'+sourceType+whose
    Source = rs.Undulator if isInternalSource else rs.WigglerWS
    kwargs = dict(period=800., K=78.5, n=3, eE=1., eI=0.5,
                  uniformRayDensity=True,  # eEspread=0.001,
                  gIntervals=3,
                  eEpsilonX=0.0, eEpsilonZ=0.00,
                  R0=R0,
                  targetOpenCL=(0, 0),
                  precisionOpenCL='float64',
                  xPrimeMax=0.35, zPrimeMax=0.35)
    #kwargs['xPrimeMaxAutoReduce'] = True
    #kwargs['zPrimeMaxAutoReduce'] = False
    xlimits = [-20, 20]
    zlimits = [-20, 20]
    xPrimelimits = [-2.3, 2.3]
    xlimitsZoom = [-5, 5]
    zlimitsZoom = [-5, 5]
    limitsFSM0X = [-1000, 1000]
    limitsFSM0Z = [-100, 100]
elif sourceType == 'w':
    whose = '_xrt' if isInternalSource else '_ws'
    pprefix = '3'+sourceType+whose
    Source = rs.Wiggler if isInternalSource else rs.WigglerWS
    kwargs = dict(period=80., K=13., n=10, eE=3., xPrimeMax=5, zPrimeMax=0.3)
    xlimits = [-40, 40]
    zlimits = [-20, 20]
    xlimitsZoom = [-8, 8]
    zlimitsZoom = [-4, 4]
    xPrimelimits = [-2.3, 2.3]
    limitsFSM0X = [-1000, 1000]
    limitsFSM0Z = [-100, 100]
elif sourceType == 'bm':
    whose = '_xrt' if isInternalSource else '_ws'
    pprefix = '4'+sourceType+whose
    Source = rs.BendingMagnet if isInternalSource else rs.BendingMagnetWS
    kwargs = dict(B0=1.7, eE=3., xPrimeMax=5, zPrimeMax=0.3)
    xlimits = [-40, 40]
    zlimits = [-20, 20]
    xlimitsZoom = [-8, 8]
    zlimitsZoom = [-4, 4]
    xPrimelimits = None  # [-0.65, 0.65]
    limitsFSM0X = [-500, 500]
    limitsFSM0Z = [-20, 20]
elif sourceType == 'eu':
    whose = '_xrt' if isInternalSource else '_urgent'
    pprefix = '5'+sourceType+whose
    Source = rs.Wiggler if isInternalSource else rs.UndulatorUrgent
    kwargs = dict(
        period=30., Ky=1.45, Kx=1.45, n=40, eE=3., eI=0.5,
        xPrimeMax=0.25, zPrimeMax=0.25, eSigmaX=48.65, eSigmaZ=6.197,
        eEpsilonX=0.263, eEpsilonZ=0.008)
    if isInternalSource:
        kwargs['phaseDeg'] = 90
        kwargs['xPrimeMaxAutoReduce'] = False
        kwargs['zPrimeMaxAutoReduce'] = False
        kwargs['targetOpenCL'] = (0, 0)
    xlimits = [-5, 5]
    zlimits = [-5, 5]
    xPrimelimits = [-0.3, 0.3]
elif sourceType == 'wu':  # wiggler by undulator code
    whose = '_xrt' if isInternalSource else '_ws'
    pprefix = '6'+sourceType+whose
    Source = rs.Undulator if isInternalSource else rs.WigglerWS
    kwargs = dict(period=80., K=13., n=10, eE=3., xPrimeMax=5, zPrimeMax=0.3)
    xlimits = [-40, 40]
    zlimits = [-20, 20]
    xlimitsZoom = [-5, 5]
    zlimitsZoom = [-5, 5]
    kwargs['uniformRayDensity'] = True
    kwargs['gIntervals'] = 99
    kwargs['targetOpenCL'] = (0, 0)
    kwargs['precisionOpenCL'] = 'float64'
    kwargs['zPrimeMaxAutoReduce'] = False
    xPrimelimits = [-2.3, 2.3]
    limitsFSM0X = [-1000, 1000]
    limitsFSM0Z = [-100, 100]
else:
    raise ValueError('Unknown source type!')

if False:  # zero source size:
    kwargs['eSigmaX'] = 1e-3
    kwargs['eSigmaZ'] = 1e-3
    kwargs['eEpsilonX'] = 0
    kwargs['eEpsilonZ'] = 0
    eEpsilonC = '0'
else:
    eEpsilonC = 'n'

eUnit = 'eV'

#prefix, eMinRays, eMaxRays, eUnit =\
#    pprefix+'1-{0}-narrowE-'.format(eEpsilonC), E00*0.5, E00*3.5*3, 'meV'
#prefix, eMinRays, eMaxRays = pprefix+'2-{0}-smallerE-'.format(eEpsilonC), \
#    1500, 7500
prefix, eMinRays, eMaxRays = pprefix+'3-{0}-monoE-BMW-'.format(eEpsilonC), \
    6600, 7200
#prefix, eMinRays, eMaxRays = pprefix+'3-{0}-wideE-'.format(eEpsilonC), \
#    36600, 37200
#prefix, eMinRays, eMaxRays = pprefix+'4-{0}-far{1:02.0f}m-E0-'.format(
#    eEpsilonC, R0*1e-3), 6900-0.01, 6900+0.01
kwargs['eMin'] = eMinRays
kwargs['eMax'] = eMaxRays
if Source == rs.UndulatorUrgent:
    kwargs['processes'] = 'half'


def build_beamline(nrays=1e5):
    beamLine = raycing.BeamLine()
    Source(beamLine, eN=1000, nx=40, nz=20, nrays=nrays, **kwargs)
    beamLine.fsm0 = rsc.Screen(beamLine, 'FSM0', (0, 0, 0))
    beamLine.fsm1 = rsc.Screen(beamLine, 'FSM1', (0, R0, 0))
    return beamLine


def run_process(beamLine):
    startTime = time.time()
    beamSource = beamLine.sources[0].shine()
    print 'shine time = {0}s'.format(time.time() - startTime)
    beamFSM0 = beamLine.fsm0.expose(beamSource)
    beamFSM1 = beamLine.fsm1.expose(beamSource)
    outDict = {'beamSource': beamSource,
               'beamFSM0': beamFSM0, 'beamFSM1': beamFSM1}
    return outDict

rr.run_process = run_process


def main():
    beamLine = build_beamline()
    plots = []
    plotsE = []

    xaxis = xrtp.XYCAxis(r'$x$', 'mm', limits=xlimits)
    yaxis = xrtp.XYCAxis(r'$z$', 'mm', limits=zlimits)
    caxis = xrtp.XYCAxis('energy', eUnit, fwhmFormatStr=None)
    plot = xrtp.XYCPlot(
        'beamFSM1', (1,), xaxis=xaxis, yaxis=yaxis, caxis=caxis,
        aspect='auto', title='total flux')
    plot.caxis.fwhmFormatStr = None
    plot.saveName = prefix + '1TotalFlux' + suffix + '.png'
    plots.append(plot)
    plotsE.append(plot)

    xaxis = xrtp.XYCAxis(r'$x$', 'mm', limits=xlimitsZoom)
    yaxis = xrtp.XYCAxis(r'$z$', 'mm', limits=zlimitsZoom)
    caxis = xrtp.XYCAxis('energy', eUnit, fwhmFormatStr=None)
    plot = xrtp.XYCPlot(
        'beamFSM1', (1,), xaxis=xaxis, yaxis=yaxis, caxis=caxis,
        aspect='auto', title='total flux zoom')
    plot.caxis.fwhmFormatStr = None
    plot.saveName = prefix + '1TotalFluxZoom' + suffix + '.png'
    plots.append(plot)
    plotsE.append(plot)

    xaxis = xrtp.XYCAxis(r'$x$', 'mm', limits=xlimits)
    yaxis = xrtp.XYCAxis(r'$z$', 'mm', limits=zlimits)
    caxis = xrtp.XYCAxis('energy', eUnit, fwhmFormatStr=None)
    plot = xrtp.XYCPlot(
        'beamFSM1', (1,), xaxis=xaxis, yaxis=yaxis, caxis=caxis,
        fluxKind='s', aspect='auto', title='horizontal polarization flux')
    plot.caxis.fwhmFormatStr = None
    plot.saveName = prefix + '2horizFlux' + suffix + '.png'
    plots.append(plot)
    plotsE.append(plot)

    xaxis = xrtp.XYCAxis(r'$x$', 'mm', limits=xlimitsZoom)
    yaxis = xrtp.XYCAxis(r'$z$', 'mm', limits=zlimitsZoom)
    caxis = xrtp.XYCAxis('energy', eUnit, fwhmFormatStr=None)
    plot = xrtp.XYCPlot(
        'beamFSM1', (1,), xaxis=xaxis, yaxis=yaxis, caxis=caxis,
        fluxKind='s', aspect='auto', title='horizontal polarization flux zoom')
    plot.caxis.fwhmFormatStr = None
    plot.saveName = prefix + '2horizFluxZoom' + suffix + '.png'
    plots.append(plot)
    plotsE.append(plot)

    xaxis = xrtp.XYCAxis(r'$x$', 'mm', limits=xlimits)
    yaxis = xrtp.XYCAxis(r'$z$', 'mm', limits=zlimits)
    caxis = xrtp.XYCAxis('energy', eUnit, fwhmFormatStr=None)
    plot = xrtp.XYCPlot(
        'beamFSM1', (1,), xaxis=xaxis, yaxis=yaxis, caxis=caxis,
        fluxKind='p', aspect='auto', title='vertical polarization flux')
    plot.caxis.fwhmFormatStr = None
    plot.saveName = prefix + '3vertFlux' + suffix + '.png'
    plots.append(plot)
    plotsE.append(plot)

    xaxis = xrtp.XYCAxis(r'$x$', 'mm', limits=xlimitsZoom)
    yaxis = xrtp.XYCAxis(r'$z$', 'mm', limits=zlimitsZoom)
    caxis = xrtp.XYCAxis('energy', eUnit, fwhmFormatStr=None)
    plot = xrtp.XYCPlot(
        'beamFSM1', (1,), xaxis=xaxis, yaxis=yaxis, caxis=caxis,
        fluxKind='p', aspect='auto', title='vertical polarization flux zoom')
    plot.caxis.fwhmFormatStr = None
    plot.saveName = prefix + '3vertFluxZoom' + suffix + '.png'
    plots.append(plot)
    plotsE.append(plot)

    xaxis = xrtp.XYCAxis(r'$x$', 'mm', limits=xlimits)
    yaxis = xrtp.XYCAxis(r'$z$', 'mm', limits=zlimits)
    plot = xrtp.XYCPlot(
        'beamFSM1', (1,), xaxis=xaxis, yaxis=yaxis,
        caxis=xrtp.XYCAxis('degree of polarization', '',
                           data=raycing.get_polarization_degree,
                           limits=[0.95, 1.0005]),
        aspect='auto', title='degree of polarization')
    plot.saveName = prefix + '4DegPol' + suffix + '.png'
    plot.caxis.fwhmFormatStr = None
    plots.append(plot)

    xaxis = xrtp.XYCAxis(r'$x$', 'mm', limits=xlimitsZoom)
    yaxis = xrtp.XYCAxis(r'$z$', 'mm', limits=zlimitsZoom)
    plot = xrtp.XYCPlot(
        'beamFSM1', (1,), xaxis=xaxis, yaxis=yaxis,
        caxis=xrtp.XYCAxis('degree of polarization', '',
                           data=raycing.get_polarization_degree,
                           limits=[0.95, 1.0005]),
        aspect='auto', title='degree of polarization zoom')
    plot.saveName = prefix + '4DegPolZoom' + suffix + '.png'
    plot.caxis.fwhmFormatStr = None
    plots.append(plot)

    xaxis = xrtp.XYCAxis(r'$x$', 'mm', limits=xlimits)
    yaxis = xrtp.XYCAxis(r'$z$', 'mm', limits=zlimits)
    plot = xrtp.XYCPlot(
        'beamFSM1', (1,), xaxis=xaxis, yaxis=yaxis,
        caxis=xrtp.XYCAxis('circular polarization rate', '',
                           data=raycing.get_circular_polarization_rate,
                           limits=[-1, 1]),
        aspect='auto', title='circular polarization rate')
    plot.saveName = prefix + '5CircPolRate' + suffix + '.png'
    plot.caxis.fwhmFormatStr = None
    plots.append(plot)

    xaxis = xrtp.XYCAxis(r'$x$', 'mm', limits=xlimitsZoom)
    yaxis = xrtp.XYCAxis(r'$z$', 'mm', limits=zlimitsZoom)
    plot = xrtp.XYCPlot(
        'beamFSM1', (1,), xaxis=xaxis, yaxis=yaxis,
        caxis=xrtp.XYCAxis('circular polarization rate', '',
                           data=raycing.get_circular_polarization_rate,
                           limits=[-1, 1]),
        aspect='auto', title='circular polarization rate zoom')
    plot.saveName = prefix + '5CircPolRateZoom' + suffix + '.png'
    plot.caxis.fwhmFormatStr = None
    plots.append(plot)

    xaxis = xrtp.XYCAxis(r'$y$', 'mm', bins=256)
    yaxis = xrtp.XYCAxis(r'$x$', '$\mu$m', limits='symmetric')
    caxis = xrtp.XYCAxis('energy', eUnit, fwhmFormatStr=None)
    plot = xrtp.XYCPlot(
        'beamSource', (1,), xaxis=xaxis, yaxis=yaxis, caxis=caxis,
        aspect='auto', title='YX source cross-section')
    plot.saveName = prefix + 'crossectionYX' + suffix + '.png'
    plot.caxis.fwhmFormatStr = None
    plots.append(plot)
    plotsE.append(plot)

    xaxis = xrtp.XYCAxis(r'$y$', 'mm', bins=256)
    yaxis = xrtp.XYCAxis(r'$z$', '$\mu$m', limits='symmetric')
    caxis = xrtp.XYCAxis('energy', eUnit, fwhmFormatStr=None)
    plot = xrtp.XYCPlot(
        'beamSource', (1,), xaxis=xaxis, yaxis=yaxis, caxis=caxis,
        aspect='auto', title='YZ source cross-section')
    plot.saveName = prefix + 'crossectionYZ' + suffix + '.png'
    plot.caxis.fwhmFormatStr = None
    plots.append(plot)
    plotsE.append(plot)

    xaxis = xrtp.XYCAxis(r'$x$', '$\mu$m', limits=limitsFSM0X)
    yaxis = xrtp.XYCAxis(r'$z$', '$\mu$m', limits=limitsFSM0Z)
    caxis = xrtp.XYCAxis('energy', eUnit, fwhmFormatStr=None)
    plot = xrtp.XYCPlot(
        'beamFSM0', (1,), xaxis=xaxis, yaxis=yaxis, caxis=caxis,
        aspect='auto', title='image at 0')
    plot.saveName = prefix + 'fsm0' + suffix + '.png'
    plot.caxis.fwhmFormatStr = None
    plots.append(plot)
    plotsE.append(plot)

    beam = 'beamFSM0'
#    beam = 'beamSource'
    xaxis = xrtp.XYCAxis(r'$x$', '$\mu$m', limits=limitsFSM0X)
    yaxis = xrtp.XYCAxis(r"$x'$", 'mrad', limits=xPrimelimits)
    caxis = xrtp.XYCAxis('energy', eUnit, fwhmFormatStr=None)
    plot = xrtp.XYCPlot(
        beam, (1,), xaxis=xaxis, yaxis=yaxis, caxis=caxis,
        aspect='auto', title='horizontal phase space')
    plot.saveName = prefix + 'horPhaseSpace' + suffix + '.png'
    plot.caxis.fwhmFormatStr = None
    plots.append(plot)
    plotsE.append(plot)

    xaxis = xrtp.XYCAxis(r'$x$', '$\mu$m', limits=[-80, 80])
    yaxis = xrtp.XYCAxis(r"$x'$", 'mrad', limits=[-0.15, 0.15])
    caxis = xrtp.XYCAxis('energy', eUnit, fwhmFormatStr=None)
    plot = xrtp.XYCPlot(
        beam, (1,), xaxis=xaxis, yaxis=yaxis, caxis=caxis,
        aspect='auto', title='horizontal phase space zoomed')
    plot.saveName = prefix + 'horPhaseSpaceZoom' + suffix + '.png'
    plot.caxis.fwhmFormatStr = None
    plots.append(plot)
    plotsE.append(plot)

    for plot in plotsE:
        f = plot.caxis.factor
        plot.caxis.limits = eMinRays*f, eMaxRays*f
    for plot in plots:
        plot.xaxis.fwhmFormatStr = '%.2f'
        plot.yaxis.fwhmFormatStr = '%.2f'
        plot.fluxFormatStr = '%.2p'

    def afterScript():
#        return
        import os
        import pickle
        flux = [plot.intensity, plot.nRaysAll, plot.nRaysAcceptedTimesI,
                plot.nRaysSeeded]
        cwd = os.getcwd()
        pickleName = os.path.join(cwd, prefix+'.pickle')
        with open(pickleName, 'wb') as f:
            pickle.dump((flux, plot.caxis.binEdges, plot.caxis.total1D), f, -1)

    xrtr.run_ray_tracing(plots, repeats=1, beamLine=beamLine)

#this is necessary to use multiprocessing in Windows, otherwise the new Python
#contexts cannot be initialized:
if __name__ == '__main__':
    main()
