.. vim: set fileencoding=utf-8 :
.. Andre Anjos <andre.dos.anjos@gmail.com>
.. Tue 15 Oct 17:41:52 2013

.. testsetup:: *

   import numpy

============
 User Guide
============

By importing this package, you can use |project| native array reading (:py:func:`bob.io.base.load`) and
writing (:py:func:`bob.io.base.save`) routines to load and save files using the Matlab(R) ``.mat`` format.

.. doctest::
   :options: +NORMALIZE_WHITESPACE, +ELLIPSIS

   >>> import bob.io.base
   >>> import bob.io.matlab #under the hood: loads Bob plugin for '.mat' files
   >>> x = bob.io.base.load('myfile.mat') # doctest: +SKIP

This package also contains a couple of other methods that allow for reading
variable names and matrices from ``.mat`` files. Proceed to the
:doc:`py_api` section for details.

Be Portable
-----------

An alternative for saving data in ``.mat`` files using
:py:func:`bob.io.base.save`, would be to save them as `HDF5`_ files which then
can be easily read inside Matlab. The `HDF5`_ format is well supported in
Matlab(R) - as a matter of fact, the newest version of `.mat` files **uses**
the HDF5 format.

Similarly, instead of having to read ``.mat`` files using
:py:func:`bob.io.base.load`, you can save your Matlab data in `HDF5`_ format,
which then can be easily read from |project|, without this add-on. Detailed
instructions about how to save and load data from Matlab to and from `HDF5`_
files can be found `here`__.

.. Place here your external references
.. include:: links.rst
.. _matlab-hdf5: http://www.mathworks.ch/help/techdoc/ref/hdf5write.html
__ matlab-hdf5_
