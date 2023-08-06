﻿# -*- coding: utf-8 -*-
__author__ = "Konstantin Klementiev"
__date__ = "20 Apr 2013"

import sys
#sys.path.append(r"/media/sf_Ray-tracing")
sys.path.append(r"c:\Ray-tracing")
import numpy as np
import BalderBL
import xrt.plotter as xrtp
import xrt.runner as xrtr
import xrt.backends.raycing.sources as rs
import xrt.backends.raycing.run as rr

stripe = 'Ir'


def run_process(beamLine, shineOnly1stSource=False):
    beamSource = beamLine.sources[0].shine()

    beamFSM0 = beamLine.fsm0.expose(beamSource)
    beamLine.feFixedMask.propagate(beamSource)
    beamFSMFE = beamLine.fsmFE.expose(beamSource)
    beamFilter1global, beamFilter1local1, beamFilter1local2 =\
        beamLine.filter1.double_refract(beamSource)
    beamFilter1local2A = rs.Beam(copyFrom=beamFilter1local2)
    beamFilter1local2A.absorb_intensity(beamSource)
    beamFurtherDown = beamFilter1global

    beamVCMglobal, beamVCMlocal = beamLine.vcm.reflect(beamFurtherDown)
    beamVCMlocal.absorb_intensity(beamFurtherDown)
    beamFSMVCM = beamLine.fsmVCM.expose(beamVCMglobal)

    outDict = {'beamSource': beamSource,
               'beamFSM0': beamFSM0,
               'beamFSMFE': beamFSMFE,
               'beamFilter1global': beamFilter1global,
               'beamFilter1local1': beamFilter1local1,
               'beamFilter1local2': beamFilter1local2,
               'beamFilter1local2A': beamFilter1local2A,
               'beamVCMglobal': beamVCMglobal, 'beamVCMlocal': beamVCMlocal,
               'beamFSMVCM': beamFSMVCM}
    beamLine.beams = outDict
    return outDict
rr.run_process = run_process


def main():
    beamLine = BalderBL.build_beamline(stripe=stripe)
    BalderBL.align_beamline(beamLine)
    plots = []

#    plot = xrtp.XYCPlot('beamFilter1local1', (1,),
#      xaxis=xrtp.XYCAxis(r'$x$', 'mm'), yaxis=xrtp.XYCAxis(r'$y$', 'mm'),
#      caxis=xrtp.XYCAxis('energy', 'keV'),
#      title='Footprint1_I')
#    plot.fluxFormatStr = '%.2e'
#    plots.append(plot)

    plot = xrtp.XYCPlot(
        'beamVCMlocal', (1,), aspect='auto',
        xaxis=xrtp.XYCAxis(r'$x$', 'mm', limits=[-7, 7]),
        yaxis=xrtp.XYCAxis(r'$y$', 'mm', limits=[-700, 700]),
        caxis=xrtp.XYCAxis('energy', 'keV'),
        fluxKind='power', title='FootprintP',  # oe=beamLine.vcm,
        contourLevels=[0.9, ], contourColors=['r', ],
        contourFmt=r'%.3f W/mm$^2$')
    plot.fluxFormatStr = '%.0f'
    plot.xaxis.fwhmFormatStr = '%.1f'
    plot.yaxis.fwhmFormatStr = '%.0f'
    plot.textPanel = plot.fig.text(
        0.85, 0.8, '', transform=plot.fig.transFigure,
        size=14, color='r', ha='center')
    plots.append(plot)

    plot = xrtp.XYCPlot(
        'beamFSMVCM', (1,),
        xaxis=xrtp.XYCAxis(r'$x$', 'mm'), yaxis=xrtp.XYCAxis(r'$z$', 'mm'),
        caxis=xrtp.XYCAxis('energy', 'keV'), title='FSM')
    plot.xaxis.limits = [-7, 7]
    plot.yaxis.limits = [-2, 12]
    plot.fluxFormatStr = '%.2p'
    plot.textPanel = plot.fig.text(
        0.85, 0.8, '', transform=plot.fig.transFigure,
        size=14, color='r', ha='center')
    plots.append(plot)

    for plot in plots:
        plot.caxis.limits = [0, beamLine.sources[0].eMax*1e-3]
        plot.caxis.fwhmFormatStr = None

    pitches = np.linspace(1., 4., 31)

    def plot_generator():
        for pitch in pitches:
            beamLine.vcm.pitch = pitch * 1e-3
            for plot in plots:
                baseName = 'vcm{0}-{1}{2:.1f}mrad'.format(
                    stripe, plot.title, pitch)
                plot.saveName = baseName + '.png'
#                plot.persistentName = baseName + '.pickle'
                if hasattr(plot, 'textPanel'):
                    plot.textPanel.set_text(
                        '{0}\n$\\theta$ = {1:.1f} mrad'.format(stripe, pitch))
            yield

    xrtr.run_ray_tracing(
        plots, repeats=1000, generator=plot_generator,
        beamLine=beamLine, globalNorm=True, processes='half')

#this is necessary to use multiprocessing in Windows, otherwise the new Python
#contexts cannot be initialized:
if __name__ == '__main__':
    main()
