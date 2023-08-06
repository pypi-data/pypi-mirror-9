# -*- coding: utf-8 -*-
__author__ = "Roman Chernikov"
__date__ = "11 Apr 2015"

import sys
#import os
#import pickle
import numpy as np
#import matplotlib.pyplot as plt

sys.path.append(r"c:\Ray-tracing")
#sys.path.append(r"/media/roman/MINTSTORAGE/test_x5")
import xrt.backends.raycing as raycing
import xrt.backends.raycing.sources as rs
import xrt.backends.raycing.screens as rsc
import xrt.backends.raycing.run as rr
#import xrt.backends.raycing.materials as rm
import xrt.plotter as xrtp
import xrt.runner as xrtr

prefix = 'taper_'
xlimits = [-5.0, 5.0]
zlimits = [-2.5, 2.5]
E0 = 10200
dEw = 800
dE = 0.5
eMin, eMax = E0-dEw, E0+dEw
elimits = [eMin, eMax]


def build_beamline(nrays=5e5):
    beamLine = raycing.BeamLine()
    rs.Undulator(
        beamLine, 'P06', nrays=nrays, eEspread=0.0011,
        eSigmaX=34.64, eSigmaZ=6.285, eEpsilonX=1., eEpsilonZ=0.01,
        period=31.4, K=2.1392-0.002, n=63, eE=6.08, eI=0.1, xPrimeMax=1.5e-2,
        zPrimeMax=1.5e-2, eMin=eMin, eMax=eMax, distE='BW',
        xPrimeMaxAutoReduce=False, zPrimeMaxAutoReduce=False,
        uniformRayDensity=True,
        taper=(1.09, 11.254),
        precisionOpenCL='float64',
        targetOpenCL=(0, 0)
        )

    beamLine.fsm1 = rsc.Screen(beamLine, 'FSM1', (0, 75000, 0))
    return beamLine


def run_process(beamLine):
    beamSource = beamLine.sources[0].shine()
    beamFSM1 = beamLine.fsm1.expose(beamSource)
    outDict = {'beamSource': beamSource,
               'beamFSM1': beamFSM1}
    return outDict

rr.run_process = run_process


def main():
    beamLine = build_beamline()
    plots = []
    plotsE = []

    xaxis = xrtp.XYCAxis(r'$x$', 'mm', limits=xlimits, bins=512, ppb=1)
    yaxis = xrtp.XYCAxis(r'$z$', 'mm', limits=zlimits, bins=256, ppb=1)
    caxis = xrtp.XYCAxis('energy', 'eV', limits=elimits,
                         offset=E0, bins=256, ppb=1)
    plot = xrtp.XYCPlot(
        'beamFSM1', (1,), xaxis=xaxis, yaxis=yaxis, caxis=caxis,
        aspect='auto', title='total flux', ePos=1)
    plot.baseName = prefix + '1TotalFlux - nearAxis - s'
    plot.saveName = plot.baseName + '.png'
    plots.append(plot)
    plotsE.append(plot)

    for plot in plots:
        plot.fluxFormatStr = '%.2p'

    def plot_generator():
        for stepE in np.linspace(E0-dEw, E0+dEw, 161):
            beamLine.sources[0].E_max = stepE + 0.5
            beamLine.sources[0].E_min = stepE - 0.5
            for plot in plots:
                plot.title = str(stepE) + " eV"
                plot.saveName = plot.title + ".png"
            yield

    xrtr.run_ray_tracing(plots, repeats=20, beamLine=beamLine,
                         generator=plot_generator, threads=4,
                         globalNorm=1)


if __name__ == '__main__':
    main()
