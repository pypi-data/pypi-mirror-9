﻿# -*- coding: utf-8 -*-
"""
Module :mod:`plotter` provides classes describing axes and plots, as well as
containers for the accumulated arrays (histograms) for subsequent
pickling/unpickling or for global flux normalization. The module defines
several constants for default plot positions and sizes. The user may want to
modify them in the module or externally as in the xrt_logo.py example.

.. note::

    Each plot has a 2D positional histogram, two 1D positional histograms and,
    typically, a 1D color histogram (e.g. energy).

    .. warning::
        The two 1D positional histograms are not calculated from the 2D one!

    In other words, the 1D histograms only respect their corresponding limits
    and not the other dimension’s limits. There can be situations when the 2D
    image is black because the screen is misplaced but one 1D histogram may
    still show a beam distribution if in that direction the screen is
    positioned correctly. This was the reason why the 1D histograms were
    designed not to be directly dependent on the 2D one – this feature
    facilitates the troubleshooting of misalignments. On the other hand, this
    behavior may lead to confusion if a part of the 2D distribution is outside
    of the visible 2D area. In such cases one or two 1D histograms may show a
    wider distribution than the one visible on the 2D image. For correcting
    this behavior, one can mask the beam by apertures or by selecting the
    physical or optical limits of an optical element.

"""
__author__ = "Konstantin Klementiev, Roman Chernikov"
__date__ = "10 Apr 2015"

import os
import copy
import pickle
import numpy as np
import scipy as sp
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from . import runner
# from runner import runCardVals, runCardProcs
from .backends import raycing

# otherwise it does not work correctly on my Ubuntu9.10 and mpl 0.99.1.1:
mpl.rcParams['axes.unicode_minus'] = False
# mpl.rcParams['font.family'] = 'serif'
mpl.rcParams['axes.linewidth'] = 0.75
# mpl.rcParams['backend'] = 'Qt4Agg'
# mpl.rcParams['backend'] = 'Agg'
#mpl.rcParams['xtick.major.pad'] = '5'
#mpl.rcParams['ytick.major.pad'] = '5'

# [Sizes and positions of plots]
dpi = 100
xOrigin2d = 80  # all sizes are in pixels
yOrigin2d = 48
space2dto1d = 4
height1d = 84
xspace1dtoE1d = 112
yspace1dtoE1d = 76
heightE1dbar = 10
heightE1d = 84
xSpaceExtraWhenNoEHistogram = 42
xSpaceExtra = 22
ySpaceExtra = 28
# [Sizes and positions of texts]
xlabelpad = 4  # x-axis label to axis
ylabelpad = 4  # y-axis label to axis

xTextPos = 1.02  # 0 to 1 relative to the figure size
yTextPosNrays = 1.0
yTextPosNraysR = 1.32
yTextPosGoodrays = 0.8
yTextPosGoodraysR = 1.1
yTextPosI = 0.58
xTextPosDx = 0.5
yTextPosDx = 1.02
xTextPosDy = 1.05
yTextPosDy = 0.5
xTextPosStatus = 0.999
yTextPosStatus = 0.001
yTextPosNrays1 = 0.88
yTextPosNrays2 = 0.66
yTextPosNrays3 = 0.44
yTextPosNrays4 = 0.22
# [Bins]
defaultBins = 128
defaultPixelPerBin = 2
extraMargin = 4  # bins. Extra margins to histograms when limits are not given.
# [Axis labels]
axisLabelFontSize = 10
defaultXTitle = '$x$'
defaultXUnit = 'mm'
defaultYTitle = '$z$'
defaultYUnit = 'mm'
defaultCTitle = 'energy'
defaultCUnit = 'eV'
defaultFwhmFormatStrForXYAxes = '%.1f'
defaultFwhmFormatStrForCAxis = '%.2f'
# [Development]
colorFactor = 0.85  # 2./3 for red-to-blue
colorSaturation = 0.85
# # end of rc-file ##


class XYCAxis(object):
    """Contains a generic record structure describing each of the 3 axes:
    X, Y and Color (typ. Energy)."""
    def __init__(
            self, label='', unit='mm', factor=None, data='auto', limits=None,
            offset=0, bins=defaultBins, ppb=defaultPixelPerBin,
            invertAxis=False, outline=0.5,
            fwhmFormatStr=defaultFwhmFormatStrForXYAxes):
        """
        *label*: str
            The label of the axis without unit. This label will appear in the
            axis caption and in the FWHM label.
        *unit*: str
            The unit of the axis which will follow the label in parentheses
            and appear in the FWHM value.
        *factor*: float
            Useful in order to match your axis units with the units of the
            ray tracing backend. For instance, the shadow length unit is cm.
            If you want to display the positions as mm: *factor=10*;
            if you want to display energy as keV: *factor=1e-3*

            Another usage of *factor* is to bring the coordinates of the ray
            tracing backend to the world coordinates. For instance, z-axis in
            shadow is directed off the OE surface. If the OE is faced upside
            down, z is directed downwards. In order to display it upside, set
            minus to *factor*.

            if not specified, *factor* will default to a value that depends
            on *unit*. See :meth:`def auto_assign_factor`.

        *data*: int for shadow, otherwise array-like or function object
            shadow:
                zero-based index of columns in the shadow binary files:

                ======  ====================================================
                 0      x
                 1      y
                 2      z
                 3      x'
                 4      y'
                 5      z'
                 6      Ex s polariz
                 7      Ey s polariz
                 8      Ez s polariz
                 9      lost ray flag
                10      photon energy
                11      ray index
                12      optical path
                13      phase (s polarization)
                14      phase (p polarization)
                15      x component of the electromagnetic vector (p polar)
                16      y component of the electromagnetic vector (p polar)
                17      z component of the electromagnetic vector (p polar)
                18      empty
                ======  ====================================================

            raycing:
                use the following functions or pass your own one. See
                :mod:`raycing` for more functions, e.g. for the polarization
                properties. Alternatively, you may pass an array of the length
                of the beam arrays.

                =======  ===================================================
                 x       raycing.get_x
                 y       raycing.get_y
                 z       raycing.get_z
                 x'      raycing.get_xprime
                 z'      raycing.get_zprime
                 energy  raycing.get_energy
                =======  ===================================================

            If *data* = 'auto' then *label* is searched for "x", "y", "z",
            "x'", "z'", "energy" and if one of them is found, *data* is
            assigned to the listed above index or function. In raycing backend
            the automatic assignment is additionally implemented for *label*
            containing 'degree (for degree of polarization)', 'circular' (for
            circular polarization rate), 'path', 'incid' or 'theta' (for
            incident angle), 'order' (for grating diffraction order), 's',
            'phi', 'r' or 's' (for parametric representation of OE).

        *limits*: list [*min* : float, *max* : float]
            Axis limits. If None, the *limits* are taken as ``np.min`` and
            ``np.max`` for the corresponding array acquired after the 1st ray
            tracing run. If *limits* == 'symmetric', the limits are forced to
            be symmetric about the origin. Can also be set outside of the
            constructor as, e.g.::

                plot1.xaxis.limits = [-15, 15]

        *offset*: float
            An offset value subtracted from the axis tick labels to be
            displayed separately. It is useful for the energy axis, where the
            band width is most frequently much smaller than the central value.
            Ignored for x and y axes.

            +-----------------+--------------------+
            | no offset       |  non-zero offset   |
            +=================+====================+
            | |image_offset0| | |image_offset5000| |
            +-----------------+--------------------+

            .. |image_offset0| image:: _images/offset0.*
               :scale: 66 %
            .. |image_offset5000| image:: _images/offset5000.*
               :scale: 66 %

        *bins*: int
            Number of bins in the corresponding 1D and 2D histograms.
            See also *ppb* parameter.
        *ppb*: int
            Screen-pixel-per-bin value. The graph arrangement was optimized
            for *bins* * *ppb* = 256. If your *bins* and *ppb* give a very
            different product, the graphs may look ugly (disproportional)
            with overlapping tick labels.
        *invertAxis*: bool
            Inverts the axis direction. Useful for energy axis in energy-
            dispersive images in order to match the colors of the energy
            histogram with the colors of the 2D histogram.
        *outline*: float within [0, 1]
            Specifies the minimum brightness of the outline drawn over the
            1D histogram. The maximum brightness equals 1 at the maximum of
            the 1D histogram.

            +--------------------+--------------------+--------------------+
            |         =0         |         =0.5       |         =1         |
            +====================+====================+====================+
            | |image_outline0.0| | |image_outline0.5| | |image_outline1.0| |
            +--------------------+--------------------+--------------------+

            .. |image_outline0.0| image:: _images/outline00.png
               :scale: 66 %
            .. |image_outline0.5| image:: _images/outline05.png
               :scale: 66 %
            .. |image_outline1.0| image:: _images/outline10.png
               :scale: 66 %

        *fwhmFormatStr*: str
            Python format string for the FWHM value. if None, the FWHM value
            is not displayed.
        """
        self.label = label
        self.unit = unit
        if self.label:
            self.displayLabel = self.label
        else:
            self.displayLabel = ''
        if self.unit:
            self.displayLabel += ' (' + self.unit + ')'
        self.factor = factor
        self.data = data
        self.limits = limits
        self.offset = offset
        self.ppb = ppb
        self.pixels = bins * ppb
        self.reset_bins(bins)
        self.extraMargin = extraMargin
        self.invertAxis = invertAxis
        if outline < 0:
            outline = 0
        if outline > 1:
            outline = 1
        self.outline = outline
        self.fwhmFormatStr = fwhmFormatStr
        self.max1D = 0
        self.max1D_RGB = 0
        self.globalMax1D = 0
        self.globalMax1D_RGB = 0
        self.useCategory = False

    def reset_bins(self, bins):
        self.bins = bins
        self.binEdges = np.zeros(bins + 1)
        self.total1D = np.zeros(bins)
        self.total1D_RGB = np.zeros((bins, 3))

    def auto_assign_data(self, backend):
        """
        Automatically assign data arrays given the axis label."""
        if "energy" in self.label:
            if backend == 'shadow':
                self.data = 10
            elif backend == 'raycing':
                self.data = raycing.get_energy
        elif "x'" in self.label:
            if backend == 'shadow':
                self.data = 3
            elif backend == 'raycing':
                self.data = raycing.get_xprime
        elif "z'" in self.label:
            if backend == 'shadow':
                self.data = 5
            elif backend == 'raycing':
                self.data = raycing.get_zprime
        elif "x" in self.label:
            if backend == 'shadow':
                self.data = 0
            elif backend == 'raycing':
                self.data = raycing.get_x
        elif "y" in self.label:
            if backend == 'shadow':
                self.data = 1
            elif backend == 'raycing':
                self.data = raycing.get_y
        elif "z" in self.label:
            if backend == 'shadow':
                self.data = 2
            elif backend == 'raycing':
                self.data = raycing.get_z
        elif "degree" in self.label:
            self.data = raycing.get_polarization_degree
        elif "circular" in self.label:
            self.data = raycing.get_circular_polarization_rate
        elif "incid" in self.label or "theta" in self.label:
            self.data = raycing.get_incidence_angle
        elif "phi" in self.label:
            self.data = raycing.get_phi
        elif "order" in self.label:
            self.data = raycing.get_order
        elif "s" in self.label:
            self.data = raycing.get_s
        elif "path" in self.label:
            self.data = raycing.get_path
        elif "r" in self.label:
            self.data = raycing.get_r
        else:
            raise ValueError(
                'cannot auto-assign data for axis "{0}"!'.format(self.label))

    def auto_assign_factor(self, backend):
        """
        Automatically assign factor given the axis label."""
        factor = 1.
        if self.unit in ['keV', ]:
            factor = 1e-3
        elif self.unit in ['mrad', 'meV']:
            factor = 1.0e3
        elif self.unit in [u'$\mu$rad', u'µrad', u'µrad']:
            factor = 1.0e6
        else:
            if backend == 'shadow':
                if self.unit in ['m', ]:
                    factor = 1e-2
                elif self.unit in ['mm', ]:
                    factor = 10.
                elif self.unit in [u'$\mu$m', u'µm', u'µm']:
                    factor = 1.0e4
                elif self.unit in ['nm', ]:
                    factor = 1.0e7
            elif backend == 'raycing':
                if self.unit in ['m', ]:
                    factor = 1e-3
                elif self.unit in ['mm', ]:
                    factor = 1.
                elif self.unit in [u'$\mu$m', u'µm', u'µm']:
                    factor = 1.0e3
                elif self.unit in ['nm', ]:
                    factor = 1.0e6
                elif self.unit in ['pm', ]:
                    factor = 1.0e9
                elif self.unit in ['fm', ]:
                    factor = 1.0e12
        self.factor = factor


