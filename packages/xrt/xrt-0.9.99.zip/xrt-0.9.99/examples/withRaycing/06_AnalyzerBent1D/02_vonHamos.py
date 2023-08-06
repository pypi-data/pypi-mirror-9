﻿# -*- coding: utf-8 -*-
"""
bla
"""
__author__ = "Konstantin Klementiev"
__date__ = "14 October 2014"
import sys
sys.path.append(r"c:\Ray-tracing")
#import math
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
    d111 = 3.1354161
elif crystalMaterial == 'Ge':
    d111 = 3.2662725
else:
    raise

crystal = rm.CrystalDiamond((4, 4, 4), d111/4, elements=crystalMaterial)
#numiter = 640
#numiter = 4000*4
numiter = 4000

Rm = 1e9  # meridional radius, mm
Rs = 1000  # tmp sagittal radius, mm
#Rs = 250  # tmp sagittal radius, mm
dphi = 0

beamV = 0.1/2.35  # vertical beam size
beamH = 0.1/2.35  # horizontal beam size

yAxesLim = 20

dxCrystal = 100.
dyCrystal = 100.
#dyCrystal = 50.
#dxCrystal = 300.
#dyCrystal = 70.

isDiced = False
yAxisLim = 32  # Mythen length = 64 mm
yAxisLine = 0.4
if isDiced:
    xAxisLim = 12
    facetKWargs = {'dxFacet': 1-0.05, 'dyFacet': 50.,
                   'dxGap': 0.05, 'dyGap': 0.}
    Toroid = roe.DicedJohannToroid
    analyzerName = crystalMaterial + 'vonHamosDiced'
else:
    xAxisLim = 5
    facetKWargs = {}
    Toroid = roe.JohannToroid
    analyzerName = crystalMaterial + 'vonHamos'

thetaDegree = 40

if isDiced:
    dphi = np.arcsin((facetKWargs['dxFacet'] + facetKWargs['dxGap']) / Rs)

if thetaDegree == 40:
    if Rs > 800:
        eAxisFlat = 7.5e-3  # @ 40 deg, R=1000
    else:
        eAxisFlat = 3e-2  # @ 40 deg
elif thetaDegree == 60:
    if Rs > 800:
        eAxisFlat = 6.8e-3  # @ 60 deg, R=1000
    else:
        eAxisFlat = 2.6e-2  # @ 60 deg
elif thetaDegree == 80:
    if Rs > 800:
        eAxisFlat = 2.6e-3  # @ 80 deg, R=1000
    else:
        eAxisFlat = 9.0e-3  # @ 80 deg
else:
    raise


def build_beamline(nrays=1e5):
    beamLine = raycing.BeamLine(azimuth=0, height=0)
    rs.GeometricSource(
        beamLine, 'GeometricSource', nrays=nrays, dx=beamH, dy=0,
        dz=beamV, distxprime='flat', distzprime='flat', polarization=None)
    beamLine.analyzer = Toroid(
        beamLine, analyzerName, surface=('',),
        limPhysX=(-dxCrystal/2, dxCrystal/2),
        limPhysY=(-dyCrystal/2, dyCrystal/2),
        Rm=Rm, Rs=Rs, shape='rect',
        #targetOpenCL=(0, 0),
        **facetKWargs)
    beamLine.detector = rsc.Screen(beamLine, 'Detector', z=(0, 0, 1))
#    beamLine.s1h = ra.RectangularAperture(
#        beamLine, 'horizontal. slit', 0, Rs-10.,
#        ('left', 'right'), [-0.1, 0.1])
    return beamLine


def run_process(beamLine):
    beamSource = beamLine.sources[0].shine()
#    beamLine.s1h.propagate(beamSource)
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


def align_spectrometer_Rs(beamLine, theta, Rs):
    sinTheta = np.sin(theta)
    cosTheta = np.cos(theta)
    sin2Theta = np.sin(2 * theta)
    p = Rs / sinTheta
    yDet = p * 2 * cosTheta**2
    zDet = p * sin2Theta

    beamLine.analyzer.center = 0, p, 0
    beamLine.analyzer.pitch = theta
    beamLine.detector.center = 0, yDet, zDet
    beamLine.detector.set_orientation(z=(0, cosTheta, sinTheta))

    beamLine.sources[0].dxprime = 1.1 * dxCrystal / p
    beamLine.sources[0].dzprime = dyCrystal * np.sin(theta) / p
    print 'theta={0}deg, Rs={1}mm: p={2}mm'.format(np.degrees(theta), Rs, p)


#def align_spectrometer_p(beamLine, theta, p):
#    sinTheta = np.sin(theta)
#    cosTheta = np.cos(theta)
#    sin2Theta = np.sin(2 * theta)
#    Rs = p * sinTheta
#    yDet = p * 2 * cosTheta**2
#    zDet = p * sin2Theta
#
#    beamLine.analyzer.center = 0, p, 0
#    beamLine.analyzer.Rs = Rs
#    beamLine.analyzer.pitch = theta
#    beamLine.detector.center = 0, yDet, zDet
#    beamLine.detector.set_orientation(z=(0, cosTheta, sinTheta))
#
#    beamLine.sources[0].dxprime = 1.1 * dxCrystal / p
#    beamLine.sources[0].dzprime = dyCrystal * np.sin(theta) / p
#    print 'theta={0}deg, p={1}mm: Rs={2}mm'.format(np.degrees(theta), p, Rs)


