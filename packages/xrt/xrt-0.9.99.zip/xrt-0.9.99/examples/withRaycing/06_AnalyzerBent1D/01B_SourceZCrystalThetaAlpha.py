﻿# -*- coding: utf-8 -*-
r"""
This example is a complete study of a crystal analyzer. The generator
``plot_generator()`` is rather complex and therefore needs some explanation.
The inner loop changes the source type. After a flat-energy source has been
ray-traced (after ``yield``), the widths of *z* and energy distributions are
saved. Then a single line source is ray-traced and provides the width of *z*
distribution. From these 3 numbers we calculate energy resolution and, as a
check, ray-trace a third source with 7 energy lines with a spacing equal to the
previously calculated energy resolution. There are 3 outer loops for various
asymmetry angles, Bragg angles and crystal types. These loops are additionally
controlled by masks (``crystalsMask``, ``thetaMask``) having zeros or ones to
switch off/on the corresponding angles or crystals. The source sizes, axis
limits, number of iterations etc. were determined experimentally and are given
by lists in the upper part of the script. The outputs are the plots and a text
file with the resulted energy resolutions."""
__author__ = "Konstantin Klementiev"
__date__ = "27 Aug 2013"
import sys
sys.path.append(r"c:\Ray-tracing")
#sys.path.append(r"/media/sf_Ray-tracing")
import math
import numpy as np
#import matplotlib as mpl

import xrt.backends.raycing as raycing
import xrt.backends.raycing.sources as rs
#import xrt.backends.raycing.apertures as ra
import xrt.backends.raycing.oes as roe
import xrt.backends.raycing.run as rr
import xrt.backends.raycing.materials as rm
import xrt.backends.raycing.screens as rsc

import xrt.plotter as xrtp
import xrt.runner as xrtr

crystalMaterial = 'Si'
if crystalMaterial == 'Si':
    d111 = 3.1354161  # Si
elif crystalMaterial == 'Ge':
    d111 = 3.2662725  # Ge
else:
    raise
orders = (1, 4, 8, 12)
crystals = [rm.CrystalDiamond((i, i, i), d111/i, elements=crystalMaterial)
            for i in orders]
crystalsMask = (0, 1, 0, 0)
numiters = [24, 2560, 1280, 5120]  # @crysals
#numiters = [8, 8, 32, 128]# @crysals

R = 500.  # mm
isJohansson = True

if isJohansson:
    Rm = R
else:
    Rm = 2. * R

beamV = 0.1/2.35,
beamH = 0.1/2.35
dxCrystal = 100.
dyCrystal = 100.

yAxesLim = 0.1,  # @beamV
if not isJohansson:
    bentName = '1D-01b'
    Cylinder = roe.JohannCylinder
    analyzerName = 'JohannAnalyzer'
    eAxesFlat = [[6.0e-3, 5.0e-3, 5.0e-3, 3.2e-3],
                 [1.2e-3, 9.6e-4, 9.6e-4, 9.6e-4],
                 [1.0e-3, 6.4e-4, 6.4e-4, 5.0e-4],
                 [6.0e-4, 4.4e-4, 4.4e-4, 4.0e-4],
                 [2.0e-4, 8.0e-5, 8.0e-5, 8.0e-5]]
    yAxesLine = [0.08, 0.08, 0.015, 0.006]  # @crysals
else:  # Johansson
    bentName = '1D-02gb'
    Cylinder = roe.JohanssonCylinder
    analyzerName = 'JohanssonAnalyzer'
    eAxesFlat = [[4.0e-3, 3.0e-3, 2.0e-3, 2.0e-3],
                 [6.0e-4, 3.0e-4, 3.0e-4, 3.0e-4],
                 [4.0e-4, 3.0e-4, 1.5e-4, 1.5e-4],
                 [3.0e-4, 1.2e-4, 9.0e-5, 7.0e-5],
                 [2.0e-4, 5.0e-5, 5.0e-5, 4.0e-5]]
    yAxesLine = [0.1, 0.045, 0.007, 0.004]  # @crysals

