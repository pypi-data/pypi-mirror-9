﻿# -*- coding: utf-8 -*-
__author__ = "Konstantin Klementiev", "Roman Chernikov"
__date__ = "10 Apr 2015"

import sys
#sys.path.append(r"/media/sf_Ray-tracing")
sys.path.append(r"c:\Ray-tracing")

import numpy as np

import BalderDMM
import xrt.plotter as xrtp
import xrt.runner as xrtr
#import xrt.backends.raycing.materials as rm

stripe = 'Si'
E0 = 8000
dE = 1200


def main():
    beamLine = BalderDMM.build_beamline(stripe=stripe,
                                        eMinRays=E0-dE, eMaxRays=E0+dE)
    plots = []

    plot = xrtp.XYCPlot(
        'beamFSMDCM', (1,),
        xaxis=xrtp.XYCAxis(r'$x$', 'mm'), yaxis=xrtp.XYCAxis(r'$z$', 'mm'),
        caxis=xrtp.XYCAxis('energy', 'keV', fwhmFormatStr='%.2f'), title='DCM')
    plot.xaxis.limits = [-7., 7.]
    plot.yaxis.limits = [20.3-7., 20.3+7.]
    plot.fluxFormatStr = '%.1p'
    plot.textPanel = plot.fig.text(0.88, 0.8, '',
                                   transform=plot.fig.transFigure, size=14,
                                   color='r', ha='center')
    plot.baseName = 'afterDMM'
    plots.append(plot)

    plot = xrtp.XYCPlot(
        'beamDCMlocal1', (1,),
        xaxis=xrtp.XYCAxis(r'$x$', 'mm'), yaxis=xrtp.XYCAxis(r'$y$', 'mm'),
        caxis=xrtp.XYCAxis('energy', 'keV', fwhmFormatStr='%.2f'),
        title='Xtal1 local')
    plot.xaxis.limits = [-86., 86.]
    plot.yaxis.limits = [-86., 86.]
    plot.fluxFormatStr = '%.1p'
    plot.textPanel = plot.fig.text(0.88, 0.8, '',
                                   transform=plot.fig.transFigure, size=14,
                                   color='r', ha='center')
    plot.baseName = '1stML'
    plots.append(plot)

    for plot in plots:
        plot.caxis.limits = [(E0 - dE)*1e-3, (E0 + dE)*1e-3]
        plot.caxis.offset = E0*1e-3

    energies = np.linspace(E0 - 500, E0 + 500, 7)

    def plot_generator():
        for energy in energies:
            BalderDMM.align_beamline(beamLine, energy=energy)
            thetaDeg = np.degrees(
                beamLine.dmm.bragg - 2*beamLine.vcm.pitch)
            for plot in plots:
                baseName = '{0}_{1:05.0f}'.format(plot.baseName, thetaDeg*1e4)
                plot.saveName = baseName + '.png'
#                plot.persistentName = baseName + '.pickle'
                if hasattr(plot, 'textPanel'):
                    plot.textPanel.set_text(
                        '$\\theta$ = {0:.3f}$^o$'.format(thetaDeg))
            yield

    xrtr.run_ray_tracing(plots, repeats=160, generator=plot_generator,
                         beamLine=beamLine, globalNorm=True, processes=1)

#this is necessary to use multiprocessing in Windows, otherwise the new Python
#contexts cannot be initialized:
if __name__ == '__main__':
    main()
