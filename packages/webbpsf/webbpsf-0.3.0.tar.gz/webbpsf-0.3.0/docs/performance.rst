.. _performance_and_parallelization:

Optimizing Performance and Parallelization
=========================================

Performance optimization on modern multi-core machines is a complex subject. 

WebbPSF can parallelize calculations in two different ways:

  1. Using Python's built-in ``multiprocessing`` package to launch many additional Python
     processes, each of which calculates a different wavelength.
  2. Using the FFTW library for optimized accellerated Fourier transform calculations.
     FFTW is capable of sharing load across multiple processes via multiple threads. 

One might think that using both of these together would result in the fastest possible speeds. 
However, in testing it appears that FFTW does not work reliably with multiprocessing for some
unknown reason; this instability manifests itself as occasional fatal crashes of the Python process.
For this reason it is recommended that one use *either multiprocessing or FFTW, but not both*.

**For most users, the recommended choice is using multiprocessing**.

FFTW only helps for FFT-based calculations, such as some coronagraphic or spectroscopic calculations.
Calculations that use only discrete matrix Fourier transforms are not helped by FFTW. 
Furthermore, baseline testing indicates that in many cases, just running multiple Python processes is in fact
significantly faster than using FFTW, even for coronagraphic calculations using FFTs. 

There is one significant tradeoff in using multiprocessing: When running in this mode, WebbPSF cannot display plots of the 
calculation's work in progress, for instance the intermediate optical planes. (This is because the background Python processes can't
write to any Matplotlib display windows owned by the foreground process). For interactive use, it can be useful to turn the parallelization
off and just run sequential calculations, then switch to parallelized calculations for batch computations where you just want to see the final results
saved as FITS files. 

The configuration options to enable multiprocessing live in :py:mod:`poppy`, the underlying library that performs the computation. Enable them as follows::

   >>> import poppy
   >>> poppy.conf.use_multiprocessing = True
   >>> poppy.conf.use_fftw = False

One caveat with running multiple processes is that the memory demands can become substantial for large oversampling factors.  For instance, a 1024-pixel-across pupil with ``oversampling=4`` results in arrays that are 256 MB each. Several such arrays are needed in memory per calculation, with peak memory utilization reaching ~ 1 GB per process for ``oversampling=4`` and over 4 GB per process for ``oversamping=8``.

Thus, if running on a 16-core computer, ensure at least 32 GB of RAM are available before using one process per core. If you are constrained by the amount of RAM available, you may experience better performance using fewer processes than the number of processor cores in your computer.

By default, WebbPSF attempts to automatically choose a number of processes based on available CPUs and free memory that will optimize computation speed without exhausting available RAM. This is implemented in the function :py:func:`poppy.utils.estimate_optimal_nprocesses`.

If desired, the number of processes can be explicitly specified::

  >>> poppy.conf.n_processes = 5

Set this to zero to enable automatic selection via the :py:func:`~poppy.utils.estimate_optimal_nprocesses` function.

Types of Fourier Transform Calculation in WebbPSF
-------------------------------------------------

  * Any direct imaging calculation, any instrument: Matrix DFT
  * NIRCam coronagraphy with circular occulters: Semi-Analytic Fast Coronagraphy and Matrix DFT
  * NIRCam coronagraphy with wedge occulters: FFT and Matrix DFT
  * MIRI Coronagraphy: FFT and Matrix DFT
  * NIRISS NRM, GR799XD: Matrix DFT
  * NIRSpec and NIRISS slit spectroscopy: FFT and Matrix DFT

Comparison of Different Parallelization Methods
------------------------------------------------

The following figure shows the comparison of single-process, single-process with FFTW, and multi-process calculations on a relatively high end 16-core Mac Pro. 
The horizontal axis shows increasing detail of calculation via higher oversampling, while the vertical axis shows computation time. Note the very different
Y-axis scales for the two figures; coronagraphic calculations take much longer than direct imaging!

.. image:: ./fig_parallel_performance_16coreMacPro.png
   :scale: 100%
   :align: center
   :alt: Graphs of performance with different parallelization options

Using multiple Python processes is the clear winner for most workloads. Explore the options to find what works best for your particular calculations and computer setup.