class OffsetFormatter(mpl.ticker.ScalarFormatter):
    """
     Removes the default scientific notation in the formatter of offset value.
    """
    def get_offset(self):
        s = ''
        if self.offset:
            s = '+' + str(self.offset)
        return self.fix_minus(s)


class XYCPlot(object):
    """Container for the accumulated histograms. Besides giving the beam
    images, this class provides with useful fields like *dx*, *dy*, *dE*
    (FWHM), *cx*, *cy*, *cE* (centers) and *intensity* which can be used in
    scripts for producing scan-like results."""
    def __init__(
            self, beam='', rayFlag=(1,), xaxis=None, yaxis=None, caxis=None,
            aspect='equal', xPos=1, yPos=1, ePos=1, title='',
            invertColorMap=False, negative=False,
            fluxKind='total', fluxUnit='auto',
            fluxFormatStr='%g', contourLevels=None, contourColors=None,
            contourFmt='%.1f', contourFactor=1., saveName=None,
            persistentName=None, oe=None, raycingParam=0,
            beamState=None, beamC=None):
        """
        *beam*: str
            The beam to be visualized.

            In raycing backend:
                The key in the dictionary returned by
                :func:`~xrt.backends.raycing.run.run_process()`. The values of
                that dictionary are beams (instances of
                :class:`~xrt.backends.raycing.sources.Beam`).

            In shadow backend:
                The Shadow output file (``star.NN``, `mirr.NN`` or
                ``screen.NNMM``). It will also appear in the window caption
                unless *title* parameter overrides it.

            This parameter is used for the automatic determination of the
            backend in use with the corresponding meaning of the next two
            parameters. If *beam* contains a dot, shadow backend is assumed.
            Otherwise raycing backend is assumed.
        *rayFlag*: int or tuple of ints
            shadow: 0=lost rays, 1=good rays, 2=all rays.
            raycing: a tuple of integer ray states: 1=good, 2=out, 3=over,
            4=alive (good + out), -NN = dead at oe number NN (numbering starts
            with 1).
        *xaxis*, *yaxis*, *caxis*: instance of :class:`XYCAxis` or None.
            If None, a default axis is created. If caxis='category' and the
            backend is raycing, then the coloring is given by ray category, the
            color axis histogram is not displayed and *ePos* is ignored.
        *aspect*: str or float
            Aspect ratio of the 2D histogram, = 'equal', 'auto' or numeric
            value (=x/y). *aspect* =1 is the same as *aspect* ='equal'.
        *xPos*, *yPos*: int
            If non-zero, the corresponding 1D histograms are visible.
        *ePos*: int
            Flag for specifying the positioning of the color axis histogram:

            +--------------------------------------------+---------------+
            | *ePos* =1: at the right (default, as       | |image_ePos1| |
            | usually the diffraction plane is vertical) |               |
            +--------------------------------------------+---------------+
            | *ePos* =2: at the top                      | |image_ePos2| |
            | (for horizontal diffraction plane)         |               |
            +--------------------------------------------+---------------+
            | *ePos* =0: no color axis histogram         | |image_ePos0| |
            +--------------------------------------------+---------------+

            .. |image_ePos1| image:: _images/ePos=1.*
               :scale: 50 %
            .. |image_ePos2| image:: _images/ePos=2.*
               :scale: 50 %
            .. |image_ePos0| image:: _images/ePos=0.*
               :scale: 50 %

        *title*: str
            If non-empty, this string will appear in the window caption,
            otherwise the *beam* will be used for this.
        *invertColorMap*: bool
            Inverts colors in the HSV color map; seen differently, this is a
            0.5 circular shift in the color map space. This inversion is
            useful in combination with *negative* in order to keep the same
            energy coloring both for black and for white images.
        *negative*: bool
            Useful for printing in order to save black inks.
            See also *invertColorMap*.

            * =False: black bknd for on-screen presentation
            * =True: white bknd for paper printing

            The following table demonstrates the combinations of
            *invertColorMap* and *negative*:

            +-------------------+------------------+------------------+
            |                   | *invertColorMap* | *invertColorMap* |
            |                   |      =False      |       =True      |
            +===================+==================+==================+
            | *negative* =False |    |image00|     |    |image10|     |
            +-------------------+------------------+------------------+
            | *negative* =True  |    |image01|     |    |image11|     |
            +-------------------+------------------+------------------+

            .. |image00| image:: _images/invertColorMap=0_negative=0.png
               :scale: 50 %
            .. |image01| image:: _images/invertColorMap=0_negative=1.png
               :scale: 50 %
            .. |image10| image:: _images/invertColorMap=1_negative=0.png
               :scale: 50 %
            .. |image11| image:: _images/invertColorMap=1_negative=1.png
               :scale: 50 %

            Note that *negative* inverts only the colors of the graphs, not
            the white global background. Use a common graphical editor to
            invert the whole picture after doing *negative=True*:

            .. image:: _images/negative=1+fullNegative.png
               :scale: 50 %

            (such a picture would nicely look on a black journal cover, e.g.
            on that of Journal of Synchrotron Radiation ;) )

        *fluxKind*: str
            Can begin with 's', 'p', '+-45', 'left-right', 'total' and 'power'.
            Specifies what kind of flux to use for the brightness of 2D
            and for the height of 1D histograms. If it ends with 'log', the
            flux scale is logarithmic.
        *fluxUnit*: 'auto' or None
            If a synchrotron source is used and *fluxUnit* is 'auto', the
            flux will be displayed as 'ph/s' or 'W' (if *fluxKind* == 'power').
            Otherwise the flux is a unitless number of rays times
            transmittivity | reflectivity.
        *fluxFormatStr*: str
            Format string for representing the flux or power. You can use a
            representation with powers of ten by utilizing 'p' as format
            specifier, e.g. '%.2p'.

        *contourLevels*: sequence
            A sequence of levels on the 2D image for drawing the contours, in
            [0, 1] range. If None, the contours are not drawn.
        *contourColors*: sequence or color
            A sequence of colors corresponding to *contourLevels*. A single
            color value is applied to all the contours. If None, the colors are
            automatic.
        *contourFmt*: str
            Python format string for contour values.
        *contourFactor*: float
            Is applied to the levels and is useful in combination with
            *contourFmt*, e.g. *contourFmt* = r'%.1f mW/mm$^2$',
            *contourFactor* = 1e3.

        *saveName*: str or list of str or None
            Save file name(s). The file type(s) are given by extensions:
            png, ps, svg, pdf. Typically, *saveName* is set outside of the
            constructor. For example::

                filename = 'filt%04imum' %thick #without extension
                plot1.saveName = [filename + '.pdf', filename + '.png']

        .. _persistentName:

        *persistentName*: str or None
            File name for reading and storing the accumulated histograms and
            other ancillary data. Ray tracing will resume the histogramming
            from the state when the persistent file was written. If the file
            does not exist yet, the histograms are initialized to zeros. The
            persistent file is rewritten when ray tracing is completed and
            the number of repeats > 0. Be careful when you use it: if you
            intend to start from zeros, make sure that this option is switched
            off or the pickle files are deleted!

            if *persistentName* ends with '.mat', a Matlab file is generated.
        *oe*: instance of descendants of
            class :class:`xrt.backends.raycing.oes.OE` or None.
            If supplied, the rectangular or circular areas of the optical
            surfaces or physical surfaces, if the optical surfaces are not
            specified, will be overdrawn. Useful with raycing backend for
            footprint images.
        *raycingParam*: int
            Used together with the *oe* parameter above for drawing footprint
            envelopes. If =2, the limits of the second crystal of DCM are taken
            for drawing the envelope; if =1000, all facets of a diced crystal
            are displayed.
        *beamState*: str
            Used in raycing backend. If not None, gives another beam that
            determines the state (good, lost etc.) instead of the state given
            by *beam*. This may be used to visualize the *incoming* beam but
            use the states of the *outgoing* beam, so that you see how the beam
            upstream of the optical element will be masked by it. See the
            examples for capillaries.
        *beamC*: str
            The same as *beamState* but refers to colors (when not of
            'category' type).
        """
        plt.ion()
        self.colorSaturation = colorSaturation

        self.beam = beam  # binary shadow image: star, mirr or screen
        if '.' in beam:
            self.backend = 'shadow'
        elif ('dummy' in beam) or (beam == ''):
            self.backend = 'dummy'
        elif isinstance(rayFlag, tuple):
            self.backend = 'raycing'
        else:
            self.backend = 'dummy'
        self.beamState = beamState
        self.beamC = beamC
        self.rayFlag = rayFlag
        if xaxis is None:
            self.xaxis = XYCAxis(defaultXTitle, defaultXUnit)
        else:
            self.xaxis = xaxis
        if yaxis is None:
            self.yaxis = XYCAxis(defaultYTitle, defaultYUnit)
        else:
            self.yaxis = yaxis
        if (caxis is None) or isinstance(caxis, basestring):
            self.caxis = XYCAxis(defaultCTitle, defaultCUnit, factor=1.,)
            self.caxis.fwhmFormatStr = defaultFwhmFormatStrForCAxis
            if isinstance(caxis, basestring):
                self.caxis.useCategory = True
                ePos = 0
        else:
            self.caxis = caxis

        self.fluxKind = fluxKind
        self.fluxUnit = fluxUnit

        if self.backend != 'dummy':
            for axis in self.xaxis, self.yaxis, self.caxis:
                if axis.data == 'auto':
                    axis.auto_assign_data(self.backend)
                if axis.factor is None:
                    axis.auto_assign_factor(self.backend)

        self.reset_bins2D()

        if isinstance(aspect, (int, float)):
            if aspect <= 0:
                aspect = 1.
        self.aspect = aspect
        self.dpi = dpi

        self.ePos = ePos  # Position of E histogram, 1=right, 2=top, 0=none

        self.negative = negative
        if self.negative:
            axisbg = 'w'  # white
        else:
            axisbg = 'k'  # black
        self.invertColorMap = invertColorMap
        self.utilityInvertColorMap = False
        self.fluxFormatStr = fluxFormatStr
        self.saveName = saveName
        self.persistentName = persistentName
        self.cx, self.dx = 0, 0
        self.cy, self.dy = 0, 0
        self.cE, self.dE = 0, 0

        xFigSize = float(xOrigin2d + self.xaxis.pixels + space2dto1d +
                         height1d + xSpaceExtra)
        yFigSize = float(yOrigin2d + self.yaxis.pixels + space2dto1d +
                         height1d + ySpaceExtra)
        if self.ePos == 1:
            xFigSize += xspace1dtoE1d + heightE1d + heightE1dbar
        elif self.ePos == 2:
            yFigSize += yspace1dtoE1d + heightE1d + heightE1dbar
        if self.ePos != 1:
            xFigSize += xSpaceExtraWhenNoEHistogram

        self.fig = plt.figure(figsize=(xFigSize/dpi, yFigSize/dpi), dpi=dpi)
        self.fig.delaxes(self.fig.gca())
        if title != '':
            self.title = title
        elif isinstance(beam, basestring):
            self.title = beam
        else:
            self.title = ' '
        self.fig.canvas.set_window_title(self.title)

        if plt.get_backend().lower() in (
                x.lower() for x in mpl.rcsetup.non_interactive_bk):
            xExtra = 0  # mpl backend-dependent (don't know why) pixel sizes
            yExtra = 0  # mpl backend-dependent (don't know why) pixel sizes
        else:  # interactive backends:
            if True:  # runner.runCardVals.repeats > 1:
                xExtra = 0
                yExtra = 2
            else:
                xExtra = 0
                yExtra = 0

        frameon = True
        rect2d = [xOrigin2d / xFigSize, yOrigin2d / yFigSize,
                  (self.xaxis.pixels-1+xExtra) / xFigSize,
                  (self.yaxis.pixels-1+yExtra) / yFigSize]
        self.ax2dHist = self.fig.add_axes(
            rect2d, aspect=aspect, xlabel=self.xaxis.displayLabel,
            ylabel=self.yaxis.displayLabel, axisbg=axisbg, autoscale_on=False,
            frameon=frameon)
        self.ax2dHist.xaxis.labelpad = xlabelpad
        self.ax2dHist.yaxis.labelpad = ylabelpad

        rect1dX = copy.deepcopy(rect2d)
        rect1dX[1] = rect2d[1] + rect2d[3] + space2dto1d/yFigSize
        rect1dX[3] = height1d / yFigSize
        self.ax1dHistX = self.fig.add_axes(
            rect1dX, axisbg=axisbg, sharex=self.ax2dHist, autoscale_on=False,
            frameon=frameon, visible=(xPos != 0))

        rect1dY = copy.deepcopy(rect2d)
        rect1dY[0] = rect2d[0] + rect2d[2] + space2dto1d/xFigSize
        rect1dY[2] = height1d / xFigSize
        self.ax1dHistY = self.fig.add_axes(
            rect1dY, axisbg=axisbg, sharey=self.ax2dHist, autoscale_on=False,
            frameon=frameon, visible=(yPos != 0))

        # make some labels invisible
        plt.setp(
            self.ax1dHistX.get_xticklabels() +
            self.ax1dHistY.get_yticklabels() +
            self.ax1dHistY.get_xticklabels() +
            self.ax1dHistX.get_yticklabels(), visible=False)

        plt.setp(
            self.ax1dHistY.yaxis.offsetText,
            position=(-float(self.xaxis.pixels+space2dto1d) / height1d, 0),
            ha='right')

        self.ax1dHistX.xaxis.set_major_formatter(OffsetFormatter(
            useOffset=False))
        self.ax1dHistY.yaxis.set_major_formatter(OffsetFormatter(
            useOffset=False))
