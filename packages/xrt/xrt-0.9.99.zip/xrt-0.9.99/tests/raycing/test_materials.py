﻿# -*- coding: utf-8 -*-
"""
Tests for Materials
-------------------

The module compares reflectivity, transmittivity, refraction index,
absorption coefficient etc. with those calculated by XOP.

Various material properties are compared with those calculated by XCrystal/XOP
(also used by shadow for modeling crystal optics), XInpro/XOP and others.

Reflectivity of Bragg crystals
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All the curves are basically equal. The small amplitude differences are due
to slight differences in Debye-Waller factor and/or tabulated values of the
atomic scattering factors. The phase difference between s- and p-polarized
rays (calculated by xrt, cyan line, right Y axis) is not calculated by the
XOP programs and therefore is given without comparison.

+-------+--------------------+------------------+-------------------+
|       |      α = -5°       |    symmetric     |       α = 5°      |
+=======+====================+==================+===================+
| thick | |bSi111_thick_-5|  | |bSi111_thick_0| | |bSi111_thick_5|  |
|       | |bSi333_thick_-5|  | |bSi333_thick_0| | |bSi333_thick_5|  |
+-------+--------------------+------------------+-------------------+
| 100 µm|   |bSi111_100_-5|  |  |bSi111_100_0|  |  |bSi111_100_5|   |
|       |   |bSi333_100_-5|  |  |bSi333_100_0|  |  |bSi333_100_5|   |
+-------+--------------------+------------------+-------------------+
| 7 µm  |   |bSi111_007_-5|  |  |bSi111_007_0|  |  |bSi111_007_5|   |
|       |   |bSi333_007_-5|  |  |bSi333_007_0|  |  |bSi333_007_5|   |
+-------+--------------------+------------------+-------------------+

.. |bSi111_thick_-5| image:: _images/bSi111_thick_-5.*
   :scale: 35 %
.. |bSi111_thick_0| image:: _images/bSi111_thick_0.*
   :scale: 35 %
.. |bSi111_thick_5| image:: _images/bSi111_thick_5.*
   :scale: 35 %
.. |bSi111_100_-5| image:: _images/bSi111_100mum_-5.*
   :scale: 35 %
.. |bSi111_100_0| image:: _images/bSi111_100mum_0.*
   :scale: 35 %
.. |bSi111_100_5| image:: _images/bSi111_100mum_5.*
   :scale: 35 %
.. |bSi111_007_-5| image:: _images/bSi111_007mum_-5.*
   :scale: 35 %
.. |bSi111_007_0| image:: _images/bSi111_007mum_0.*
   :scale: 35 %
.. |bSi111_007_5| image:: _images/bSi111_007mum_5.*
   :scale: 35 %

.. |bSi333_thick_-5| image:: _images/bSi333_thick_-5.*
   :scale: 35 %
.. |bSi333_thick_0| image:: _images/bSi333_thick_0.*
   :scale: 35 %
.. |bSi333_thick_5| image:: _images/bSi333_thick_5.*
   :scale: 35 %
.. |bSi333_100_-5| image:: _images/bSi333_100mum_-5.*
   :scale: 35 %
.. |bSi333_100_0| image:: _images/bSi333_100mum_0.*
   :scale: 35 %
.. |bSi333_100_5| image:: _images/bSi333_100mum_5.*
   :scale: 35 %
.. |bSi333_007_-5| image:: _images/bSi333_007mum_-5.*
   :scale: 35 %
.. |bSi333_007_0| image:: _images/bSi333_007mum_0.*
   :scale: 35 %
.. |bSi333_007_5| image:: _images/bSi333_007mum_5.*
   :scale: 35 %

Reflectivity of Laue crystals
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All the curves are basically equal. The small amplitude differences are due
to slight differences in Debye-Waller factor and/or tabulated values of the
atomic scattering factors. The phase difference between s- and p-polarized
rays (calculated by xrt, cyan line, right Y axis) is not calculated by the
XOP programs and therefore is given without comparison.

+-------+--------------------+------------------+-------------------+
|       |      α = -5°       |    symmetric     |       α = 5°      |
+=======+====================+==================+===================+
| 100 µm|   |lSi111_100_-5|  |  |lSi111_100_0|  |  |lSi111_100_5|   |
|       |   |lSi333_100_-5|  |  |lSi333_100_0|  |  |lSi333_100_5|   |
+-------+--------------------+------------------+-------------------+
| 7 µm  |   |lSi111_007_-5|  |  |lSi111_007_0|  |  |lSi111_007_5|   |
|       |   |lSi333_007_-5|  |  |lSi333_007_0|  |  |lSi333_007_5|   |
+-------+--------------------+------------------+-------------------+

.. |lSi111_100_-5| image:: _images/lSi111_100mum_-5.*
   :scale: 35 %
.. |lSi111_100_0| image:: _images/lSi111_100mum_0.*
   :scale: 35 %
.. |lSi111_100_5| image:: _images/lSi111_100mum_5.*
   :scale: 35 %
.. |lSi111_007_-5| image:: _images/lSi111_007mum_-5.*
   :scale: 35 %
.. |lSi111_007_0| image:: _images/lSi111_007mum_0.*
   :scale: 35 %
.. |lSi111_007_5| image:: _images/lSi111_007mum_5.*
   :scale: 35 %

.. |lSi333_100_-5| image:: _images/lSi333_100mum_-5.*
   :scale: 35 %
.. |lSi333_100_0| image:: _images/lSi333_100mum_0.*
   :scale: 35 %
.. |lSi333_100_5| image:: _images/lSi333_100mum_5.*
   :scale: 35 %
.. |lSi333_007_-5| image:: _images/lSi333_007mum_-5.*
   :scale: 35 %
.. |lSi333_007_0| image:: _images/lSi333_007mum_0.*
   :scale: 35 %
.. |lSi333_007_5| image:: _images/lSi333_007mum_5.*
   :scale: 35 %

.. _transmittivity_Bragg:

Transmittivity of Bragg crystals
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The curves are basically equal only for the symmetric case. Both
XCrystal/XOP and XInpro/XOP are wrong for asymmetric crystals, when they
give too low or too high (>1) transmittivity.

+-------+--------------------+-------------------+--------------------+
|       |      α = -5°       |     symmetric     |        α = 5°      |
+=======+====================+===================+====================+
| 100 µm|  |btSi111_100_-5|  |  |btSi111_100_0|  |  |btSi111_100_5|   |
|       |  |btSi333_100_-5|  |  |btSi333_100_0|  |  |btSi333_100_5|   |
+-------+--------------------+-------------------+--------------------+
| 7 µm  |  |btSi111_007_-5|  |  |btSi111_007_0|  |  |btSi111_007_5|   |
|       |  |btSi333_007_-5|  |  |btSi333_007_0|  |  |btSi333_007_5|   |
+-------+--------------------+-------------------+--------------------+

.. |btSi111_100_-5| image:: _images/btSi111_100mum_-5.*
   :scale: 35 %
.. |btSi111_100_0| image:: _images/btSi111_100mum_0.*
   :scale: 35 %
.. |btSi111_100_5| image:: _images/btSi111_100mum_5.*
   :scale: 35 %
.. |btSi111_007_-5| image:: _images/btSi111_007mum_-5.*
   :scale: 35 %
.. |btSi111_007_0| image:: _images/btSi111_007mum_0.*
   :scale: 35 %
.. |btSi111_007_5| image:: _images/btSi111_007mum_5.*
   :scale: 35 %

.. |btSi333_100_-5| image:: _images/btSi333_100mum_-5.*
   :scale: 35 %
.. |btSi333_100_0| image:: _images/btSi333_100mum_0.*
   :scale: 35 %
.. |btSi333_100_5| image:: _images/btSi333_100mum_5.*
   :scale: 35 %
.. |btSi333_007_-5| image:: _images/btSi333_007mum_-5.*
   :scale: 35 %
.. |btSi333_007_0| image:: _images/btSi333_007mum_0.*
   :scale: 35 %
.. |btSi333_007_5| image:: _images/btSi333_007mum_5.*
   :scale: 35 %

Transmittivity of Laue crystals
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The curves are basically equal only for the symmetric case and only with
XInpro/XOP results. XInpro/XOP is wrong for asymmetric crystals, when it
gives too low or too high (>1) transmittivity. As seen, XCrystal/XOP is
essentially different and wrong with Laue transmittivity.

+-------+--------------------+-------------------+--------------------+
|       |      α = -5°       |    symmetric      |        α = 5°      |
+=======+====================+===================+====================+
| 100 µm|  |ltSi111_100_-5|  |  |ltSi111_100_0|  |  |ltSi111_100_5|   |
|       |  |ltSi333_100_-5|  |  |ltSi333_100_0|  |  |ltSi333_100_5|   |
+-------+--------------------+-------------------+--------------------+
| 7 µm  |  |ltSi111_007_-5|  |  |ltSi111_007_0|  |  |ltSi111_007_5|   |
|       |  |ltSi333_007_-5|  |  |ltSi333_007_0|  |  |ltSi333_007_5|   |
+-------+--------------------+-------------------+--------------------+

.. |ltSi111_100_-5| image:: _images/ltSi111_100mum_-5.*
   :scale: 35 %
.. |ltSi111_100_0| image:: _images/ltSi111_100mum_0.*
   :scale: 35 %
.. |ltSi111_100_5| image:: _images/ltSi111_100mum_5.*
   :scale: 35 %
.. |ltSi111_007_-5| image:: _images/ltSi111_007mum_-5.*
   :scale: 35 %
.. |ltSi111_007_0| image:: _images/ltSi111_007mum_0.*
   :scale: 35 %
.. |ltSi111_007_5| image:: _images/ltSi111_007mum_5.*
   :scale: 35 %

.. |ltSi333_100_-5| image:: _images/ltSi333_100mum_-5.*
   :scale: 35 %
.. |ltSi333_100_0| image:: _images/ltSi333_100mum_0.*
   :scale: 35 %
.. |ltSi333_100_5| image:: _images/ltSi333_100mum_5.*
   :scale: 35 %
.. |ltSi333_007_-5| image:: _images/ltSi333_007mum_-5.*
   :scale: 35 %
.. |ltSi333_007_0| image:: _images/ltSi333_007mum_0.*
   :scale: 35 %
.. |ltSi333_007_5| image:: _images/ltSi333_007mum_5.*
   :scale: 35 %

Mirror reflectivity
~~~~~~~~~~~~~~~~~~~

The curves are basically equal. The small amplitude differences are due
to slight differences in tabulated values of the atomic scattering factors.
The phase difference between s- and p-polarized rays (calculated by xrt,
cyan line, right Y axis) is not calculated by the XOP programs and
therefore is given without comparison.

.. image:: _images/MirrorReflSi@0.5deg.*
   :scale: 35 %
.. image:: _images/MirrorReflSiO2@0.5deg.*
   :scale: 35 %
.. image:: _images/MirrorReflRh@2mrad.*
   :scale: 35 %
.. image:: _images/MirrorReflPt@4mrad.*
   :scale: 35 %

.. _multilayer_reflectivity:

Slab and multilayer reflectivity
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The curves are basically equal. The small amplitude differences are due
to slight differences in tabulated values of the atomic scattering factors.
The phase difference between s- and p-polarized rays is given without
comparison.

.. image:: _images/SlabReflW.*
   :scale: 35 %
.. image:: _images/MultilayerSiW.*
   :scale: 35 %

Transmittivity of materials
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The curves are basically equal. The small amplitude differences are due
to slight differences in tabulated values of the atomic scattering factors.

.. image:: _images/TransmDiamond.*
   :scale: 35 %

Absorption of materials
~~~~~~~~~~~~~~~~~~~~~~~

The curves are basically equal. The small amplitude differences are due
to slight differences in tabulated values of the atomic scattering factors.

.. image:: _images/AbsorptionBe.*
   :scale: 35 %
"""
__author__ = "Konstantin Klementiev"
__date__ = "12 Mar 2014"

