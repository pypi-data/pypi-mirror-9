﻿# -*- coding: utf-8 -*-
__author__ = "Konstantin Klementiev"
__date__ = "1 Mar 2012"
import sys
sys.path.append(r"c:\Ray-tracing")
import math
import numpy as np
import matplotlib as mpl

import xrt.backends.raycing as raycing
import xrt.backends.raycing.sources as rs
import xrt.backends.raycing.apertures as ra
import xrt.backends.raycing.oes as roe
import xrt.backends.raycing.run as rr
import xrt.backends.raycing.materials as rm
import xrt.backends.raycing.screens as rsc

import xrt.plotter as xrtp
import xrt.runner as xrtr

E0 = 9000.
eLimits = E0, E0+2.5

crystalDiamond = rm.CrystalDiamond(
    (1, 1, 1), 2.0592872, elements='C', geom='Laue transmitted', t=0.05)
#crystalDiamond = rm.CrystalDiamond(
#    (3, 1, 1), 2.0592872*(3./11)**0.5, elements='C', geom='Laue transmitted',
#    t=0.05)
theta0 = math.asin(rm.ch / (2 * crystalDiamond.d * (E0+1.2)))


def build_beamline(nrays=raycing.nrays):
    fixedExit = 15.

    beamLine = raycing.BeamLine(azimuth=0, height=0)
    hDiv = 1.5e-3
    vDiv = 2.5e-4
    rs.GeometricSource(
        beamLine, 'GeometricSource', (0, 0, 0),
        nrays=nrays, dx=0.1, dy=0, dz=2., dxprime=hDiv/2, dzprime=0,
        distE='flat', energies=eLimits, polarization='horizontal')

    beamLine.feMovableMaskLT = ra.RectangularAperture(
        beamLine, 'FEMovableMaskLT', [0, 10000, 0], ('left', 'top'), [-10, 3.])
    beamLine.feMovableMaskRB = ra.RectangularAperture(
        beamLine, 'FEMovableMaskRB', [0, 10500, 0], ('right', 'bottom'),
        [10, -3.])
    beamLine.feMovableMaskLT.set_divergence(
        beamLine.sources[0], [-hDiv/2, vDiv/2])
    beamLine.feMovableMaskRB.set_divergence(
        beamLine.sources[0], [hDiv/2, -vDiv/2])

    yDCM = 21000.
    si111 = rm.CrystalSi(hkl=(1, 1, 1), tK=-171+273.15)
    beamLine.dcm = roe.DCM(
        beamLine, 'DCM', (0, yDCM, 0), surface=('Si111',), material=(si111,))
    beamLine.dcm.bragg = math.asin(rm.ch / (2 * si111.d * E0))
    beamLine.dcm.cryst2perpTransl = fixedExit/2./math.cos(beamLine.dcm.bragg)

    beamLine.fsm1 = rsc.Screen(beamLine, 'FSM1', (0, yDCM + 700, 0))

    yVFM = 24000.
    beamLine.vfm = roe.ToroidMirror(
        beamLine, 'VFM', (0, yVFM, fixedExit), pitch=4.0e-3)
    beamLine.vfm.R = yVFM / beamLine.vfm.pitch
    beamLine.vfm.r = 2. / 3. * yVFM * beamLine.vfm.pitch
    yFlatMirror = yVFM + 2000.
    zFlatMirror = (yFlatMirror - yVFM) * 2. * beamLine.vfm.pitch + fixedExit
    beamLine.vdm = roe.OE(
        beamLine, 'FlatMirror', (0, yFlatMirror, zFlatMirror),
        pitch=-beamLine.vfm.pitch, positionRoll=math.pi)

    ySample = 1.5 * yVFM
    yQWP = ySample - 3000.
    beamLine.qwp = roe.LauePlate(beamLine, 'QWP', (0, yQWP, zFlatMirror),
                                 roll=math.pi/4, material=(crystalDiamond,))
    beamLine.qwp.pitch = theta0 + math.pi/2

    beamLine.fsm2 = rsc.Screen(beamLine, 'FSM2', (0, ySample, zFlatMirror))

    return beamLine