#        for tick in (self.ax2dHist.xaxis.get_major_ticks() + \
#          self.ax2dHist.yaxis.get_major_ticks()):
#            tick.label1.set_fontsize(axisLabelFontSize)
        if self.ePos == 1:  # right
            rect1dE = copy.deepcopy(rect1dY)
            rect1dE[0] = rect1dY[0] + rect1dY[2] + xspace1dtoE1d/xFigSize
            rect1dE[2] = heightE1dbar / xFigSize
            rect1dE[3] *= float(self.caxis.pixels) / self.yaxis.pixels
            self.ax1dHistEbar = self.fig.add_axes(
                rect1dE, ylabel=self.caxis.displayLabel, axisbg=axisbg,
                autoscale_on=False, frameon=frameon)
            self.ax1dHistEbar.yaxis.labelpad = xlabelpad
            rect1dE[0] += rect1dE[2]
            rect1dE[2] = heightE1d / xFigSize
            self.ax1dHistE = self.fig.add_axes(
                rect1dE, sharey=self.ax1dHistEbar, axisbg=axisbg,
                autoscale_on=False, frameon=frameon)
            plt.setp(
                self.ax1dHistEbar.get_xticklabels() +
                self.ax1dHistE.get_xticklabels() +
                self.ax1dHistE.get_yticklabels(), visible=False)
            plt.setp(self.ax1dHistE.yaxis.offsetText, visible=False)
            plt.setp(self.ax1dHistEbar, xticks=())
            self.ax1dHistE.yaxis.set_major_formatter(
                OffsetFormatter(useOffset=False))
            if self.caxis.limits is not None:
                self.ax1dHistE.set_ylim(self.caxis.limits)
        elif self.ePos == 2:  # top
            rect1dE = copy.deepcopy(rect1dX)
            rect1dE[1] = rect1dX[1] + rect1dX[3] + yspace1dtoE1d/yFigSize
            rect1dE[3] = heightE1dbar / yFigSize
            rect1dE[2] *= float(self.caxis.pixels) / self.xaxis.pixels
            self.ax1dHistEbar = self.fig.add_axes(
                rect1dE, xlabel=self.caxis.displayLabel, axisbg=axisbg,
                autoscale_on=False, frameon=frameon)
            self.ax1dHistEbar.xaxis.labelpad = xlabelpad
            rect1dE[1] += rect1dE[3]
            rect1dE[3] = heightE1d / yFigSize
            self.ax1dHistE = self.fig.add_axes(
                rect1dE, sharex=self.ax1dHistEbar, axisbg=axisbg,
                autoscale_on=False, frameon=frameon)
            plt.setp(
                self.ax1dHistEbar.get_yticklabels() +
                self.ax1dHistE.get_yticklabels() +
                self.ax1dHistE.get_xticklabels(), visible=False)
            plt.setp(self.ax1dHistE.xaxis.offsetText, visible=False)
            plt.setp(self.ax1dHistEbar, yticks=())
            self.ax1dHistE.xaxis.set_major_formatter(
                OffsetFormatter(useOffset=False))
            if self.caxis.limits is not None:
                self.ax1dHistE.set_xlim(self.caxis.limits)

        allAxes = [self.ax1dHistX, self.ax1dHistY, self.ax2dHist]
        if self.ePos != 0:
            allAxes.append(self.ax1dHistE)
            allAxes.append(self.ax1dHistEbar)
        for ax in allAxes:
            for axXY in (ax.xaxis, ax.yaxis):
                for line in axXY.get_ticklines():
                    line.set_color('grey')

        if self.ePos == 1:
            self.textDE = plt.text(
                xTextPosDy, yTextPosDy, ' ', rotation='vertical',
                transform=self.ax1dHistE.transAxes, ha='left', va='center')
        elif self.ePos == 2:
            self.textDE = plt.text(
                xTextPosDx, yTextPosDx, ' ',
                transform=self.ax1dHistE.transAxes, ha='center', va='bottom')

        self.nRaysAll = 0
        self.nRaysAllRestored = -1
        self.intensity = 0
        transform = self.ax1dHistX.transAxes
        self.textGoodrays = None
        self.textI = None
        self.power = 0
        self.flux = 0
        self.contourLevels = contourLevels
        self.contourColors = contourColors
        self.contourFmt = contourFmt
        self.contourFactor = contourFactor
        self.displayAsAbsorbedPower = False

        self.textNrays = None
        if self.backend == 'shadow' or self.backend == 'dummy':
            self.textNrays = plt.text(
                xTextPos, yTextPosNrays, ' ', transform=transform, ha='left',
                va='top')
            self.nRaysNeeded = long(0)
            if self.rayFlag != 2:
                self.textGoodrays = plt.text(
                    xTextPos, yTextPosGoodrays, ' ', transform=transform,
                    ha='left', va='top')
            self.textI = plt.text(
                xTextPos, yTextPosI, ' ', transform=transform, ha='left',
                va='top')
        elif self.backend == 'raycing':
            # =0: ignored, =1: good,
            # =2: reflected outside of working area, =3: transmitted without
            #     intersection
            # =-NN: lost (absorbed) at OE#NN-OE numbering starts from 1 !!!
            #       If NN>1000 then
            # the slit with ordinal number NN-1000 is meant.
            self.nRaysAlive = long(0)
            self.nRaysGood = long(0)
            self.nRaysOut = long(0)
            self.nRaysOver = long(0)
            self.nRaysDead = long(0)
            self.nRaysAccepted = long(0)
            self.nRaysAcceptedE = 0.
            self.nRaysSeeded = long(0)
            self.nRaysSeededI = 0.
            self.textNrays = plt.text(
                xTextPos, yTextPosNraysR, ' ', transform=transform, ha='left',
                va='top')
            self.textGood = None
            self.textOut = None
            self.textOver = None
            self.textAlive = None
            self.textDead = None
            if 1 in self.rayFlag:
                self.textGood = plt.text(
                    xTextPos, yTextPosNrays1, ' ', transform=transform,
                    ha='left', va='top')
            if 2 in self.rayFlag:
                self.textOut = plt.text(
                    xTextPos, yTextPosNrays2, ' ', transform=transform,
                    ha='left', va='top')
            if 3 in self.rayFlag:
                self.textOver = plt.text(
                    xTextPos, yTextPosNrays3, ' ', transform=transform,
                    ha='left', va='top')
            if 4 in self.rayFlag:
                self.textAlive = plt.text(
                    xTextPos, yTextPosGoodraysR, ' ', transform=transform,
                    ha='left', va='top')
            if not self.caxis.useCategory:
                self.textI = plt.text(
                    xTextPos, yTextPosNrays4, ' ', transform=transform,
                    ha='left', va='top')
            else:
                if (np.array(self.rayFlag) < 0).sum() > 0:
                    self.textDead = plt.text(
                        xTextPos, yTextPosNrays4, ' ', transform=transform,
                        ha='left', va='top')

        self.textDx = plt.text(
            xTextPosDx, yTextPosDx, ' ', transform=self.ax1dHistX.transAxes,
            ha='center', va='bottom')
        self.textDy = plt.text(
            xTextPosDy, yTextPosDy, ' ', rotation='vertical',
            transform=self.ax1dHistY.transAxes, ha='left', va='center')
        self.textStatus = plt.text(
            xTextPosStatus, yTextPosStatus, '', transform=self.fig.transFigure,
            ha='right', va='bottom')
        self.textStatus.set_color('r')

        self.ax1dHistX.imshow(
            np.zeros((2, 2, 3)), aspect='auto', interpolation='nearest',
            origin='lower', figure=self.fig, lod=True)
        self.ax1dHistY.imshow(
            np.zeros((2, 2, 3)), aspect='auto', interpolation='nearest',
            origin='lower', figure=self.fig, lod=True)
        if self.ePos != 0:
            self.ax1dHistE.imshow(
                np.zeros((2, 2, 3)), aspect='auto', interpolation='nearest',
                origin='lower', figure=self.fig, lod=True)
            self.ax1dHistEbar.imshow(
                np.zeros((2, 2, 3)), aspect='auto', interpolation='nearest',
                origin='lower', figure=self.fig, lod=True)
        self.ax2dHist.imshow(
            np.zeros((2, 2, 3)), aspect=self.aspect, interpolation='nearest',
            origin='lower', figure=self.fig, lod=True)
        self.contours2D = None

        self.oe = oe
        self.oeSurfaceLabels = []
        self.raycingParam = raycingParam
        self.draw_footprint_area()
        if self.xaxis.limits is not None:
            if not isinstance(self.xaxis.limits, str):
                self.ax2dHist.set_xlim(self.xaxis.limits)
                self.ax1dHistX.set_xlim(self.xaxis.limits)
        if self.yaxis.limits is not None:
            if not isinstance(self.yaxis.limits, str):
                self.ax2dHist.set_ylim(self.yaxis.limits)
                self.ax1dHistY.set_ylim(self.yaxis.limits)

        self.cidp = self.fig.canvas.mpl_connect(
            'button_press_event', self.on_press)
        plt.ioff()
        self.fig.canvas.draw()

    def reset_bins2D(self):
        self.total2D = np.zeros((self.yaxis.bins, self.xaxis.bins))
        self.total2D_RGB = np.zeros((self.yaxis.bins, self.xaxis.bins, 3))
        self.max2D_RGB = 0
        self.globalMax2D_RGB = 0

    def update_user_elements(self):
        return  # 'user message'

    def clean_user_elements(self):
        pass

    def on_press(self, event):
        """
        Defines the right button click event for stopping the loop.
        """
        if event.button == 3:
            runner.runCardVals.stop_event.set()
            self.textStatus.set_text("stopping ...")

    def timer_callback(self, evt=None):
        """
        This code will be executed on every timer tick. We have to start
        :meth:`runner.dispatch_jobs` here as otherwise we cannot force the
        redrawing.
        """
        if self.areProcessAlreadyRunning:
            return
        self.areProcessAlreadyRunning = True
        runner.dispatch_jobs()

    def set_axes_limits(self, xmin, xmax, ymin, ymax, emin, emax):
        """
        Used in multiprocessing for automatic limits of the 3 axes: x, y and
        energy (caxis). It is meant only for the 1st ray tracing run.
        """