import os
import sys
import math
#import cmath
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

sys.path.append(r"c:\Ray-tracing")
#sys.path.append(r"/media/sf_Ray-tracing")
import xrt.backends.raycing.materials as rm


def compare_rocking_curves(hkl, t=None, geom='Bragg reflected', factDW=1.,
                           legendPos1=4, legendPos2=1):
    """A comparison subroutine used in the module test suit."""
    def for_one_alpha(crystal, alphaDeg, hkl):
        alpha = math.radians(alphaDeg)
        s0 = (np.zeros_like(theta), np.cos(theta+alpha), -np.sin(theta+alpha))
        sh = (np.zeros_like(theta), np.cos(theta-alpha), np.sin(theta-alpha))
        if geom.startswith('Bragg'):
            n = (0, 0, 1)  # outward surface normal
        else:
            n = (0, -1, 0)  # outward surface normal
        hn = (0, math.sin(alpha), math.cos(alpha))  # outward Bragg normal
        gamma0 = sum(i*j for i, j in zip(n, s0))
        gammah = sum(i*j for i, j in zip(n, sh))
        hns0 = sum(i*j for i, j in zip(hn, s0))

        fig = plt.figure()
        fig.subplots_adjust(right=0.88)
        ax = fig.add_subplot(111)

#        curS, curP = crystal.get_amplitude_Authie(E, gamma0, gammah, hns0)
#        p5, = ax.plot((theta - thetaCenter) * convFactor, abs(curS)**2, '-g')
#        p6, = ax.plot((theta - thetaCenter) * convFactor, abs(curP)**2, '--g')
        curS, curP = crystal.get_amplitude(E, gamma0, gammah, hns0)