thetasDegree = 10., 30., 40., 60., 80.,  # degree
thetaMask = 0, 0, 1, 1, 1
alphasDegree = 0.,  # asymmetry angle, degree


def build_beamline(nrays=raycing.nrays):
    beamLine = raycing.BeamLine(azimuth=0, height=0)
    rs.GeometricSource(
        beamLine, 'GeometricSource', nrays=nrays, dx=beamH, dy=0,
        dz=0.05, distxprime='flat', distzprime='flat', polarization=None)
    beamLine.analyzer = Cylinder(
        beamLine, analyzerName, surface=('',), Rm=Rm,
        limPhysX=(-dxCrystal/2, dxCrystal/2),
        limPhysY=(-dyCrystal/2, dyCrystal/2))
    beamLine.detector = rsc.Screen(beamLine, 'Detector')
    return beamLine


def run_process(beamLine):
    beamSource = beamLine.sources[0].shine()
    beamAnalyzerGlobal, beamAnalyzerLocal = \
        beamLine.analyzer.reflect(beamSource)
    beamDetector = beamLine.detector.expose(beamAnalyzerGlobal)
    outDict = {'beamSource': beamSource,
               'beamAnalyzerGlobal': beamAnalyzerGlobal,
               'beamAnalyzerLocal': beamAnalyzerLocal,
               'beamDetector': beamDetector
               }
    return outDict
rr.run_process = run_process


def main():
    beamLine = build_beamline()
    fwhmFormatStrE = '%.2f'
    plots = []
    plotsAnalyzer = []
    plotsDetector = []
    plotsE = []
    limXCrystal = -dxCrystal/2 - 10, dxCrystal/2 + 10
    limYCrystal = -dyCrystal/2 - 10, dyCrystal/2 + 10
    limXDetector = -(dxCrystal + 1), dxCrystal + 1

#    plotAnC = xrtp.XYCPlot('beamAnalyzerLocal', (1,2,3,-1),
#      xaxis=xrtp.XYCAxis(
#          r'$x$', 'mm', 1.0, limits=limXCrystal, bins=400, ppb=1),
#      yaxis=xrtp.XYCAxis(
#           r'$y$', 'mm', 1.0, limits=limYCrystal, bins=400, ppb=1),
#      caxis='category', title='xtal_footprint', oe=beamLine.analyzer)
#    plotsAnalyzer.append(plotAnC)

    plotAnE = xrtp.XYCPlot(
        'beamAnalyzerLocal', (1,), aspect='auto',
        xaxis=xrtp.XYCAxis(r'$x$', 'mm', limits=limXCrystal, bins=400, ppb=1),
        yaxis=xrtp.XYCAxis(r'$y$', 'mm', limits=limYCrystal, bins=400, ppb=1),
        caxis=xrtp.XYCAxis('energy', 'eV', fwhmFormatStr='%.2f',
                           bins=200, ppb=2),
        title='xtal_E', oe=beamLine.analyzer)
    plotAnE.caxis.fwhmFormatStr = fwhmFormatStrE
    plotAnE.caxis.invertAxis = True
    plotAnE.textPanel = plotAnE.fig.text(
        0.88, 0.85, '', transform=plotAnE.fig.transFigure, size=14, color='r',
        ha='center')
    plotsAnalyzer.append(plotAnE)
    plotsE.append(plotAnE)

