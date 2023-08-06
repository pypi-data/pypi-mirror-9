# -*- coding: utf-8 -*-
"""An example of using xrt with raycing backend."""
__author__ = "Konstantin Klementiev"
__date__ = "1 Mar 2012"
import sys
sys.path.append(r"c:\Ray-tracing")
import math
#import numpy as np

import xrt.backends.raycing as raycing
import xrt.backends.raycing.sources as rs
import xrt.backends.raycing.oes as roe
import xrt.backends.raycing.run as rr
import xrt.backends.raycing.materials as rm
import xrt.backends.raycing.screens as rsc

import xrt.plotter as xrtp
import xrt.runner as xrtr

E0 = 9000.
eLimits = E0, E0+2.5


def build_beamline(nrays=raycing.nrays):
    fixedExit = 15.

    beamLine = raycing.BeamLine(azimuth=0, height=0)
    rs.GeometricSource(
        beamLine, 'GeometricSource', (0, 0, -fixedExit),
        nrays=nrays, dx=5., dy=0, dz=5., dxprime=0., dzprime=0.,
        distE='flat', energies=eLimits, polarization='horizontal')

    p = 20000.
    si111 = rm.CrystalSi(hkl=(1, 1, 1), tK=-171+273.15)
    beamLine.dcm = roe.DCM(beamLine, 'DCM', (0, p - 2000, -fixedExit),
                           surface=('Si111',), material=(si111,))
    beamLine.dcm.bragg = math.asin(rm.ch / (2 * si111.d * E0))
    beamLine.dcm.cryst2perpTransl = fixedExit/2./math.cos(beamLine.dcm.bragg)

    beamLine.fsm1 = rsc.Screen(beamLine, 'FSM1', (0, p - 1000, 0))

    crystalDiamond = rm.CrystalDiamond((1, 1, 1), 2.0592872, elements='C',
                                       geom='Bragg reflected')
    beamLine.qwp = roe.OE(
        beamLine, 'QWP', (0, p, 0), material=(crystalDiamond,))
    theta0 = math.asin(rm.ch / (2 * crystalDiamond.d * (E0+0.4)))
    beamLine.qwp.pitch = theta0
    q = 50.

    beamLine.fsm2 = rsc.Screen(beamLine, 'FSM2', (0, p + q, 0))

    return beamLine


def run_process(beamLine):
    beamSource = beamLine.sources[0].shine()

    beamDCMglobal, beamDCMlocal1, beamDCMlocal2 =\
        beamLine.dcm.double_reflect(beamSource)
    beamFSM1 = beamLine.fsm1.expose(beamDCMglobal)

    beamQWPglobal, beamQWPlocal = beamLine.qwp.reflect(beamDCMglobal)
    beamFSM2 = beamLine.fsm2.expose(beamQWPglobal)

    outDict = {'beamSource': beamSource,
               'beamDCMglobal': beamDCMglobal,
               'beamDCMlocal1': beamDCMlocal1,
               'beamDCMlocal2': beamDCMlocal2,
               'beamFSM1': beamFSM1,
               'beamQWPglobal': beamQWPglobal,
               'beamQWPlocal': beamQWPlocal,
               'beamFSM2': beamFSM2
               }
    return outDict

rr.run_process = run_process