# phases:
        ax2 = ax.twinx()
        ax2.set_ylabel(r'$\phi_s - \phi_p$', color='c')
        phi = np.unwrap(np.angle(curS * curP.conj()))
        p9, = ax2.plot((theta-thetaCenter) * convFactor, phi, 'c', lw=1,
                       yunits=math.pi, zorder=0)
        formatter = mpl.ticker.FormatStrFormatter('%g' + r'$ \pi$')
        ax2.yaxis.set_major_formatter(formatter)
        for tl in ax2.get_yticklabels():
            tl.set_color('c')

        if t is not None:
            tt = u', t={0:.0f}µm'.format(t * 1e3)
            tname = '{0:03d}mum'.format(int(t * 1e3))
        else:
            tt = ' thick'
            tname = 'thick'
        if geom.startswith('Bragg'):
            geomPrefix = 'b'
        else:
            geomPrefix = 'l'
        if geom.endswith('transmitted'):
            geomPrefix += 't'
        fig.suptitle(r'{0} Si{1}, $\alpha={2:.1f}^\circ${3}'.format(geom,
                     hkl, alphaDeg, tt), fontsize=16)

        path = os.path.join('', 'XOP-RockingCurves') + os.sep
        x, R2s = np.loadtxt("{0}{1}Si{2}_{3}_{4:-.0f}_s.xc.gz".format(path,
                            geomPrefix, hkl, tname, alphaDeg), unpack=True)
        p1, = ax.plot(x, R2s, '-k', label='s XCrystal')
        x, R2p = np.loadtxt("{0}{1}Si{2}_{3}_{4:-.0f}_p.xc.gz".format(path,
                            geomPrefix, hkl, tname, alphaDeg), unpack=True)
        p2, = ax.plot(x, R2p, '--k', label='p XCrystal')

        x, R2s = np.loadtxt("{0}{1}Si{2}_{3}_{4:-.0f}_s.xin.gz".format(path,
                            geomPrefix, hkl, tname, alphaDeg), unpack=True)
        p3, = ax.plot(x, R2s, '-b', label='s XInpro')
        x, R2p = np.loadtxt("{0}{1}Si{2}_{3}_{4:-.0f}_p.xin.gz".format(path,
                            geomPrefix, hkl, tname, alphaDeg), unpack=True)
        p4, = ax.plot(x, R2p, '--b', label='p XInpro')

        p7, = ax.plot((theta - thetaCenter) * convFactor, abs(curS)**2, '-r')
        p8, = ax.plot((theta - thetaCenter) * convFactor, abs(curP)**2, '--r')
        ax.set_xlabel(r'$\theta-\theta_B$ (arcsec)')
        if geom.endswith('transmitted'):
            ax.set_ylabel('transmittivity')
        else:
            ax.set_ylabel('reflectivity')
        ax.set_xlim([dtheta[0] * convFactor, dtheta[-1] * convFactor])