def stripe_number(beam):
    phi = np.arcsin(beam.x / Rs)
    return np.round(phi / dphi)


def main():
    beamLine = build_beamline()
    fwhmFormatStrE = '%.2f'
    plots = []
    plotsAnalyzer = []
    plotsDetector = []
    plotsE = []

    limits = [-dxCrystal/2 - 5, dxCrystal/2 + 5]
    plotAnE = xrtp.XYCPlot(
        'beamAnalyzerLocal', (1,),
        xaxis=xrtp.XYCAxis(r'$x$', 'mm', bins=400, ppb=1, limits=limits),
        yaxis=xrtp.XYCAxis(r'$y$', 'mm', bins=400, ppb=1, limits=limits),
        caxis=xrtp.XYCAxis('energy', 'eV', fwhmFormatStr='%.2f',
                           bins=200, ppb=2),
        title='xtal_E', oe=beamLine.analyzer, raycingParam=1000)
    plotAnE.caxis.fwhmFormatStr = fwhmFormatStrE
    plotAnE.textPanel = plotAnE.fig.text(
        0.88, 0.85, '', transform=plotAnE.fig.transFigure, size=14, color='r',
        ha='center')
    plotsAnalyzer.append(plotAnE)
    plotsE.append(plotAnE)

    if isDiced:
        plotAnS = xrtp.XYCPlot(
            'beamAnalyzerLocal', (1,),
            xaxis=xrtp.XYCAxis(r'$x$', 'mm', bins=400, ppb=1, limits=limits),
            yaxis=xrtp.XYCAxis(r'$y$', 'mm', bins=400, ppb=1, limits=limits),
            caxis=xrtp.XYCAxis('stripe number', '', data=stripe_number),
            title='xtal_stripes', oe=beamLine.analyzer, raycingParam=1000)
        plotAnS.textPanel = plotAnS.fig.text(
            0.88, 0.85, '', transform=plotAnS.fig.transFigure, size=14,
            color='r', ha='center')
        plotsAnalyzer.append(plotAnS)

    if isDiced:
        xMax = (facetKWargs['dxFacet']+1) / 2
        limits = [-xMax, xMax]
    else:
        limits = [-3, 3]
    plot = xrtp.XYCPlot(
        'beamAnalyzerLocal', (1,),
        xaxis=xrtp.XYCAxis(r'$x$', 'mm', limits=limits),
        yaxis=xrtp.XYCAxis(r'$y$', 'mm', limits=limits),
        caxis=xrtp.XYCAxis('energy', 'eV', fwhmFormatStr='%.2f'),
        title='xtal_E_zoom', oe=beamLine.analyzer, raycingParam=1000)
    plot.caxis.fwhmFormatStr = fwhmFormatStrE
    plot.textPanel = plot.fig.text(
        0.88, 0.8, '', transform=plot.fig.transFigure, size=14, color='r',
        ha='center')
    plotsAnalyzer.append(plot)
    plotsE.append(plot)

    if isDiced:
        plot = xrtp.XYCPlot(
            'beamAnalyzerLocal', (1,),
            xaxis=xrtp.XYCAxis(r'$x$', 'mm', limits=limits),
            yaxis=xrtp.XYCAxis(r'$y$', 'mm', limits=limits),
            caxis=xrtp.XYCAxis('stripe number', '', data=stripe_number),
            title='xtal_stripes_zoom', oe=beamLine.analyzer,
            raycingParam=1000)
        plot.textPanel = plot.fig.text(
            0.88, 0.8, '', transform=plot.fig.transFigure, size=14, color='r',
            ha='center')
        plotsAnalyzer.append(plot)

    plotDetE = xrtp.XYCPlot(
        'beamDetector', (1,), aspect='auto',
        xaxis=xrtp.XYCAxis(r'$x$', 'mm', fwhmFormatStr='%.3f'),
        yaxis=xrtp.XYCAxis(r'$z$', 'mm', fwhmFormatStr='%.3f'),
        title='det_E')
    plotDetE.xaxis.limits = -xAxisLim, xAxisLim
    plotDetE.yaxis.limits = -yAxisLim, yAxisLim
    plotDetE.caxis.fwhmFormatStr = fwhmFormatStrE
    plotDetE.textPanel = plotDetE.fig.text(
        0.88, 0.8, '', transform=plotDetE.fig.transFigure, size=14, color='r',
        ha='center')
    plotsDetector.append(plotDetE)
    plotsE.append(plotDetE)

    if isDiced:
        plotDetS = xrtp.XYCPlot(
            'beamDetector', (1,), aspect='auto',
            xaxis=xrtp.XYCAxis(r'$x$', 'mm', fwhmFormatStr='%.3f'),
            yaxis=xrtp.XYCAxis(r'$z$', 'mm', fwhmFormatStr='%.3f'),
            caxis=xrtp.XYCAxis('stripe number', '', data=stripe_number),
            beamC='beamAnalyzerLocal', title='det_stripes')
        plotDetS.xaxis.limits = -xAxisLim, xAxisLim
        plotDetS.yaxis.limits = -yAxisLim, yAxisLim
        plotDetS.textPanel = plotDetS.fig.text(
            0.88, 0.8, '', transform=plotDetS.fig.transFigure, size=14,
            color='r', ha='center')
        plotsDetector.append(plotDetS)

    for plot in plotsAnalyzer:
        plots.append(plot)
    for plot in plotsDetector:
        plots.append(plot)

    def plot_generator():
        hklSeparator = ',' if np.any(np.array(crystal.hkl) > 10) else ''
        crystalLabel = '{0}{1[0]}{2}{1[1]}{2}{1[2]}'.format(
            crystalMaterial, crystal.hkl, hklSeparator)
        beamLine.analyzer.surface = crystalLabel,
        for plot in plotsAnalyzer:
            plot.draw_footprint_area()
        beamLine.analyzer.material = crystal
        theta = np.radians(thetaDegree)
        align_spectrometer_Rs(beamLine, theta, Rs)

        sinTheta = np.sin(theta)
        E0raw = rm.ch / (2 * crystal.d * sinTheta)
        dTheta = crystal.get_dtheta_symmetric_Bragg(E0raw)
        E0 = rm.ch / (2 * crystal.d * np.sin(theta + dTheta))
        offsetE = round(E0, 3)

        dELine = 0
        dzLine = 0
