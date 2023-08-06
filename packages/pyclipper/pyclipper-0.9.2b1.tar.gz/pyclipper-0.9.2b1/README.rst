About
=====

Pyclipper is a Cython wrapper exposing public functions and classes of
the C++ translation of the `Angus Johnson's Clipper library (ver.
6.2.1) <http://www.angusj.com/delphi/clipper.php>`__.

Pyclipper releases were tested with Python 2.7 and 3.4 on Linux (Ubuntu
14.04, x64) and Windows (8.1, x64).

Source code is available on
`GitHub <https://github.com/greginvm/pyclipper>`__.

About Clipper
-------------

        Clipper - an open source freeware library for clipping and
        offsetting lines and polygons.

        The Clipper library performs line & polygon clipping -
        intersection, union, difference & exclusive-or, and line &
        polygon offsetting. The library is based on Vatti's clipping
        algorithm.

        \ `Angus Johnson's Clipper
        library <http://www.angusj.com/delphi/clipper.php>`__\ 

Install
=======

Dependencies
------------

Cython dependency is optional. Cpp sources generated with Cython are
available in releases.

Note on using the ``setup.py``:

``setup.py`` operates in 2 modes that are based on the presence of the
``dev`` file in the root of the project.

-  When ``dev`` is present, Cython will be used to compile the ``.pyx``
   sources. This is the *development mode* (as you get it in the git
   repository).
-  When ``dev`` is absent, C/C++ compiler will be used to compile the
   ``.cpp`` sources (that were prepared in in the development mode).
   This is the distribution mode (as you get it on PyPI).

This way the package can be used without or with an incompatible version
of Cython.

The idea comes from `Matt Shannon's bandmat
library <https://github.com/MattShannon/bandmat>`__.

From PyPI
---------

Cython not required.

::

        pip install pyclipper
        

From source
-----------

Cython required.

Clone the repository:

::

        git clone git@github.com:greginvm/pyclipper.git
        

Install:

::

        python setup.py install
        

After every modification of ``.pyx`` files compile with Cython:

::

        python setup.py build_ext --inplace
        

Clippers' preprocessor directives
---------------------------------
Clipper can be compiled with the following preprocessor directives: ``use_int32``, ``use_xyz``, ``use_lines`` and ``use_deprecated``. 
Among these the ``use_int32`` and ``use_lines`` can be used with Pyclipper.

-  ``use_int32`` - when enabled 32bit ints are used instead of 64bit ints. This improve performance but coordinate values are limited to the range +/- 46340. In Pyclipper this directive is **disabled** by default.

-  ``use_lines`` - enables line clipping. Adds a very minor cost to performance. In Pyclipper this directive is **enabled** by default (since version 0.9.2b0).

In case you would want to change these settings, clone this repository and change the ``define_macros`` collection (``setup.py``, pyclipper extension definition). Add a set like ``('use_int32', 1)`` to enable the directive, or remove the set to disable it. After that you need to rebuild the package.

How to use
==========

This wrapper library tries to follow naming conventions of the original
library.

-  ``ClipperLib`` namespace is represented by the ``pyclipper`` module,
-  classes ``Clipper`` and ``ClipperOffset`` -> ``Pyclipper`` and
   ``Pyclipper`` and ``PyclipperOffset``,
-  when Clipper is overloading functions with different number of
   parameters or different types (eg. ``Clipper.Execute``, one function
   fills a list of paths the other PolyTree) that becomes
   ``Pyclipper.Execute`` and ``Pyclipper.Execute2``.

Basic example (based on `Angus Johnson's Clipper
library <http://www.angusj.com/delphi/clipper.php>`__):

.. code:: python

    import pyclipper

    subj = (
        ((180, 200), (260, 200), (260, 150), (180, 150)),
        ((215, 160), (230, 190), (200, 190))
    )
    clip = ((190, 210), (240, 210), (240, 130), (190, 130))

    pc = pyclipper.Pyclipper()
    pc.AddPath(clip, pyclipper.PT_CLIP, True)
    pc.AddPaths(subj, pyclipper.PT_SUBJ, True)

    solution = pc.Execute(pyclipper.CT_INTERSECTION, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD) 

The Clipper library uses integers instead of floating point values to
preserve numerical robustness. You can use ``pyclipper.SCALING_FACTOR``
to scale your values to preserve the desired presision. The default
value is 1, which disables scaling. This setting only scales coordinates
of polygon vertices, properties like ``miterLimit``, ``roundPrecision``
etc. are not scaled.

For more examples of use see ``tests/test_pyclipper.py`` and
`Clipper
documentation <http://www.angusj.com/delphi/clipper/documentation/Docs/_Body.htm>`__.

Authors
=======

-  The Clipper library is written by `Angus
   Johnson <http://www.angusj.com/delphi/clipper.php>`__,
-  This wrapper was initially written by `Maxime
   Chalton <https://sites.google.com/site/maxelsbackyard/home/pyclipper>`__,
-  Adaptions to make it work with version 5 written by `Lukas
   Treyer <http://www.lukastreyer.com>`__,
-  Adaptions to make it work with version 6.2.1 and PyPI package written
   by `Gregor Ratajc <http://www.gregorratajc.com>`__.

License
=======

-  Pyclipper is available under `MIT
   license <http://opensource.org/licenses/MIT>`__.
-  The core Clipper library is available under `Boost Software
   License <http://www.boost.org/LICENSE_1_0.txt>`__. Freeware for both
   open source and commercial applications.

Changelog
=========

0.9.2b1
-------
-  bug fix: Fix setting of the PyPolyNode.IsHole property

0.9.2b0
-------
-  enable preprocessor directive ``use_lines`` by default,
-  bug fix: PyPolyNode.Contour that is now one path and not a list of paths as it was previously.