#upper right	1
#upper left	2
#lower left	3
#lower right	4
#right   	5
#center left	6
#center right	7
#lower center	8
#upper center	9
#center         10
        l1 = ax2.legend([p1, p2], ['s', 'p'], loc=legendPos1)
#        ax.legend([p1, p3, p5, p7], ['XCrystal/XOP', 'XInpro/XOP',
#        'pxrt-Authier', 'pxrt-Bel&Dm'], loc=1)
        ax2.legend([p1, p3, p7], ['XCrystal/XOP', 'XInpro/XOP', 'xrt'],
                   loc=legendPos2)
        ax2.add_artist(l1)

        fname = '{0}Si{1}_{2}_{3:-.0f}'.format(
            geomPrefix, hkl, tname, alphaDeg)
        fig.savefig(fname + '.png')

    E0 = 10000.
    convFactor = 180 / math.pi * 3600.  # arcsec
    if hkl == '111':  # Si111
        if geom.startswith('Bragg'):
            dtheta = np.linspace(0, 100, 400) * 1e-6
        else:
            dtheta = np.linspace(-50, 50, 400) * 1e-6
        dSpacing = 3.13562
        hklInd = 1, 1, 1
    elif hkl == '333':  # Si333
        if geom.startswith('Bragg'):
            dtheta = np.linspace(0, 30, 400) * 1e-6
        else:
            dtheta = np.linspace(-15, 15, 400) * 1e-6
        dSpacing = 3.13562 / 3
        hklInd = 3, 3, 3

    siCrystal = rm.CrystalDiamond(hklInd, dSpacing, t=t, geom=geom,
                                  factDW=factDW)
    thetaCenter = math.asin(rm.ch / (2*siCrystal.d*E0))

    E = np.ones_like(dtheta) * E0
    theta = dtheta + thetaCenter
    for_one_alpha(siCrystal, 0., hkl)
    for_one_alpha(siCrystal, -5., hkl)
    for_one_alpha(siCrystal, 5., hkl)