#        if (self.xaxis.limits is None) or isinstance(self.xaxis.limits, str):
# the check is not needed: even if the limits have been already set, they may
# change due to *aspect*; this is checked in :mod:`multipro`.
        self.xaxis.limits = [xmin, xmax]
        self.yaxis.limits = [ymin, ymax]
        self.caxis.limits = [emin, emax]

    def draw_footprint_area(self):
        """
        Useful with raycing backend for footprint images.
        """
        if self.oe is None:
            return
        if self.oe.surface is None:
            return
        if isinstance(self.oe.surface, basestring):
            surface = self.oe.surface,
        else:
            surface = self.oe.surface

        if len(self.oeSurfaceLabels) > 0:
            for isurf, surf in enumerate(surface):
                self.oeSurfaceLabels[isurf].set_text(surf)
                return
        r = [0, 0, 0, 0]
        if self.raycingParam == 2:  # the second crystal of DCM
            limsPhys = self.oe.limPhysX2, self.oe.limPhysY2
            limsOpt = self.oe.limOptX2, self.oe.limOptY2
        elif (self.raycingParam >= 1000) and hasattr(self.oe, "xStep"):
            # all facets of a diced crystal
            if self.oe.limPhysX[1] == np.inf:
                return
            if self.oe.limPhysY[1] == np.inf:
                return
            if self.xaxis.limits is None:
                return
            if self.yaxis.limits is None:
                return
            ixMin = int(round(max(self.oe.limPhysX[0], self.xaxis.limits[0]) /
                        self.oe.xStep))
            ixMax = int(round(min(self.oe.limPhysX[1], self.xaxis.limits[1]) /
                        self.oe.xStep))
            iyMin = int(round(max(self.oe.limPhysY[0], self.yaxis.limits[0]) /
                        self.oe.yStep))
            iyMax = int(round(min(self.oe.limPhysY[1], self.yaxis.limits[1]) /
                        self.oe.yStep))
            surface = []
            limFacetXMin, limFacetXMax = [], []
            limFacetYMin, limFacetYMax = [], []
            for ix in range(ixMin, ixMax+1):
                for iy in range(iyMin, iyMax+1):
                    surface.append('')
                    cx = ix * self.oe.xStep
                    cy = iy * self.oe.yStep
                    dxHalf = self.oe.dxFacet / 2
                    dyHalf = self.oe.dyFacet / 2
                    limFacetXMin.append(max(cx-dxHalf, self.oe.limPhysX[0]))
                    limFacetXMax.append(min(cx+dxHalf, self.oe.limPhysX[1]))
                    limFacetYMin.append(max(cy-dyHalf, self.oe.limPhysY[0]))
                    limFacetYMax.append(min(cy+dyHalf, self.oe.limPhysY[1]))
            limsPhys = \
                (limFacetXMin, limFacetXMax), (limFacetYMin, limFacetYMax)
            limsOpt = None, None
        else:
            limsPhys = self.oe.limPhysX, self.oe.limPhysY
            limsOpt = self.oe.limOptX, self.oe.limOptY
        for isurf, surf in enumerate(surface):
            for ilim1, ilim2, limPhys, limOpt in zip(
                    (0, 2), (1, 3), limsPhys, limsOpt):
                if limOpt is not None:
                    if raycing.is_sequence(limOpt[0]):
                        r[ilim1], r[ilim2] = limOpt[0][isurf], limOpt[1][isurf]
                    else:
                        r[ilim1], r[ilim2] = limOpt[0], limOpt[1]
                else:
                    if raycing.is_sequence(limPhys[0]):
                        r[ilim1], r[ilim2] = \
                            limPhys[0][isurf], limPhys[1][isurf]
                    else:
                        r[ilim1], r[ilim2] = limPhys[0], limPhys[1]
            if isinstance(self.oe.shape, str):
                if self.oe.shape.startswith('ro') and\
                        (self.raycingParam < 1000):
                    envelope = mpl.patches.Circle(
                        ((r[1]+r[0])*0.5, (r[3]+r[2])*0.5), (r[1]-r[0])*0.5,
                        fc="#aaaaaa", lw=0, alpha=0.25)
                elif self.oe.shape.startswith('rect') or\
                        (self.raycingParam >= 1000):
                    envelope = mpl.patches.Rectangle(
                        (r[0], r[2]), r[1] - r[0], r[3] - r[2],
                        fc="#aaaaaa", lw=0, alpha=0.25)
            elif isinstance(self.oe.shape, list):
                envelope = mpl.patches.Polygon(self.oe.shape, closed=True,
                                               fc="#aaaaaa", lw=0, alpha=0.25)
            self.ax2dHist.add_patch(envelope)
            if self.raycingParam < 1000:
                if self.yaxis.limits is not None:
                    yTextPos = max(r[2], self.yaxis.limits[0])
                else:
                    yTextPos = r[2]
                osl = self.ax2dHist.text(
                    (r[0]+r[1]) * 0.5, yTextPos, surf, ha='center',
                    va='bottom', color='w')
                self.oeSurfaceLabels.append(osl)

    def plot_hist1d(self, what_axis_char):
        """Plots the specified 1D histogram as imshow and calculates FWHM with
        showing the ends of the FWHM bar.
        Parameters:
            *what_axis_char*: str [ 'x' | 'y' | 'c' ]
                defines the axis
        Returns:
            *center*, *fwhm*: floats
                the center and fwhm values for later displaying.
        """
        if what_axis_char == 'x':
            axis = self.xaxis
            graph = self.ax1dHistX
            orientation = 'horizontal'
            histoPixelHeight = height1d
        elif what_axis_char == 'y':
            axis = self.yaxis
            graph = self.ax1dHistY
            orientation = 'vertical'
            histoPixelHeight = height1d
        elif what_axis_char == 'c':
            axis = self.caxis
            graph = self.ax1dHistE
            if self.ePos == 1:
                orientation = 'vertical'
            elif self.ePos == 2:
                orientation = 'horizontal'
            histoPixelHeight = heightE1d
        if orientation == 'horizontal':
            graph.xaxis.get_major_formatter().offset = axis.offset
        else:  # 'vertical'
            graph.yaxis.get_major_formatter().offset = axis.offset

        axis.max1D = float(np.max(axis.total1D))
        if axis.max1D > 0:
            if runner.runCardVals.passNo > 0:
                mult = 1.0 / axis.globalMax1D
            else:
                mult = 1.0 / axis.max1D
            xx = axis.total1D * mult
        else:
            xx = axis.total1D
        if runner.runCardVals.passNo > 0:
            xxMaxHalf = float(np.max(xx)) * 0.5  # for calculating FWHM
        else:
            xxMaxHalf = 0.5

        axis.max1D_RGB = float(np.max(axis.total1D_RGB))
        if axis.max1D_RGB > 0:
            if runner.runCardVals.passNo > 1:
                mult = 1.0 / axis.globalMax1D_RGB
            else:
                mult = 1.0 / axis.max1D_RGB
            xxRGB = axis.total1D_RGB * mult
        else:
            xxRGB = axis.total1D_RGB

        if orientation[0] == 'h':
            map2d = np.zeros((histoPixelHeight, len(xx), 3))
            for ix, cx in enumerate(xx):
                maxPixel = round((histoPixelHeight-1) * cx)
                if 0 <= maxPixel <= (histoPixelHeight-1):
                    map2d[0:maxPixel, ix, :] = xxRGB[ix, :]
                    if axis.outline:
                        maxRGB = np.max(xxRGB[ix, :])
                        if maxRGB > 1e-20:
                            scaleFactor = \
                                1 - axis.outline + axis.outline/maxRGB
                            map2d[maxPixel-1, ix, :] *= scaleFactor
            extent = None
            if (axis.limits is not None) and\
                    (not isinstance(axis.limits, str)):
                extent = [axis.limits[0], axis.limits[1], 0, 1]
        elif orientation[0] == 'v':
            map2d = np.zeros((len(xx), histoPixelHeight, 3))
            for ix, cx in enumerate(xx):
                maxPixel = round((histoPixelHeight-1) * cx)
                if 0 <= maxPixel <= (histoPixelHeight-1):
                    map2d[ix, 0:maxPixel, :] = xxRGB[ix, :]
                    if axis.outline:
                        maxRGB = np.max(xxRGB[ix, :])
                        if maxRGB > 1e-20:
                            scaleFactor = \
                                1 - axis.outline + axis.outline/maxRGB
                            map2d[ix, maxPixel-1, :] *= scaleFactor
            extent = None
            if (axis.limits is not None) and \
                    not (isinstance(axis.limits, str)):
                extent = [0, 1, axis.limits[0], axis.limits[1]]

        if self.negative:
            map2d = 1 - map2d
        if self.utilityInvertColorMap:
            map2d = mpl.colors.rgb_to_hsv(map2d)
            map2d[:, :, 0] -= 0.5
            map2d[map2d < 0] += 1
            map2d = mpl.colors.hsv_to_rgb(map2d)
        graph.images[0].set_data(map2d)
        if extent is not None:
            graph.images[0].set_extent(extent)

        del graph.lines[:]  # otherwise it accumulates the FWHM lines
        if axis.max1D > 0:
            args = np.argwhere(xx >= xxMaxHalf)
            iHistFWHMlow = np.min(args)
            iHistFWHMhigh = np.max(args) + 1
            histFWHMlow = axis.binEdges[iHistFWHMlow]
            histFWHMhigh = axis.binEdges[iHistFWHMhigh]
            if axis.fwhmFormatStr is not None:
                if orientation[0] == 'h':
                    graph.plot([histFWHMlow, histFWHMhigh],
                               [xxMaxHalf, xxMaxHalf], '+', color='grey')
                elif orientation[0] == 'v':
                    graph.plot([xxMaxHalf, xxMaxHalf],
                               [histFWHMlow, histFWHMhigh], '+', color='grey')
        else:
            histFWHMlow = 0
            histFWHMhigh = 0

        if orientation[0] == 'h':
            if not isinstance(axis.limits, str):
                graph.set_xlim(axis.limits)
            graph.set_ylim([0, 1])
        elif orientation[0] == 'v':
            graph.set_xlim([0, 1])
            if not isinstance(axis.limits, str):
                graph.set_ylim(axis.limits)

        weighted1D = \
            axis.total1D * (axis.binEdges[:-1]+axis.binEdges[1:]) * 0.5
        xxAve = axis.total1D.sum()
        if xxAve != 0:
            xxAve = weighted1D.sum() / xxAve
        return xxAve, histFWHMhigh - histFWHMlow

    def plot_colorbar(self):
        """
        Plots a color bar adjacent to the caxis 1D histogram.
        """
        a = np.linspace(0, colorFactor, self.caxis.pixels, endpoint=True)
        a = np.asarray(a).reshape(1, -1)
        if self.invertColorMap:
            a -= 0.5
            a[a < 0] += 1
        if self.caxis.limits is None:
            return
        eMin, eMax = self.caxis.limits
        a = np.vstack((a, a))
        if self.ePos == 1:
            a = a.T
            extent = [0, 1, eMin, eMax]
        else:
            extent = [eMin, eMax, 0, 1]

        a = np.dstack(
            (a, np.ones_like(a) * self.colorSaturation, np.ones_like(a)))
        a = mpl.colors.hsv_to_rgb(a)
        if self.negative:
            a = 1 - a
        self.ax1dHistEbar.images[0].set_data(a)
        self.ax1dHistEbar.images[0].set_extent(extent)

        if self.caxis.invertAxis:
            if self.ePos == 2:
                self.ax1dHistEbar.set_xlim(self.ax1dHistEbar.get_xlim()[::-1])
            elif self.ePos == 1:
                self.ax1dHistEbar.set_ylim(self.ax1dHistEbar.get_ylim()[::-1])

    def plot_hist2d(self):
        """
        Plots the 2D histogram as imshow.
        """
        self.max2D_RGB = float(np.max(self.total2D_RGB))
        if self.max2D_RGB > 0:
            if runner.runCardVals.passNo > 1:
                mult = 1.0 / self.globalMax2D_RGB
            else:
                mult = 1.0 / self.max2D_RGB
            xyRGB = self.total2D_RGB * mult
        else:
            xyRGB = self.total2D_RGB
        if self.negative:
            xyRGB = 1 - xyRGB
        if self.utilityInvertColorMap:
            xyRGB = mpl.colors.rgb_to_hsv(xyRGB)
            xyRGB[:, :, 0] -= 0.5
            xyRGB[xyRGB < 0] += 1
            xyRGB = mpl.colors.hsv_to_rgb(xyRGB)
        xyRGB[xyRGB < 0] = 0
        xyRGB[xyRGB > 1] = 1