def run_process(beamLine):
    beamSource = beamLine.sources[0].shine()
    beamLine.feMovableMaskLT.propagate(beamSource)
    beamLine.feMovableMaskRB.propagate(beamSource)

    beamDCMglobal, beamDCMlocal1, beamDCMlocal2 = \
        beamLine.dcm.double_reflect(beamSource)
    beamFSM1 = beamLine.fsm1.expose(beamDCMglobal)

    beamVFMglobal, beamVFMlocal = beamLine.vfm.reflect(beamDCMglobal)
    beamVDMglobal, beamVDMlocal = beamLine.vdm.reflect(beamVFMglobal)

    beamQWPglobal, beamQWPlocal = beamLine.qwp.reflect(beamVDMglobal)
    beamFSM2 = beamLine.fsm2.expose(beamQWPglobal)

    outDict = {'beamSource': beamSource,
               'beamDCMglobal': beamDCMglobal,
               'beamDCMlocal1': beamDCMlocal1,
               'beamDCMlocal2': beamDCMlocal2,
               'beamFSM1': beamFSM1,
               'beamVFMglobal': beamVFMglobal,
               'beamVFMlocal': beamVFMlocal,
               'beamVDMglobal': beamVDMglobal,
               'beamVDMlocal': beamVDMlocal,
               'beamQWPglobal': beamQWPglobal,
               'beamQWPlocal': beamQWPlocal,
               'beamFSM2': beamFSM2
               }
    return outDict

rr.run_process = run_process


def main():
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

#    plot = xrtp.XYCPlot('beamFSM1', (1,),
#      xaxis=xrtp.XYCAxis(r'$x$', 'mm', limits=[-20, 20]),
#      yaxis=xrtp.XYCAxis(r'$z$', 'mm', limits=[-20, 20]),
#      ePos=1, title=beamLine.fsm1.name+'_E')
#    plot.caxis.fwhmFormatStr = fwhmFormatStrE
#    plot.caxis.limits = eLimits
#    plot.caxis.offset = offsetE
#    plot.textPanel = plot.fig.text(
#        0.88, 0.8, '', transform=plot.fig.transFigure, size=14, color='r',
#        ha='center')
#    plots.append(plot)

#    plot = xrtp.XYCPlot('beamVFMlocal', (1,2), aspect='auto',
#      xaxis=xrtp.XYCAxis(r'$x$', 'mm', limits=[-20, 20]),
#      yaxis=xrtp.XYCAxis(r'$y$', 'mm'),
#      title='VFM_footprint')
#    plots.append(plot)

#    plot = xrtp.XYCPlot('beamQWPlocal', (1,2),
#      xaxis=xrtp.XYCAxis(r'$x$', 'mm', limits=[-10, 10]),
#      yaxis=xrtp.XYCAxis(r'$y$', 'mm'),
#      title='QWP_footprint')
#    plots.append(plot)

    plot = xrtp.XYCPlot(
        'beamFSM2', (1,),
        xaxis=xrtp.XYCAxis(r'$x$', 'mm', limits=[-0.15, 0.15]),
        yaxis=xrtp.XYCAxis(r'$z$', 'mm', limits=[-0.15, 0.15]),
        ePos=1, title=beamLine.fsm2.name+'_E')
    plot.caxis.fwhmFormatStr = fwhmFormatStrE
    plot.caxis.limits = eLimits
    plot.caxis.offset = offsetE
    plot.textPanel = plot.fig.text(
        0.88, 0.8, '', transform=plot.fig.transFigure, size=14, color='r',
        ha='center')
    plots.append(plot)

#    plot = xrtp.XYCPlot('beamFSM2', (1,),
#      xaxis=xrtp.XYCAxis(r'$x$', 'mm', limits=[-0.15, 0.15]),
#      yaxis=xrtp.XYCAxis(r'$z$', 'mm', limits=[-0.15, 0.15]),
#      caxis=xrtp.XYCAxis('degree of polarization', '',
#      data=raycing.get_polarization_degree, limits=[0, 1]),
#      ePos=1, title=beamLine.fsm2.name+'_DegreeOfPol')
#    plot.textPanel = plot.fig.text(
#        0.88, 0.8, '', transform=plot.fig.transFigure, size=14, color='r',
#        ha='center')
#    plots.append(plot)

    plot = xrtp.XYCPlot(
        'beamFSM2', (1,),
        xaxis=xrtp.XYCAxis(r'$x$', 'mm', limits=[-0.15, 0.15]),
        yaxis=xrtp.XYCAxis(r'$z$', 'mm', limits=[-0.15, 0.15]),
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
        xaxis=xrtp.XYCAxis(r'$x$', 'mm', limits=[-0.15, 0.15]),
        yaxis=xrtp.XYCAxis(r'$z$', 'mm', limits=[-0.15, 0.15]),
        caxis=xrtp.XYCAxis('ratio of ellipse axes', '',
                           data=raycing.get_ratio_ellipse_axes,
                           limits=[-1, 1]),
        ePos=1, title=beamLine.fsm2.name+'_PolAxesRatio')
    plot.textPanel = plot.fig.text(
        0.88, 0.8, '', transform=plot.fig.transFigure, size=14, color='r',
        ha='center')
    plots.append(plot)