def compare_Bragg_Laue(hkl, beamPath, factDW=1.):
    """A comparison subroutine used in the module test suit."""
    def for_one_alpha(alphaDeg, hkl):
        alpha = math.radians(alphaDeg)
        s0 = (np.zeros_like(theta), np.cos(theta+alpha), -np.sin(theta+alpha))
        sh = (np.zeros_like(theta), np.cos(theta-alpha), np.sin(theta-alpha))

#'Bragg':
        n = (0, 0, 1)  # outward surface normal
        hn = (0, math.sin(alpha), math.cos(alpha))  # outward Bragg normal
        gamma0 = sum(i*j for i, j in zip(n, s0))
        gammah = sum(i*j for i, j in zip(n, sh))
        hns0 = sum(i*j for i, j in zip(hn, s0))
        braggS, braggP = siBraggCrystal.get_amplitude(E, gamma0, gammah, hns0)
#'Laue':
        n = (0, -1, 0)  # outward surface normal
        hn = (0, math.sin(alpha), math.cos(alpha))  # outward Bragg normal
        gamma0 = sum(i*j for i, j in zip(n, s0))
        gammah = sum(i*j for i, j in zip(n, sh))
        hns0 = sum(i*j for i, j in zip(hn, s0))
        laueS, laueP = siLaueCrystal.get_amplitude(E, gamma0, gammah, hns0)

        fig = plt.figure()
        ax = fig.add_subplot(111)

# phases:
        ax2 = ax.twinx()
        ax2.set_ylabel(r'$\phi_s - \phi_p$', color='c')
        phi = np.unwrap(np.angle(braggS * braggP.conj()))
        p5, = ax2.plot((theta-thetaCenter) * convFactor, phi, '-c', lw=1,
                       yunits=math.pi, zorder=0)
        phi = np.unwrap(np.angle(laueS * laueP.conj()))
        p6, = ax2.plot((theta-thetaCenter) * convFactor, phi, '-c.', lw=1,
                       yunits=math.pi, zorder=0)
        formatter = mpl.ticker.FormatStrFormatter('%g' + r'$ \pi$')
        ax2.yaxis.set_major_formatter(formatter)
        for tl in ax2.get_yticklabels():
            tl.set_color('c')

        fig.suptitle(r'Comparison of Bragg and Laue transmittivity for Si{0}'.
                     format(hkl), fontsize=16)
        p1, = ax.plot((theta-thetaCenter) * convFactor, abs(braggS)**2, '-r')
        p2, = ax.plot((theta-thetaCenter) * convFactor, abs(braggP)**2, '-b')
        p3, = ax.plot((theta-thetaCenter) * convFactor, abs(laueS)**2, '-r.')
        p4, = ax.plot((theta-thetaCenter) * convFactor, abs(laueP)**2, '-b.')
        ax.set_xlabel(r'$\theta-\theta_B$ (arcsec)')
        ax.set_ylabel('transmittivity')

#upper right	1
#upper left	2
#lower left	3
#lower right	4
#right   	5
#center left	6
#center right	7
#lower center	8
#upper center	9
#center         10
        l1 = ax.legend([p1, p2], ['s', 'p'], loc=3)
        ax.legend([p1, p3], [u'Bragg t={0:.1f} µm'.format(
            siBraggCrystal.t * 1e3), u'Laue t={0:.1f} µm'.format(
            siLaueCrystal.t * 1e3)], loc=2)
        ax.add_artist(l1)
        ax.set_xlim([dtheta[0] * convFactor, dtheta[-1] * convFactor])

        fname = r'BraggLaueTrSi{0}'.format(hkl)
        fig.savefig(fname + '.png')

    E0 = 10000.
    convFactor = 180 / math.pi * 3600.  # arcsec
    if hkl == '111':  # Si111
        dtheta = np.linspace(-100, 100, 400) * 1e-6
        dSpacing = 3.13562
        hklInd = 1, 1, 1
    elif hkl == '333':  # Si333
        dtheta = np.linspace(-30, 30, 400) * 1e-6
        dSpacing = 3.13562 / 3
        hklInd = 3, 3, 3

    thetaCenter = math.asin(rm.ch / (2*dSpacing*E0))
    t = beamPath * math.sin(thetaCenter)
    siBraggCrystal = rm.CrystalDiamond(hklInd, dSpacing, t=t,
                                       geom='Bragg transmitted', factDW=factDW)
    t = beamPath * math.cos(thetaCenter)
    siLaueCrystal = rm.CrystalDiamond(hklInd, dSpacing, t=t,
                                      geom='Laue transmitted', factDW=factDW)

    E = np.ones_like(dtheta) * E0
    theta = dtheta + thetaCenter
    for_one_alpha(0., hkl)