# #test:
#        xyRGB[:,:,:]=0
#        xyRGB[1::2,1::2,0]=1
        extent = None
        if (self.xaxis.limits is not None) and (self.yaxis.limits is not None):
            if (not isinstance(self.xaxis.limits, str)) and\
               (not isinstance(self.yaxis.limits, str)):
                extent = [self.xaxis.limits[0], self.xaxis.limits[1],
                          self.yaxis.limits[0], self.yaxis.limits[1]]
        self.ax2dHist.images[0].set_data(xyRGB)
        if extent is not None:
            self.ax2dHist.images[0].set_extent(extent)

        if self.xaxis.invertAxis:
            self.ax2dHist.set_xlim(self.ax2dHist.get_xlim()[::-1])
        if self.yaxis.invertAxis:
            self.ax2dHist.set_ylim(self.ax2dHist.get_ylim()[::-1])

        if self.contourLevels is not None:
            if self.contours2D is not None:
                for c in self.contours2D.collections:
                    try:
                        self.ax2dHist.collections.remove(c)
                    except ValueError:
                        pass
                self.ax2dHist.artists = []
            dx = float(self.xaxis.limits[1]-self.xaxis.limits[0]) /\
                self.xaxis.bins
            dy = float(self.yaxis.limits[1]-self.yaxis.limits[0]) /\
                self.yaxis.bins
            if dx == 0:
                dx = 1.
            if dy == 0:
                dy = 1.
            x = np.linspace(
                self.xaxis.limits[0] + dx/2, self.xaxis.limits[1] - dx/2,
                self.xaxis.bins)
            y = np.linspace(
                self.yaxis.limits[0] + dy/2, self.yaxis.limits[1] - dy/2,
                self.yaxis.bins)
            X, Y = np.meshgrid(x, y)
            norm = self.nRaysAll * dx * dy
            if norm > 0:
                Z = copy.copy(self.total2D) / norm
                Z = sp.ndimage.filters.gaussian_filter(Z, 3, mode='nearest')\
                    * self.contourFactor
                self.contourMax = np.max(Z)
                if True:  # self.contourMax > 1e-4:
                    contourLevels =\
                        [l*self.contourMax for l in self.contourLevels]
                    self.contours2D = self.ax2dHist.contour(
                        X, Y, Z, levels=contourLevels,
                        colors=self.contourColors)
                    self.ax2dHist.clabel(
                        self.contours2D, fmt=self.contourFmt, inline=True,
                        fontsize=10)

    def textFWHM(self, axis, textD, average, hwhm):
        """Updates the text field that has average of the *axis* plus-minus the
        HWHM value."""
        deltaStr = axis.label + '$ = $' + axis.fwhmFormatStr +\
            r'$\pm$' + axis.fwhmFormatStr + ' %s'
        textD.set_text(deltaStr % (average, hwhm, axis.unit))

    def _pow10(self, x, digits=1):
        """
        Returns a string representation of the scientific notation of the given
        number formatted for use with LaTeX or Mathtext, with specified number
        of significant decimal digits.
        """
        x = float(x)
        if (x <= 0) or np.isnan(x).any():
            return '0'
        exponent = int(np.floor(np.log10(abs(x))))
        coeff = np.round(x / float(10**exponent), digits)
        return r"{0:.{2}f}$\cdot$10$^{{{1:d}}}$".format(
            coeff, exponent, digits)