#    plot = xrtp.XYCPlot('beamAnalyzerLocal', (1,),
#      xaxis=xrtp.XYCAxis(r'$x$', 'mm', limits=limXCrystal, bins=400, ppb=1),
#      yaxis=xrtp.XYCAxis(r'$y$', 'mm', limits=limYCrystal, bins=400, ppb=1),
#      caxis=xrtp.XYCAxis('degree of polarization', '', bins=200, ppb=2,
#      data=raycing.get_polarization_degree, limits=[0, 1]),
#      title='xtal_DegOfPol', oe=beamLine.analyzer)
#    plot.textPanel = plot.fig.text(0.88, 0.85, '',
#      transform=plot.fig.transFigure, size=14, color='r', ha='center')
#    plotsAnalyzer.append(plot)
#
#    plot = xrtp.XYCPlot('beamAnalyzerLocal', (1,),
#      xaxis=xrtp.XYCAxis(r'$x$', 'mm', limits=limXCrystal, bins=400, ppb=1),
#      yaxis=xrtp.XYCAxis(r'$y$', 'mm', limits=limYCrystal, bins=400, ppb=1),
#      caxis=xrtp.XYCAxis('circular polarization rate', '', bins=200, ppb=2,
#      data=raycing.get_circular_polarization_rate, limits=[-1, 1]),
#      title='xtal_CircPol', oe=beamLine.analyzer)
#    plot.textPanel = plot.fig.text(0.88, 0.85, '',
#      transform=plot.fig.transFigure, size=14, color='r', ha='center')
#    plotsAnalyzer.append(plot)
#
#    plot = xrtp.XYCPlot('beamAnalyzerLocal', (1,),
#      xaxis=xrtp.XYCAxis(r'$x$', 'mm', limits=limXCrystal, bins=400, ppb=1),
#      yaxis=xrtp.XYCAxis(r'$y$', 'mm', limits=limYCrystal, bins=400, ppb=1),
#      caxis=xrtp.XYCAxis('ratio of ellipse axes', '', bins=200, ppb=2,
#      data=raycing.get_ratio_ellipse_axes, limits=[-1, 1]),
#      title='xtal_PolAxes', oe=beamLine.analyzer)
#    plot.textPanel = plot.fig.text(0.88, 0.85, '',
#      transform=plot.fig.transFigure, size=14, color='r', ha='center')
#    plotsAnalyzer.append(plot)
#
#    plot = xrtp.XYCPlot('beamAnalyzerLocal', (1,),
#      xaxis=xrtp.XYCAxis(r'$x$', 'mm', limits=limXCrystal, bins=400, ppb=1),
#      yaxis=xrtp.XYCAxis(r'$y$', 'mm', limits=limYCrystal, bins=400, ppb=1),
#      caxis=xrtp.XYCAxis('phase shift', '', bins=200, ppb=2,
#      data=raycing.get_phase_shift, limits=[-1, 1]),#in units of pi!
#      title='xtal_Phase', oe=beamLine.analyzer)
#    plot.textPanel = plot.fig.text(0.88, 0.85, '',
#      transform=plot.fig.transFigure, size=14, color='r', ha='center')
#    formatter = mpl.ticker.FormatStrFormatter('%g' + r'$ \pi$')
#    plot.ax1dHistE.yaxis.set_major_formatter(formatter)
#    plotsAnalyzer.append(plot)

    plotDetE = xrtp.XYCPlot(
        'beamDetector', (1,), aspect='auto',
        xaxis=xrtp.XYCAxis(r'$x$', 'mm', limits=limXDetector,
                           fwhmFormatStr='%.2f'),
        yaxis=xrtp.XYCAxis(r'$z$', 'mm', limits=[-0.25, 0.25],
                           fwhmFormatStr='%.2f'),
        title='det_E')
    plotDetE.caxis.fwhmFormatStr = fwhmFormatStrE
    plotDetE.caxis.invertAxis = True
    plotDetE.textPanel = plotDetE.fig.text(
        0.88, 0.8, '', transform=plotDetE.fig.transFigure, size=14, color='r',
        ha='center')
    plotsDetector.append(plotDetE)
    plotsE.append(plotDetE)

    plot = xrtp.XYCPlot(
        'beamDetector', (1,), aspect='auto',
        xaxis=xrtp.XYCAxis(r'$x$', 'mm', limits=limXDetector,
                           fwhmFormatStr='%.2f'),
        yaxis=xrtp.XYCAxis(r'$z$', 'mm', limits=[-0.25, 0.25],
                           fwhmFormatStr='%.2f'),
        caxis=xrtp.XYCAxis('degree of polarization', '',
                           data=raycing.get_polarization_degree,
                           limits=[-0.01, 1.01]),
        title='det_DegOfPol')
    plot.textPanel = plot.fig.text(
        0.88, 0.8, '', transform=plot.fig.transFigure, size=14, color='r',
        ha='center')
    plotsDetector.append(plot)