#    for_one_alpha(siCrystal, -5., hkl)
#    for_one_alpha(siCrystal, 5., hkl)


def compare_reflectivity():
    """A comparison subroutine used in the module test suit."""
    def for_one_material(stripe, refs, refp, theta, reprAngle):
        fig = plt.figure()
        fig.subplots_adjust(right=0.86)
        ax = fig.add_subplot(111)
        ax.set_xlabel('energy (eV)')
        ax.set_ylabel('reflectivity')
        ax.set_xlim(30, 5e4)
        fig.suptitle(stripe.name + ' ' + reprAngle, fontsize=16)
        x, R2s = np.loadtxt(refs, unpack=True)
        p1, = ax.plot(x, R2s, '-k', label='s xf1f2')
        x, R2s = np.loadtxt(refp, unpack=True)
        p2, = ax.plot(x, R2s, '--k', label='p xf1f2')
        refl = stripe.get_amplitude(E, math.sin(theta))
        rs, rp = refl[0], refl[1]
        p3, = ax.semilogx(E, abs(rs)**2, '-r')
        p4, = ax.semilogx(E, abs(rp)**2, '--r')
        l1 = ax.legend([p1, p2], ['s', 'p'], loc=3)
        ax.legend([p1, p3], ['Xf1f2/XOP', 'xrt'], loc=6)
        ax.add_artist(l1)
# phases:
        ax2 = ax.twinx()
        ax2.set_ylabel(r'$\phi_s - \phi_p$', color='c')
        phi = np.unwrap(np.angle(rs * rp.conj()))
        p9, = ax2.plot(x, phi, 'c', lw=2, yunits=math.pi, zorder=0)
        formatter = mpl.ticker.FormatStrFormatter('%g' + r'$ \pi$')
        ax2.yaxis.set_major_formatter(formatter)
        for tl in ax2.get_yticklabels():
            tl.set_color('c')
        fname = 'MirrorRefl' + stripe.name + reprAngle
        fig.savefig(fname + '.png')

    dataDir = os.path.join('', 'XOP-Reflectivities')
    E = np.logspace(1.+math.log10(3.), 4.+math.log10(5.), 500)
    stripeSi = rm.Material('Si', rho=2.33)
    for_one_material(stripeSi,
                     os.path.join(dataDir, "Si05deg_s.xf1f2.gz"),
                     os.path.join(dataDir, "Si05deg_p.xf1f2.gz"),
                     math.radians(0.5), '@ 0.5 deg')
    stripePt = rm.Material('Pt', rho=21.45)
    for_one_material(stripePt,
                     os.path.join(dataDir, "Pt4mrad_s.xf1f2.gz"),
                     os.path.join(dataDir, "Pt4mrad_p.xf1f2.gz"),
                     4e-3, '@ 4 mrad')
    stripeSiO2 = rm.Material(('Si', 'O'), quantities=(1, 2), rho=2.2)
    for_one_material(stripeSiO2,
                     os.path.join(dataDir, "SiO205deg_s.xf1f2.gz"),
                     os.path.join(dataDir, "SiO205deg_p.xf1f2.gz"),
                     math.radians(0.5), '@ 0.5 deg')
    stripeRh = rm.Material('Rh', rho=12.41)
    for_one_material(stripeRh,
                     os.path.join(dataDir, "Rh2mrad_s.xf1f2.gz"),
                     os.path.join(dataDir, "Rh2mrad_p.xf1f2.gz"),
                     2e-3, '@ 2 mrad')


def compare_reflectivity_slab():
    """A comparison subroutine used in the module test suit."""
    def for_one_material(stripe, refs, refp, E, reprEnergy):
        fig = plt.figure()
        fig.subplots_adjust(right=0.86)
        ax = fig.add_subplot(111)
        ax.set_xlabel('grazing angle (deg)')
        ax.set_ylabel('reflectivity')
        ax.set_xlim(0, 10)
        fig.suptitle(stripe.name + ' ' + reprEnergy, fontsize=16)
        x, R2s = np.loadtxt(refs, unpack=True)
        p1, = ax.plot(x, R2s, '-k', label='s Mlayer')
        x, R2s = np.loadtxt(refp, unpack=True)
        p2, = ax.plot(x, R2s, '--k', label='p Mlayer')
        refl = stripe.get_amplitude(E, np.sin(np.deg2rad(theta)))
        rs, rp = refl[0], refl[1]
        p3, = ax.semilogy(theta, abs(rs)**2, '-r')
        p4, = ax.semilogy(theta, abs(rp)**2, '--r')
        l1 = ax.legend([p1, p2], ['s', 'p'], loc=3)
        ax.legend([p1, p3], ['Mlayer/XOP', 'xrt'], loc=1)
        ax.add_artist(l1)
        ylim = ax.get_ylim()
        ax.set_ylim([ylim[0], 1])