#    def _round_to_n(self, x, n):
#        """Round x to n significant figures"""
#        return round(x, -int(np.floor(np.sign(x) * np.log10(abs(x)))) + n)
#
#    def _str_fmt10(self, x, n=2):
#        " Format x into nice Latex rounding to n"
#        if x <= 0: return "0"
#        try:
#            power = int(np.log10(self._round_to_n(x, 0)))
#            f_SF = self._round_to_n(x, n) * pow(10, -power)
#        except OverflowError:
#            return "0"
#        return r"{0}$\cdot$10$^{{{1}}}$".format(f_SF, power)

    def plot_plots(self):
        """
        Does all graphics update.
        """
        self.cx, self.dx = self.plot_hist1d('x')
        self.cy, self.dy = self.plot_hist1d('y')

        if self.ePos != 0:
            self.cE, self.dE = self.plot_hist1d('c')
            self.plot_colorbar()
            if self.caxis.fwhmFormatStr is not None:
                self.textFWHM(self.caxis, self.textDE, self.cE, self.dE/2)
        self.plot_hist2d()

        if self.textNrays:
            self.textNrays.set_text(r'$N_{\rm all} = $%s' % self.nRaysAll)
        if self.textGoodrays:
            if (runner.runCardVals.backend == 'shadow'):
                strDict = {0: r'lost', 1: r'good'}
                self.textGoodrays.set_text(
                    ''.join([r'$N_{\rm ', strDict[self.rayFlag[0]],
                            r'} = $%s']) % self.nRaysNeeded)
        if (runner.runCardVals.backend == 'raycing'):
            for iTextPanel, iEnergy, iN, substr in zip(
                [self.textGood, self.textOut, self.textOver, self.textAlive,
                 self.textDead],
                [raycing.hueGood, raycing.hueOut, raycing.hueOver, 0,
                 raycing.hueDead],
                [self.nRaysGood, self.nRaysOut, self.nRaysOver,
                 self.nRaysAlive, self.nRaysDead],
                    ['good', 'out', 'over', 'alive', 'dead']):
                if iTextPanel is not None:
                    iTextPanel.set_text(''.join(
                        [r'$N_{\rm ', substr, r'} = $%s']) % iN)
                    if self.caxis.useCategory:
                        eMin, eMax = self.caxis.limits
                        if iEnergy == 0:
                            color = 'black'
                        else:
                            hue = (iEnergy-eMin) / (eMax-eMin) * colorFactor
