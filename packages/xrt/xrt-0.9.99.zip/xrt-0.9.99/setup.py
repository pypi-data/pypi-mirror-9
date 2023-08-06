from distutils.core import setup

#import importLongDescription
#long_description = importLongDescription.output()
long_description = """
Package xrt (XRayTracer) is a python software library for ray tracing and
wave propagation in x-ray regime. It is primarily meant for modeling
synchrotron sources, beamlines and beamline elements.

Features of xrt
---------------

* *Publication quality graphics*. 1D and 2D position histograms are
  *simultaneously* coded by hue and brightness. Typically, colors represent
  energy and brightness represents beam intensity. The user may select other
  quantities to be encoded by colors: angular and positional distributions,
  various polarization properties, beam categories, number of reflections,
  incidence angle etc. Brightness can also encode partial flux for a selected
  polarization and incident or absorbed power. Publication quality plots are
  provided by `matplotlib` with image formats PNG, PostScript, PDF, SVG.

* *Rays and waves*. Classical ray tracing and wave propagation via Kirchhoff
  integral.

* *Unlimited number of rays*. The colored histograms are *cumulative*. The
  accumulation can be stopped and resumed.

* *Parallel execution*. xrt can be run in parallel in several threads or
  processes (can be opted), which accelerates the execution on multi-core
  computers. It can run on an external server (supercomputer), also without
  X window system (X11) support.

* *Scripting in Python*. xrt can be run within Python scripts to generate a
  series of images under changing geometrical or physical parameters. The image
  brightness and 1D histograms can be normalized to the global maximum
  throughout the series.

* *Sources*. xrt can have several light sources. For example, an ID beamline
  has 3 sources: one ID and two BM. This feature allows exploring the influence
  of out-of-focus sources.

* *Synchrotron sources*. Bending magnet, wiggler, undulator and elliptic
  undulator are calculated internally within xrt. There is also a legacy
  approach to sampling synchrotron sources using the codes `ws` and `urgent`
  which are parts of XOP package. Please look the section
  `comparison-synchrotron-sources` for the comparison between the
  implementations. If the photon source is one of the synchrotron sources, the
  total flux in the beam is reported not just in number of rays but in physical
  units of ph/s. The total power or absorbed power can be opted instead of flux
  and is reported in W. The power density can be visualized by isolines. The
  magnetic gap of undulators can be tapered. Undulators can be calculated in
  near field. Undulators can be calculated on GPU, with a high gain in
  computation speed, which is important for tapering and near field
  calculations.

* *Shapes*. There are several predefined shapes of optical elements implemented
  as python classes. The inheritance mechanism simplifies creation of other
  shapes. The user specifies methods for the surface and the surface normal.
  For asymmetric crystals, the normal to the atomic planes can be additionally
  given. The surface and the normals are defined either in local (x, y)
  coordinates or in user-defined parametric coordinates. Parametric
  representation enables closed shapes like capillaries. It also enables exact
  solutions for complex shapes (e.g. a logarithmic spiral) without any
  expansion. The methods of finding the intersections of rays with the surface
  are very robust and can cope with pathological cases as sharp surface kinks.
  Notice that the search for intersection points does not involve any
  approximation and has only numerical inaccuracy which is set by default as
  1 fm. Any surface can be combined with a (differently and variably oriented)
  crystal structure and/or (variable) grating vector. Surfaces can be faceted.

* *Energy dispersive elements*. Implemented are crystals in dynamical
  diffraction, gratings (also with efficiency calculations), Fresnel zone
  plates, Bragg-Fresnel optics and multilayers in dynamical diffraction.
  Crystals can work in Bragg or Laue cases, in reflection or in transmission.
  The two-field polarization phenomena are fully preserved, also within the
  Darwin   diffraction plateau, thus enabling the ray tracing of crystal-based
  phase retarders.

* *Materials*. The material properties are incorporated using three different
  tabulations of the scattering factors, with differently wide and differently
  dense energy meshes. Refraction index and absorption coefficient are
  calculated from the scattering factors. Two-surface bodies, like plates or
  refractive lenses, are treated with both refraction and absorption.

* *Multiple reflections*. xrt can trace multiple reflections in a single
  optical element. This is useful, for example in 'whispering gallery' optics
  or in Montel or Wolter mirrors. Here, very handy is the histogramming over
  the number of reflections, incidence angle and elevation over the surface.

* *Non-sequential optics*. xrt can trace non-sequential optics where different
  parts of the incoming beam meet different surfaces. Examples of such optics
  are poly-capillaries and Wolter mirrors.

* *Global coordinate system*. The optical elements are positioned in a global
  coordinate system. This is convenient for modeling a real synchrotron
  beamline. The coordinates in this system can be directly taken from a CAD
  library. The optical surfaces are defined in local systems for the user's
  convenience.

* *Beam categories*. xrt discriminates rays by several categories: `good`,
  `out`, `over` and `dead`. This distinction simplifies the adjustment of
  entrance and exit slits. An alarm is triggered if the fraction of dead rays
  exceeds a specified level.

* *Portability*. xrt runs on Windows and Unix-like platforms, wherever you can
  run python.

* *Examples*. xrt comes with many examples; see the galleries.

Dependencies
------------
numpy, scipy and matplotlib are required. If you use OpenCL for calculations on
GPU or CPU, you need AMD/NVIDIA drivers, ``Intel CPU only OpenCL runtime``
(these are search key words), pytools and pyopencl.

Python 3
--------
The code can be fully automatically converted to Python 3 with ``2to3`` at its
default options."""

setup(name='xrt',
      version='0.9.99',
      description='Ray tracing and wave propagation in x-ray regime, '
                  'primarily meant for modeling '
                  'synchrotron beamlines and beamline elements',
      long_description=long_description,
      author=('Konstantin Klementiev', 'Roman Chernikov'),
      author_email='first DOT last AT gmail DOT com',
      url='http://pythonhosted.org/xrt',
      platforms='OS Independent',
      license='MIT License',
      packages=['xrt', 'xrt.backends', 'xrt.backends.raycing'],
      package_data={'xrt.backends.raycing': ['data/*.*', '*.cl'],
                    'xrt': ['*.cl']},
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Intended Audience :: Science/Research',
                   'Natural Language :: English',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python :: 2',
                   'Programming Language :: Python :: 3',
                   'License :: OSI Approved :: MIT License',
                   'Topic :: Scientific/Engineering :: Physics',
                   'Topic :: Scientific/Engineering :: Visualization'],
      )