# phases:
        ax2 = ax.twinx()
        ax2.set_ylabel(r'$\phi_s - \phi_p$', color='c')
        phi = np.unwrap(np.angle(rs * rp.conj()))
        p9, = ax2.plot(x, phi, 'c', lw=2, yunits=math.pi, zorder=0)
        formatter = mpl.ticker.FormatStrFormatter('%g' + r'$ \pi$')
        ax2.yaxis.set_major_formatter(formatter)
        for tl in ax2.get_yticklabels():
            tl.set_color('c')
        fname = 'SlabRefl' + stripe.name + ' ' + reprEnergy
        fig.savefig(fname + '.png')

    dataDir = os.path.join('', 'XOP-Reflectivities')
    theta = np.linspace(0, 10, 500)  # degrees
    layerW = rm.Material('W', kind='thin mirror', rho=19.3, t=2.5e-6)
    for_one_material(layerW,
                     os.path.join(dataDir, "W25A_10kev_s.mlayer.gz"),
                     os.path.join(dataDir, "W25A_10kev_p.mlayer.gz"), 1e4,
                     u'slab, t = 25 Å, @ 10 keV')


def compare_reflectivity_multilayer():
    """A comparison subroutine used in the module test suit."""
    def for_one_material(ml, refs, E, label):
        fig = plt.figure()
        fig.subplots_adjust(right=0.86)
        ax = fig.add_subplot(111)
        ax.set_xlabel('grazing angle (deg)')
        ax.set_ylabel('reflectivity')
        ax.set_xlim(theta[0], theta[-1])
        fig.suptitle(label, fontsize=16)
        x, R2s = np.loadtxt(refs, unpack=True)
        p1, = ax.plot(x, R2s, '-k', label='s Mlayer')
        refl = ml.get_amplitude(E, np.sin(np.deg2rad(theta)))
        rs, rp = refl[0], refl[1]
        p3, = ax.plot(theta, abs(rs)**2, '-r', lw=1)
        p4, = ax.plot(theta, abs(rp)**2, '--r')
        l1 = ax.legend([p3, p4], ['s', 'p'], loc=3)
        ax.legend([p1, p3], ['Mlayer/XOP', 'xrt'], loc=1)
        ax.add_artist(l1)
        ylim = ax.get_ylim()
        ax.set_ylim([ylim[0], 1])
# phases:
        ax2 = ax.twinx()
        ax2.set_ylabel(r'$\phi_s - \phi_p$', color='c')
        phi = np.unwrap(np.angle(rs * rp.conj()))
        p9, = ax2.plot(x, phi, 'c', lw=2, yunits=math.pi, zorder=0)
        formatter = mpl.ticker.FormatStrFormatter('%g' + r'$ \pi$')
        ax2.yaxis.set_major_formatter(formatter)
        for tl in ax2.get_yticklabels():
            tl.set_color('c')
        ax2.set_xlim(theta[0], theta[-1])

        fname = 'Multilayer' + ml.tLayer.name + ml.bLayer.name
        fig.savefig(fname + '.png')

    dataDir = os.path.join('', 'XOP-Reflectivities')
    theta = np.linspace(0, 1.6, 801)  # degrees
    mSi = rm.Material('Si', rho=2.33)
    mW = rm.Material('W', rho=19.3)
    mL = rm.Multilayer(mSi, 27, mW, 18, 40, mSi)
    for_one_material(mL, os.path.join(dataDir, "WSi45A04.mlayer.gz"), 8050,
                     u'40 × [27 Å Si + 18 Å W] multilayer @ 8.05 keV')


def compare_absorption_coeff():
    """A comparison subroutine used in the module test suit."""
    def for_one_material(mat, ref1, title):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_xlabel('energy (eV)')
        ax.set_ylabel(r'$\mu_0$ (cm$^{-1}$)')
        fig.suptitle(title, fontsize=16)
        x, mu0 = np.loadtxt(ref1, unpack=True)
        p1, = ax.loglog(x, mu0, '-k', lw=2, label='XCrossSec')
        calcmu0 = mat.get_absorption_coefficient(E)
        p3, = ax.loglog(E, calcmu0, '-r', label='xrt')
        ax.legend(loc=1)
        ax.set_xlim(E[0], E[-1])
        fname = title
        fig.savefig(fname + '.png')

    dataDir = os.path.join('', 'XOP-Reflectivities')
    E = np.logspace(1, 4.+math.log10(3.), 500)
    mat = rm.Material('Be', rho=1.848)
    for_one_material(mat, os.path.join(dataDir, "Be_absCoeff.xcrosssec.gz"),
                     u'Absorption in Be')