#                            hue = iEnergy / 10.0 * colorFactor
                            color = np.dstack((hue, 1, 1))
                            color = \
                                mpl.colors.hsv_to_rgb(color)[0, :].reshape(3, )
                        iTextPanel.set_color(color)
            if self.textI:
                isPowerOfTen = False
                if self.fluxFormatStr.endswith('p'):
                    pos = self.fluxFormatStr.find('.')
                    if 0 < pos+1 < len(self.fluxFormatStr):
                        isPowerOfTen = True
                        powerOfTenDecN = int(self.fluxFormatStr[pos+1])
                if (self.fluxUnit is None) or (self.nRaysSeeded == 0):
                    intensityStr = r'$\Phi = $'
                    if isPowerOfTen:
                        intensityStr += self._pow10(
                            self.intensity, powerOfTenDecN)
                    else:
                        intensityStr += self.fluxFormatStr % self.intensity
                    self.textI.set_text(intensityStr)
                else:
                    if self.fluxKind.startswith('power'):
                        if self.nRaysAll > 0:
                            self.power = self.intensity / self.nRaysAll
                            if self.displayAsAbsorbedPower:
                                powerStr2 = r'P$_{\rm abs} = $'
                            else:
                                powerStr2 = r'P$_{\rm tot} = $'
                            powerStr = powerStr2 + self.fluxFormatStr + ' W'
                            self.textI.set_text(powerStr % self.power)
                    else:
                        if (self.nRaysAll > 0) and (self.nRaysSeeded > 0):
#                            self.flux = self.intensity / self.nRaysAll *\
#                                self.nRaysAccepted / self.nRaysSeeded
                            self.flux = self.intensity / self.nRaysAll *\
                                self.nRaysSeededI / self.nRaysSeeded
                            if isPowerOfTen:
                                intensityStr = self._pow10(
                                    self.flux, powerOfTenDecN)
                            else:
                                intensityStr = self.fluxFormatStr % self.flux
                            intensityStr = \
                                r'$\Phi = ${0} ph/s'.format(intensityStr)
                            self.textI.set_text(intensityStr)
            self.update_user_elements()
        if (runner.runCardVals.backend == 'shadow'):
            if self.textI:
                intensityStr = r'$I = $' + self.fluxFormatStr
                self.textI.set_text(intensityStr % self.intensity)

        if self.xaxis.fwhmFormatStr is not None:
            self.textFWHM(self.xaxis, self.textDx, self.cx, self.dx/2)
        if self.yaxis.fwhmFormatStr is not None:
            self.textFWHM(self.yaxis, self.textDy, self.cy, self.dy/2)

        self.fig.canvas.draw()

    def save(self, suffix=''):
        """
        Saves matplotlib figures with the *suffix* appended to the file name(s)
        in front of the extension.
        """
        if self.saveName is None:
            return
        if isinstance(self.saveName, basestring):
            fileList = [self.saveName, ]
        else:  # fileList is a sequence
            fileList = self.saveName
        for aName in fileList:
            (fileBaseName, fileExtension) = os.path.splitext(aName)
            saveName = ''.join([fileBaseName, suffix, fileExtension])
            self.fig.savefig(saveName, dpi=self.dpi)

    def clean_plots(self):
        """
        Cleans the graph in order to prepare it for the next ray tracing.
        """
        runner.runCardVals.iteration = 0
        runner.runCardVals.stop_event.clear()
        runner.runCardVals.finished_event.clear()
        for axis in [self.xaxis, self.yaxis, self.caxis]:
            axis.total1D = np.zeros(axis.bins)
            axis.total1D_RGB = np.zeros((axis.bins, 3))
        self.total2D = np.zeros((self.yaxis.bins, self.xaxis.bins))
        self.total2D_RGB = np.zeros((self.yaxis.bins, self.xaxis.bins, 3))

        try:
            self.fig.canvas.window().setWindowTitle(self.title)
        except AttributeError:
            pass
        self.nRaysAll = 0
        self.nRaysAllRestored = -1
        self.intensity = 0
        self.cidp = self.fig.canvas.mpl_connect(
            'button_press_event', self.on_press)
        self.fig.canvas.draw()
        if self.ePos != 0:
            if self.caxis.fwhmFormatStr is not None:
                self.textDE.set_text('')
        self.textNrays.set_text('')
        if self.backend == 'shadow':
            self.nRaysNeeded = long(0)
            if self.textGoodrays is not None:
                self.textGoodrays.set_text('')
        if self.backend == 'raycing':
            self.nRaysAlive = long(0)
            self.nRaysGood = long(0)
            self.nRaysOut = long(0)
            self.nRaysOver = long(0)
            self.nRaysDead = long(0)
            if self.textGood is not None:
                self.textGood.set_text('')
            if self.textOut is not None:
                self.textOut.set_text('')
            if self.textOver is not None:
                self.textOver.set_text('')
            if self.textAlive is not None:
                self.textAlive.set_text('')
            if self.textDead is not None:
                self.textDead.set_text('')
        if self.textI:
            self.textI.set_text('')
        if self.xaxis.fwhmFormatStr is not None:
            self.textDx.set_text('')
        if self.yaxis.fwhmFormatStr is not None:
            self.textDy.set_text('')
        self.clean_user_elements()
        if self.contours2D is not None:
            self.contours2D.collections = []
            self.ax2dHist.collections = []

        self.plot_plots()

    def set_negative(self):
        """
        Utility function. Makes all plots in the graph negative (in color).
        """
        self.negative = not self.negative
        if self.negative:
            axisbg = 'w'
        else:
            axisbg = 'k'
        axesList = [self.ax2dHist, self.ax1dHistX, self.ax1dHistY]
        if self.ePos != 0:
            axesList.append(self.ax1dHistE)
            axesList.append(self.ax1dHistEbar)
        for axes in axesList:
            axes.set_axis_bgcolor(axisbg)
        self.plot_plots()

    def set_invert_colors(self):
        """
        Utility function. Inverts the color map.
        """
        self.invertColorMap = not self.invertColorMap  # this variable is used
        # at the time of handling the ray-tracing arrays, as it is cheaper
        # there but needs an additional inversion at the time of plotting if
        # requested by user.
        self.utilityInvertColorMap = not self.utilityInvertColorMap  # this
        # variable is used at the time of plotting
        self.plot_plots()

    def card_copy(self):
        """
        Returns a minimum set of properties (a "card") describing the plot.
        Used for passing it to a new process or thread.
        """
        return PlotCard2Pickle(self)

    def store_plots(self):
        """
        Pickles the accumulated arrays (histograms) and values (like flux) into
        the binary file *persistentName*.
        """
        saved = SaveResults(self)
        if runner.runCardVals.globalNorm:
            runner.runCardVals.savedResults.append(saved)
        if self.persistentName and (self.nRaysAll > self.nRaysAllRestored):
            if self.persistentName.endswith('mat'):
                import scipy.io as io
                #if os.path.isfile(self.persistentName):
                #    os.remove(self.persistentName)
                io.savemat(self.persistentName, vars(saved))
            else:
                f = open(self.persistentName, 'wb')
                pickle.dump(saved, f, -1)
                f.close()

    def restore_plots(self):
        """
        Restores itself from a file, if possible.
        """
        try:
            if self.persistentName:
                if self.persistentName.endswith('mat'):
                    import scipy.io as io
                    saved_dic = {}
                    io.loadmat(self.persistentName, saved_dic)
                    saved = SaveResults(self)
                    saved.__dict__.update(saved_dic)
                else:
                    pickleFile = open(self.persistentName, 'rb')
                    saved = pickle.load(pickleFile)
                    pickleFile.close()
                saved.restore(self)
            if True:  # _DEBUG:
                print 'persistentName=', self.persistentName
                print 'saved nRaysAll=', self.nRaysAll
        except IOError:
            pass