#
#    plot = xrtp.XYCPlot('beamDetector', (1,), aspect='auto',
#      xaxis=xrtp.XYCAxis(r'$x$', 'mm', limits=limXDetector,
#                         fwhmFormatStr='%.2f'),
#      yaxis=xrtp.XYCAxis(r'$z$', 'mm', limits=[-0.25, 0.25],
#                         fwhmFormatStr='%.2f'),
#      caxis=xrtp.XYCAxis('circular polarization rate', '',
#                         data=raycing.get_circular_polarization_rate,
#                         limits=[-1, 1]),
#      title='det_CircPol')
#    plot.textPanel = plot.fig.text(0.88, 0.8, '',
#      transform=plot.fig.transFigure, size=14, color='r', ha='center')
#    plotsDetector.append(plot)
#
#    plot = xrtp.XYCPlot('beamDetector', (1,), aspect='auto',
#      xaxis=xrtp.XYCAxis(r'$x$', 'mm', limits=limXDetector,
#                         fwhmFormatStr='%.2f'),
#      yaxis=xrtp.XYCAxis(r'$z$', 'mm', limits=[-0.25, 0.25],
#                         fwhmFormatStr='%.2f'),
#      caxis=xrtp.XYCAxis('ratio of ellipse axes', '',
#      data=raycing.get_ratio_ellipse_axes, limits=[-1, 1]),
#      title='det_PolAxes')
#    plot.textPanel = plot.fig.text(0.88, 0.8, '',
#      transform=plot.fig.transFigure, size=14, color='r', ha='center')
#    plotsDetector.append(plot)
#
#    plot = xrtp.XYCPlot('beamDetector', (1,), aspect='auto',
#      xaxis=xrtp.XYCAxis(r'$x$', 'mm', limits=limXDetector,
#                         fwhmFormatStr='%.2f'),
#      yaxis=xrtp.XYCAxis(r'$z$', 'mm', limits=[-0.25, 0.25],
#                         fwhmFormatStr='%.2f'),
#      caxis=xrtp.XYCAxis('phase shift', '',
#      data=raycing.get_phase_shift, limits=[-1, 1]),#in units of pi!
#      title='det_Phase')
#    plot.textPanel = plot.fig.text(0.88, 0.8, '',
#      transform=plot.fig.transFigure, size=14, color='r', ha='center')
#    formatter = mpl.ticker.FormatStrFormatter('%g' + r'$ \pi$')
#    plot.ax1dHistE.yaxis.set_major_formatter(formatter)
#    plotsDetector.append(plot)

    for plot in plotsAnalyzer:
        plots.append(plot)
    for plot in plotsDetector:
        plots.append(plot)

    fOut1 = open(crystalMaterial + bentName + '_long.txt', 'w')
    E0table = [[0 for ic in crystals] for it in thetasDegree]
    dEtable = [[0 for ic in crystals] for it in thetasDegree]
    rEtable = [[0 for ic in crystals] for it in thetasDegree]

    def plot_generator():
        for bvs, yAxisLim in zip(beamV, yAxesLim):
            beamLine.sources[0].dz = bvs
            bsname = 'h={0:03.0f}mum'.format(bvs*1e3)
            for icrystal, crystal in enumerate(crystals):
                if not crystalsMask[icrystal]:
                    continue
                numiter = numiters[icrystal]
                yAxisLine = yAxesLine[icrystal]
                if np.any(np.array(crystal.hkl) > 10):
                    hklSeparator = ','
                else:
                    hklSeparator = ''
                crystalLabel = '{0}{1[0]}{2}{1[1]}{2}{1[2]}'.format(
                    crystalMaterial, crystal.hkl, hklSeparator)
                beamLine.analyzer.surface = crystalLabel,
                plotAnE.draw_footprint_area()