def main():
    prefix = '01-collimated-BR'
    beamLine = build_beamline()
    dE = beamLine.sources[0].energies[-1] - beamLine.sources[0].energies[0]
    midE = \
        (beamLine.sources[0].energies[-1] + beamLine.sources[0].energies[0])/2
    if dE < midE / 20.:
        fwhmFormatStrE = '%.2f'
        offsetE = E0
    else:
        fwhmFormatStrE = None
        offsetE = 0
    plots = []

    plot = xrtp.XYCPlot(
        'beamFSM1', (1,),
        xaxis=xrtp.XYCAxis(r'$x$', 'mm', limits=[-15, 15]),
        yaxis=xrtp.XYCAxis(r'$z$', 'mm', limits=[-15, 15]),
        ePos=1, title=beamLine.fsm1.name+'_E')
    plot.caxis.fwhmFormatStr = fwhmFormatStrE
    plot.caxis.limits = eLimits
    plot.caxis.offset = offsetE
    plot.textPanel = plot.fig.text(
        0.88, 0.8, '', transform=plot.fig.transFigure, size=14, color='r',
        ha='center')
    plots.append(plot)

    plot = xrtp.XYCPlot(
        'beamFSM2', (1,),
        xaxis=xrtp.XYCAxis(r'$x$', 'mm', limits=[-15, 15]),
        yaxis=xrtp.XYCAxis(r'$z$', 'mm', limits=[25, 55]),
        ePos=1, title=beamLine.fsm2.name+'_E')
    plot.caxis.fwhmFormatStr = fwhmFormatStrE
    plot.caxis.limits = eLimits
    plot.caxis.offset = offsetE
    plot.textPanel = plot.fig.text(
        0.88, 0.8, '', transform=plot.fig.transFigure, size=14, color='r',
        ha='center')
    plots.append(plot)

    plot = xrtp.XYCPlot(
        'beamFSM2', (1,),
        xaxis=xrtp.XYCAxis(r'$x$', 'mm', limits=[-15, 15]),
        yaxis=xrtp.XYCAxis(r'$z$', 'mm', limits=[25, 55]),
        caxis=xrtp.XYCAxis('degree of polarization', '',
                           data=raycing.get_polarization_degree,
                           limits=[0, 1]),
        ePos=1, title=beamLine.fsm2.name+'_DegreeOfPol')
    plot.textPanel = plot.fig.text(
        0.88, 0.8, '', transform=plot.fig.transFigure, size=14, color='r',
        ha='center')
    plots.append(plot)

    plot = xrtp.XYCPlot(
        'beamFSM2', (1,),
        xaxis=xrtp.XYCAxis(r'$x$', 'mm', limits=[-15, 15]),
        yaxis=xrtp.XYCAxis(r'$z$', 'mm', limits=[25, 55]),
        caxis=xrtp.XYCAxis('circular polarization rate', '',
                           data=raycing.get_circular_polarization_rate,
                           limits=[-1, 1]),
        ePos=1, title=beamLine.fsm2.name+'_CircPolRate')
    plot.textPanel = plot.fig.text(
        0.88, 0.8, '', transform=plot.fig.transFigure, size=14, color='r',
        ha='center')
    plots.append(plot)

    plot = xrtp.XYCPlot(
        'beamFSM2', (1,),
        xaxis=xrtp.XYCAxis(r'$x$', 'mm', limits=[-15, 15]),
        yaxis=xrtp.XYCAxis(r'$z$', 'mm', limits=[25, 55]),
        caxis=xrtp.XYCAxis('ratio of ellipse axes', '',
                           data=raycing.get_ratio_ellipse_axes,
                           limits=[-1, 1]),
        ePos=1, title=beamLine.fsm2.name+'_PolAxesRatio')
    plot.textPanel = plot.fig.text(
        0.88, 0.8, '', transform=plot.fig.transFigure, size=14, color='r',
        ha='center')
    plots.append(plot)

    plot = xrtp.XYCPlot(
        'beamFSM2', (1,),
        xaxis=xrtp.XYCAxis(r'$x$', 'mm', limits=[-15, 15]),
        yaxis=xrtp.XYCAxis(r'$z$', 'mm', limits=[25, 55]),
        caxis=xrtp.XYCAxis('angle of polarization ellipse', 'rad',
                           data=raycing.get_polarization_psi,
                           limits=[-math.pi/2, math.pi/2]),
        ePos=1, title=beamLine.fsm2.name+'_PolPsi')
    plot.ax1dHistE.set_yticks(
        (-math.pi/2, -math.pi/4, 0, math.pi/4, math.pi/2))
    plot.ax1dHistE.set_yticklabels(
        (r'-$\frac{\pi}{2}$', r'-$\frac{\pi}{4}$',
         '0', r'$\frac{\pi}{4}$', r'$\frac{\pi}{2}$'))
    plot.textPanel = plot.fig.text(
        0.88, 0.8, '', transform=plot.fig.transFigure, size=14, color='r',
        ha='center')
    plots.append(plot)

#    polarization = ['horizontal', 'vertical', '+45', '-45', 'right', 'left',
#                    None]
    polarization = '+45',

    def plot_generator():
        for polar in polarization:
            beamLine.sources[0].polarization = polar
            suffix = polar
            if suffix is None:
                suffix = 'none'
            for plot in plots:
                plot.xaxis.fwhmFormatStr = '%.1f'
                plot.yaxis.fwhmFormatStr = '%.1f'
                fileName = '{0}{1}_{2}'.format(prefix, plot.title, suffix)
                plot.saveName = fileName + '.png'
#                plot.persistentName = fileName + '.pickle'
                try:
                    plot.textPanel.set_text('{0}'.format(suffix))
                except AttributeError:
                    pass
            yield

    xrtr.run_ray_tracing(
        plots, repeats=40, generator=plot_generator,
        beamLine=beamLine, processes='auto')

#this is necessary to use multiprocessing in Windows, otherwise the new Python
#contexts cannot be initialized:
if __name__ == '__main__':
    main()