#        for isource in np.arange(3):
        for isource in [-1, ]:
            xrtr.runCardVals.repeats = numiter
            if isource == 0 or isource == -1:  # flat or norm
#                xrtr.runCardVals.repeats = 0
                if isource == -1:
                    eAxisFlat = 8e-4 * E0
                    eAxisMin = E0 - 3*eAxisFlat/2
                    eAxisMax = E0 + 3*eAxisFlat/2
                else:
                    eAxisMin = E0 * (1 - eAxisFlat)
                    eAxisMax = E0 * (1 + eAxisFlat)
                for plot in plotsE:
                    if plot is None:
                        continue
                    plot.caxis.offset = int(round(offsetE, -2))
                    plot.caxis.limits = [eAxisMin, eAxisMax]
                tt = r'{0}{1}$\theta = {2:.0f}^\circ$'.format(
                    crystalLabel, '\n', thetaDegree)
                for plot in plots:
                    try:
                        plot.textPanel.set_text(tt)
                    except AttributeError:
                        pass
                if isource == -1:
                    beamLine.sources[0].distE = 'normal'
                    beamLine.sources[0].energies = E0, eAxisFlat/2.355
                    sourcename = 'norm'
                else:
                    beamLine.sources[0].distE = 'flat'
                    beamLine.sources[0].energies = eAxisMin, eAxisMax
                    sourcename = 'flat'
            elif isource == 1:  # line
#                xrtr.runCardVals.repeats = 0
                beamLine.sources[0].distE = 'lines'
                beamLine.sources[0].energies = E0,
                sourcename = 'line'
                for plot in plotsDetector:
                    plot.yaxis.limits = [-yAxisLine, yAxisLine]
            else:
#                xrtr.runCardVals.repeats = 2560*16L
                for plot in plotsDetector:
                    plot.xaxis.limits = -6, 6
                tt = (r'{0}{1}$\theta = {2:.0f}^\circ${1}$' +
                      '\delta E = ${3:.3f} eV').format(
                    crystalLabel, '\n', thetaDegree, dELine)
                for plot in plots:
                    try:
                        plot.textPanel.set_text(tt)
                    except AttributeError:
                        pass
                beamLine.sources[0].distE = 'lines'
                sourcename = '7lin'
                for plot in plotsDetector:
                    plot.yaxis.limits = [-dzLine*7, dzLine*7]
                dEStep = dELine
                beamLine.sources[0].energies = \
                    [E0 + dEStep * i for i in range(-3, 4)]
                eAxisMin = E0 - dEStep * 4
                eAxisMax = E0 + dEStep * 4
                for plot in plotsE:
                    if plot is None:
                        continue
                    plot.caxis.limits = [eAxisMin, eAxisMax]

            for plot in plots:
                filename = '{0}{1}-{2}-{3}'.format(
                    analyzerName, thetaDegree, plot.title, sourcename)
                plot.saveName = filename + '.png'
                plot.persistentName = filename + '.pickle'
            yield

            if isource == 0:
                dzFlat = plotDetE.dy
                dEFlat = plotDetE.dE
            elif isource == 1:
                dzLine = plotDetE.dy
                try:
                    dELine = dzLine * dEFlat / dzFlat
                except:
                    print 'dzFlat={0}'.format(dzFlat)
                    dELine = 0

    xrtr.run_ray_tracing(
        plots, generator=plot_generator, beamLine=beamLine, processes='all')

#this is necessary to use multiprocessing in Windows, otherwise the new Python
#contexts cannot be initialized:
if __name__ == '__main__':
    main()