#    plot = xrtp.XYCPlot('beamFSM2', (1,),
#      xaxis=xrtp.XYCAxis(r'$x$', 'mm', limits=[-0.15, 0.15]),
#      yaxis=xrtp.XYCAxis(r'$z$', 'mm', limits=[-0.15, 0.15]),
#      caxis=xrtp.XYCAxis('angle of polarization ellipse', 'rad',
#      data=raycing.get_polarization_psi, limits=[-math.pi/2, math.pi/2]),
#      ePos=1, title=beamLine.fsm2.name+'_PolPsi')
#    plot.ax1dHistE.set_yticks(
#        (-math.pi/2, -math.pi/4, 0, math.pi/4, math.pi/2))
#    plot.ax1dHistE.set_yticklabels((r'-$\frac{\pi}{2}$', r'-$\frac{\pi}{4}$',
#      '0', r'$\frac{\pi}{4}$', r'$\frac{\pi}{2}$'))
#    plot.textPanel = plot.fig.text(
#        0.88, 0.8, '', transform=plot.fig.transFigure,
#        size=14, color='r', ha='center')
#    plots.append(plot)

    plot = xrtp.XYCPlot(
        'beamFSM2', (1,),
        xaxis=xrtp.XYCAxis(r'$x$', 'mm', limits=[-0.15, 0.15]),
        yaxis=xrtp.XYCAxis(r'$z$', 'mm', limits=[-0.15, 0.15]),
        caxis=xrtp.XYCAxis('phase shift', '',
                           data=raycing.get_phase_shift,
                           limits=[-1, 1]),  # limits are in units of pi!
        ePos=1, title=beamLine.fsm2.name+'_PhaseShift')
    formatter = mpl.ticker.FormatStrFormatter('%g' + r'$ \pi$')
    plot.ax1dHistE.yaxis.set_major_formatter(formatter)
    plot.textPanel = plot.fig.text(
        0.88, 0.8, '', transform=plot.fig.transFigure, size=14, color='r',
        ha='center')
    plots.append(plot)

#    polarization = ['horiz', 'vert', '+45', '-45', 'right', 'left', None]
    polarization = 'horiz',

    prefix = '06_conv_LT'
#    thickness = np.linspace(500., 5000., 10)#in um
    thickness = 500.,  # in um
#    thickness = 2500.,#in um
    posTheta = np.logspace(0, 13, 14, base=2)
    departureTheta = np.hstack((-posTheta[::-1], 0, posTheta))

    def plot_generator():
        for polar in polarization:
            beamLine.sources[0].polarization = polar
            suffix = polar
            if suffix is None:
                suffix = 'none'
            for thick in thickness:
                crystalDiamond.t = thick * 1e-3  # in mm
                for iTheta, dTheta in enumerate(departureTheta):
                    beamLine.qwp.pitch = theta0 + math.pi/2 +\
                        math.radians(dTheta / 3600.)
                    for plot in plots:
                        plot.xaxis.fwhmFormatStr = '%.1f'
                        plot.yaxis.fwhmFormatStr = '%.1f'
                        fileName = '{0}_{1}_{2}_{3:04.0f}um_{4:02d}'.\
                            format(prefix, plot.title, suffix, thick, iTheta)
                        plot.saveName = fileName + '.png'
#                        plot.persistentName = fileName + '.pickle'
                        try:
                            plot.textPanel.set_text(
                                u'{0}\n{1:4.0f} µm\n{2:+4.0f} arcsec'.
                                format(suffix, thick, dTheta))
                        except AttributeError:
                            pass
                    yield

    xrtr.run_ray_tracing(
        plots, repeats=24, generator=plot_generator,
        beamLine=beamLine, globalNorm=True, processes='all')

#this is necessary to use multiprocessing in Windows, otherwise the new Python
#contexts cannot be initialized:
if __name__ == '__main__':
    main()