#                plotAnC.draw_footprint_area()
                beamLine.analyzer.material = crystal
                for ithetaDegree, thetaDegree in enumerate(thetasDegree):
                    if not thetaMask[ithetaDegree]:
                        continue
                    theta = np.radians(thetaDegree)
                    sinTheta = np.sin(theta)
                    E0raw = rm.ch / (2 * crystal.d * sinTheta)
                    dTheta = crystal.get_dtheta_symmetric_Bragg(E0raw)
                    E0 = rm.ch / (2 * crystal.d * math.sin(theta + dTheta))
                    offsetE = round(E0, 2)
                    for alphaDegree in alphasDegree:
                        alpha = np.radians(alphaDegree)
                        beamLine.analyzer.set_alpha(alpha)
#                        b = math.sin(theta - alpha) / math.sin(theta + alpha)
                        p = 2. * R * math.sin(theta + alpha)
                        q = 2. * R * math.sin(theta - alpha)
                        sin2Theta = math.sin(2 * theta)
                        cos2Theta = math.cos(2 * theta)
                        yDet = p + q * cos2Theta
                        zDet = q * sin2Theta
                        pdp = 2. * R * math.sin(theta + alpha - dyCrystal/6/R)
                        beamLine.sources[0].dxprime = dxCrystal / pdp
                        beamLine.sources[0].dzprime = dyCrystal *\
                            math.sin(theta - alpha) / pdp
                        beamLine.analyzer.center = 0, p, 0
                        beamLine.analyzer.pitch = theta + alpha
                        beamLine.detector.center = 0, yDet, zDet
                        beamLine.detector.set_orientation(
                            z=(0, -sin2Theta, cos2Theta))

                        dELine, dzLine, dEFlat, dzFlat = 0, 0, 0, 1
#                        for isource in np.arange(3):
                        for isource in [-1, ]:
                            xrtr.runCardVals.repeats = numiter
                            for plot in plotsDetector:
                                plot.yaxis.limits = [-yAxisLim, yAxisLim]
                            if isource == 0 or isource == -1:  # flat or norm
#                                xrtr.runCardVals.repeats = 0
                                if isource == -1:
                                    eAxisFlat = 8e-4 * E0
                                    eAxisMin = E0 - 3*eAxisFlat/2
                                    eAxisMax = E0 + 3*eAxisFlat/2
                                else:
                                    eAxisFlat =\
                                        eAxesFlat[ithetaDegree][icrystal]
                                    eAxisMin = E0 * (1. - eAxisFlat)
                                    eAxisMax = E0 * (1. + eAxisFlat)
                                for plot in plotsE:
                                    if plot is None:
                                        continue
                                    plot.caxis.offset = offsetE
                                    plot.caxis.limits = [eAxisMin, eAxisMax]
                                tt = r'{0}{1}$\theta = {2:.0f}^\circ$'.format(
                                    crystalLabel, '\n', thetaDegree)
                                for plot in plots:
                                    if hasattr(plot, 'textPanel'):
                                        plot.textPanel.set_text(tt)
                                if isource == -1:
                                    beamLine.sources[0].distE = 'normal'
                                    beamLine.sources[0].energies =\
                                        E0, eAxisFlat/2.355
                                    sourcename = 'norm'
                                else:
                                    beamLine.sources[0].distE = 'flat'
                                    beamLine.sources[0].energies = \
                                        eAxisMin, eAxisMax
                                    sourcename = 'flat'
                            elif isource == 1:  # line