def compare_transmittivity():
    """A comparison subroutine used in the module test suit."""
    def for_one_material(mat, thickness, ref1, title, sname):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_xlabel('energy (eV)')
        ax.set_ylabel('transmittivity')
        fig.suptitle(title, fontsize=16)
        x, tr = np.loadtxt(ref1, unpack=True)
        p1, = ax.semilogx(x, tr, '-k', lw=2, label='XPower/XOP')
        calcmu0 = mat.get_absorption_coefficient(E)
        transm = np.exp(-calcmu0 * thickness)
        p3, = ax.semilogx(E, transm, '-r', label='xrt')
        ax.legend(loc=2)
        ax.set_xlim(E[0], E[-1])
        fname = 'Transm' + sname
        fig.savefig(fname + '.png')

    dataDir = os.path.join('', 'XOP-Reflectivities')
    E = np.logspace(2.+math.log10(3.), 4.+math.log10(3.), 500)
    matDiamond = rm.Material('C', rho=3.52)
    for_one_material(matDiamond, 60*1e-4,
                     os.path.join(dataDir, "Diamond60mum.xpower.gz"),
                     r'Transmittivity of 60-$\mu$m-thick diamond', 'Diamond')


def run_tests():
    """The body of the module test suit. Uncomment the tests you want."""

#Compare the calculated rocking curves of Si crystals with those calculated by
#XCrystal and XInpro (parts of XOP):
#    compare_rocking_curves('111')
#    compare_rocking_curves('333')
#    compare_rocking_curves('111', t=0.007)  # t is thickness in mm
#    compare_rocking_curves('333', t=0.007)
#    compare_rocking_curves('111', t=0.100)
#    compare_rocking_curves('333', t=0.100)
#    compare_rocking_curves('111', t=0.007, geom='Bragg transmitted')
#    compare_rocking_curves('333', t=0.007, geom='Bragg transmitted')
#    compare_rocking_curves('111', t=0.100, geom='Bragg transmitted')
#    compare_rocking_curves('333', t=0.100, geom='Bragg transmitted')
#    compare_rocking_curves('111', t=0.007, geom='Laue reflected')
#    compare_rocking_curves('333', t=0.007, geom='Laue reflected')
#    compare_rocking_curves('111', t=0.100, geom='Laue reflected')
#    compare_rocking_curves('333', t=0.100, geom='Laue reflected')
#    compare_rocking_curves('111', t=0.007, geom='Laue transmitted')
#    compare_rocking_curves('333', t=0.007, geom='Laue transmitted')
#    compare_rocking_curves('111', t=0.100, geom='Laue transmitted')
#    compare_rocking_curves('333', t=0.100, geom='Laue transmitted')

#check that Bragg transmitted and Laue transmitted give the same results if the
#beam path is equal:
#    beamPath = 0.1  # mm
#    compare_Bragg_Laue('111', beamPath=beamPath)
#    compare_Bragg_Laue('333', beamPath=beamPath)

#Compare the calculated reflectivities of Si, Pt, SiO_2 with those by Xf1f2
#(part of XOP):
#    compare_reflectivity()

#Compare the calculated reflectivities of W slab with those by Mlayer
#(part of XOP):
#    compare_reflectivity_slab()

#Compare the calculated reflectivities of W slab with those by Mlayer
#(part of XOP):
    compare_reflectivity_multilayer()

#Compare the calculated absorption coefficient with that by XCrossSec
#(part of XOP):
#    compare_absorption_coeff()

#Compare the calculated transmittivity with that by XPower
#(part of XOP):
#    compare_transmittivity()

#Play with Si crystal:
#    crystalSi = rm.CrystalSi(hkl=(1, 1, 1), tK=100.)
#    print 2 * crystalSi.get_a()/math.sqrt(3.)  # 2dSi111
#    print 'Si111 d-spacing = {0:.6f}'.format(crystalSi.d)
#    print crystalSi.get_Bragg_offset(8600, 8979)
#
#    crystalDiamond = rm.CrystalDiamond((1, 1, 1), 2.0592872, elements='C')
#    E = 9000.
#    print u'Darwin width at E={0:.0f} eV is {1:.5f} µrad for s-polarization'.\
#        format(E, crystalDiamond.get_Darwin_width(E) * 1e6)
#    print u'Darwin width at E={0:.0f} eV is {1:.5f} µrad for p-polarization'.\
#        format(E, crystalDiamond.get_Darwin_width(E, polarization='p') * 1e6)

    plt.show()
    print "finished"


if __name__ == '__main__':
    run_tests()