class XYCPlotWithNumerOfReflections(XYCPlot):
    def update_user_elements(self):
        if not hasattr(self, 'ax1dHistE'):
            return
        if not hasattr(self, 'textUser'):
            self.textUser = []
        else:
            self.ax1dHistE.texts[:] = [t for t in self.ax1dHistE.texts
                                       if t not in self.textUser]
            del self.textUser[:]
        bins = self.caxis.total1D.nonzero()[0]
        self.ax1dHistE.yaxis.set_major_locator(MaxNLocator(integer=True))
        yPrev = -1e3
        fontSize = 8
        for i, b in enumerate(bins):
            binVal = int(round(abs(
                self.caxis.binEdges[b]+self.caxis.binEdges[b+1]) / 2))
            textOut = ' n({0:.0f})={1:.1%}'.format(
                binVal, self.caxis.total1D[b] / self.intensity)
            y = self.caxis.binEdges[b+1] if i < (len(bins)-1) else\
                self.caxis.binEdges[b]
            tr = self.ax1dHistE.transData.transform
            if abs(tr((0, y))[1] - tr((0, yPrev))[1]) < fontSize:
                continue
            yPrev = y
            color = self.caxis.total1D_RGB[b] / max(self.caxis.total1D_RGB[b])
#            va = 'bottom' if binVal < self.caxis.limits[1] else 'top'
            va = 'bottom' if i < (len(bins) - 1) else 'top'
            myText = self.ax1dHistE.text(
                0, y, textOut, ha='left', va=va, size=fontSize, color=color)
            self.textUser.append(myText)

    def clean_user_elements(self):
        if hasattr(self, 'textUser'):
            self.ax1dHistE.texts[:] = [t for t in self.ax1dHistE.texts
                                       if t not in self.textUser]
            del self.textUser[:]


class PlotCard2Pickle(object):
    """
    Container for a minimum set of properties (a "card") describing the plot.
    Used for passing it to a new process or thread. Must be pickleable.
    """
    def __init__(self, plot):
        self.xaxis = plot.xaxis
        self.yaxis = plot.yaxis
        self.caxis = plot.caxis
        self.aspect = plot.aspect
        self.beam = plot.beam
        self.beamState = plot.beamState
        self.beamC = plot.beamC
        self.rayFlag = plot.rayFlag
        self.invertColorMap = plot.invertColorMap
        self.ePos = plot.ePos
        self.colorFactor = colorFactor
        self.colorSaturation = colorSaturation
        self.fluxKind = plot.fluxKind


class SaveResults(object):
    """
    Container for the accumulated arrays (histograms) and values (like flux)
    for subsequent pickling/unpickling or for global flux normalization.
    """
    def __init__(self, plot):
        """
        Stores the arrays and values and finds the global histogram maxima.
        """
        self.xtotal1D = copy.copy(plot.xaxis.total1D)
        self.xtotal1D_RGB = copy.copy(plot.xaxis.total1D_RGB)
        self.ytotal1D = copy.copy(plot.yaxis.total1D)
        self.ytotal1D_RGB = copy.copy(plot.yaxis.total1D_RGB)
        self.etotal1D = copy.copy(plot.caxis.total1D)
        self.etotal1D_RGB = copy.copy(plot.caxis.total1D_RGB)
        self.total2D = copy.copy(plot.total2D)
        self.total2D_RGB = copy.copy(plot.total2D_RGB)

        axes = [plot.xaxis, plot.yaxis]
        if plot.ePos:
            axes.append(plot.caxis)
        for axis in axes:
            if axis.globalMax1D < axis.max1D:
                axis.globalMax1D = axis.max1D
            if axis.globalMax1D_RGB < axis.max1D_RGB:
                axis.globalMax1D_RGB = axis.max1D_RGB
        if plot.globalMax2D_RGB < plot.max2D_RGB:
            plot.globalMax2D_RGB = plot.max2D_RGB
        self.nRaysAll = copy.copy(plot.nRaysAll)
        self.intensity = copy.copy(plot.intensity)
        if plot.backend == 'shadow':
            self.nRaysNeeded = copy.copy(plot.nRaysNeeded)
        elif plot.backend == 'raycing':
            self.nRaysAlive = copy.copy(plot.nRaysAlive)
            self.nRaysGood = copy.copy(plot.nRaysGood)
            self.nRaysOut = copy.copy(plot.nRaysOut)
            self.nRaysOver = copy.copy(plot.nRaysOver)
            self.nRaysDead = copy.copy(plot.nRaysDead)
            if (plot.nRaysSeeded > 0):
                self.nRaysAccepted = copy.copy(plot.nRaysAccepted)
                self.nRaysAcceptedE = copy.copy(plot.nRaysAcceptedE)
                self.nRaysSeeded = copy.copy(plot.nRaysSeeded)
                self.nRaysSeededI = copy.copy(plot.nRaysSeededI)

        self.xlimits = plot.xaxis.limits
        self.ylimits = plot.yaxis.limits
        self.elimits = plot.caxis.limits
        self.xbinEdges = plot.xaxis.binEdges
        self.ybinEdges = plot.yaxis.binEdges
        self.ebinEdges = plot.caxis.binEdges
        self.fluxKind = plot.fluxKind

    def restore(self, plot):
        """
        Restores the arrays and values after unpickling or after running the
        ray-tracing series and finding the global histogram maxima.
        """
        plot.xaxis.total1D = np.copy(np.squeeze(self.xtotal1D))
        plot.xaxis.total1D_RGB = np.copy(np.squeeze(self.xtotal1D_RGB))
        plot.yaxis.total1D = np.copy(np.squeeze(self.ytotal1D))
        plot.yaxis.total1D_RGB = np.copy(np.squeeze(self.ytotal1D_RGB))
        plot.caxis.total1D = np.copy(np.squeeze(self.etotal1D))
        plot.caxis.total1D_RGB = np.copy(np.squeeze(self.etotal1D_RGB))
        plot.total2D = np.copy(np.squeeze(self.total2D))
        plot.total2D_RGB = np.copy(np.squeeze(self.total2D_RGB))

        plot.nRaysAll = np.copy(np.squeeze(self.nRaysAll))
        plot.nRaysAllRestored = np.copy(np.squeeze(self.nRaysAll))
        plot.intensity = np.copy(np.squeeze(self.intensity))
        if plot.backend == 'shadow':
            plot.nRaysNeeded = np.copy(np.squeeze(self.nRaysNeeded))
        elif plot.backend == 'raycing':
            plot.nRaysAlive = np.copy(np.squeeze(self.nRaysAlive))
            plot.nRaysGood = np.copy(np.squeeze(self.nRaysGood))
            plot.nRaysOut = np.copy(np.squeeze(self.nRaysOut))
            plot.nRaysOver = np.copy(np.squeeze(self.nRaysOver))
            plot.nRaysDead = np.copy(np.squeeze(self.nRaysDead))
            if hasattr(self, 'nRaysSeeded'):
                if (self.nRaysSeeded > 0):
                    plot.nRaysAccepted =\
                        np.copy(np.squeeze(self.nRaysAccepted))
                    plot.nRaysAcceptedE =\
                        np.copy(np.squeeze(self.nRaysAcceptedE))
                    plot.nRaysSeeded = np.copy(np.squeeze(self.nRaysSeeded))
                    plot.nRaysSeededI = np.copy(np.squeeze(self.nRaysSeededI))

        plot.xaxis.limits = np.copy(np.squeeze(self.xlimits))
        plot.yaxis.limits = np.copy(np.squeeze(self.ylimits))
        plot.caxis.limits = np.copy(np.squeeze(self.elimits))
        plot.xaxis.binEdges = np.copy(np.squeeze(self.xbinEdges))
        plot.yaxis.binEdges = np.copy(np.squeeze(self.ybinEdges))
        plot.caxis.binEdges = np.copy(np.squeeze(self.ebinEdges))
        plot.fluxKind = np.array_str(np.copy(np.squeeze(self.fluxKind)))


#    def __getstate__(self):
#        odict = self.__dict__.copy() # copy the dict since we change it
#        del odict['plot']  # remove plot reference, it cannot be pickled
#        return odict