#                                xrtr.runCardVals.repeats = 0
                                beamLine.sources[0].distE = 'lines'
                                beamLine.sources[0].energies = E0,
                                sourcename = 'line'
                                for plot in plotsDetector:
                                    plot.yaxis.limits = [-yAxisLine, yAxisLine]
                            else:
#                                xrtr.runCardVals.repeats = 0
                                tt = (r'{0}{1}$\theta = {2:.0f}^\circ${1}' +
                                      r'$\delta E = ${3:.3f} eV').format(
                                    crystalLabel, '\n', thetaDegree, dELine)
                                for plot in plots:
                                    if hasattr(plot, 'textPanel'):
                                        plot.textPanel.set_text(tt)
                                beamLine.sources[0].distE = 'lines'
                                sourcename = '7lin'
                                for plot in plotsDetector:
                                    plot.yaxis.limits = [-dzLine*4, dzLine*4]
                                dEStep = dELine
                                beamLine.sources[0].energies = \
                                    [E0 + dEStep*i for i in range(-3, 4)]
                                eAxisMin = E0 - dEStep * 4
                                eAxisMax = E0 + dEStep * 4
                                for plot in plotsE:
                                    if plot is None:
                                        continue
                                    plot.caxis.limits = [eAxisMin, eAxisMax]

                            for plot in plots:
                                filename = '{0}-{1}-{2:.0f}-{3}-{4}'.format(
                                    bentName, crystalLabel, thetaDegree,
                                    plot.title, sourcename)
                                plot.saveName = filename + '.png'
                                plot.persistentName = filename + '.pickle'
                            yield

                            if isource == 0:
                                dzFlat = plotDetE.dy
                                dEFlat = plotDetE.dE
                                if (dzFlat == 0) or (dEFlat == 0)\
                                        or np.isnan(dzFlat) \
                                        or np.isnan(dEFlat):
                                    raise
                            elif isource == 1:
                                dzLine = plotDetE.dy
                                try:
                                    dELine = dzLine * dEFlat / dzFlat
                                except:
                                    print 'dzFlat={0}'.format(dzFlat)
                                    dELine = 0
                                outStr = ('{0}, {1}, {2}, {3}, {4}, {5}, ' +
                                          '{6}, {7}, {8}, {9}\n').format(
                                    bsname, crystalLabel, thetaDegree,
                                    alpha, E0, dzFlat, dEFlat, dzLine,
                                    dELine, dELine/E0)
                                print outStr
                                E0table[ithetaDegree][icrystal] = E0
                                dEtable[ithetaDegree][icrystal] = dELine
                                rEtable[ithetaDegree][icrystal] = dELine/E0
                                fOut1.write(outStr)

        fOut1.close()
        fOut2 = open(crystalMaterial + bentName + '_table.txt', 'w')
        for ithetaDegree, thetaDegree in enumerate(thetasDegree):
            outStr = (r'| {0:2.0f} |  *E* = {1[0]:.0f} eV       |  *E* = ' +
                      r'{1[1]:.0f} eV       |  *E* = {1[2]:.0f} eV       ' +
                      r'|  *E* = {1[3]:.0f} eV      |{2}').format(
                thetaDegree, E0table[ithetaDegree], '\n')
            fOut2.write(outStr)
            outStr = (r'|    | {0}={1[0]:.2f}eV={2[0]:.1e} *E* | {0}=' +
                      r'{1[1]:.2f}eV={2[1]:.1e} *E* | {0}={1[2]:.2f}eV=' +
                      r'{2[2]:.1e} *E* | {0}={1[3]:.2f}eV={2[3]:.1e} *E*' +
                      r' |{3}').format(bentName, dEtable[ithetaDegree],
                                       rEtable[ithetaDegree], '\n')
            fOut2.write(outStr)
        fOut2.close()

    xrtr.run_ray_tracing(plots, generator=plot_generator,
                         beamLine=beamLine, processes='all')

#this is necessary to use multiprocessing in Windows, otherwise the new Python
#contexts cannot be initialized:
if __name__ == '__main__':
    main()
