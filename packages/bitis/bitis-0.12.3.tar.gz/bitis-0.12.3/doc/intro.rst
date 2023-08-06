
.. role:: red

.. raw:: html

    <style> .red {color: red; font-weight: bold} </style>



==============================================
Bitis, binary timed signals processing library
==============================================

Introduction
============

**Bitis** is a python module that implements a full set of operators over
binary signals represented with BTS format. The `BTS format <./btsformat.html>`_
is a computer memory representation of a binary signal that can have a very
compact memory footprint when the signal has a low rate of change with respect
to its sampling period.

For example, let see a typical case, a time reference signal having about
one pulse per second and one microsecond of time resolution. The BTS
format allows to completely discard the one million samples per second
between each two pulses and allows to keep in memory only the signal change
times: for each second, the time of the pulse front edge and the time of the
trailing edge.

This is the documentation for version |version|.

Since version 0.9.0, the `BTS format <./btsformat.html>`_ :red:`has changed`. The
start and the end times of the signal are no more in the signal changes times
sequence. Now, they are attributes of the signal object (Signal.start,
Signal.end).` 

At present, no effort is made for speed optimization and the employed
algorithms are essentially procedural. The only goal is "make it work in
some way" and understand what can be a decent set of objects/methods/functions.

BITIS is released under the GNU General Public License.

At present, version |version|, BITIS is in alpha status. Any debugging aid is
welcome.

For any question, suggestion, contribution contact the author Fabrizio Pollastri <f.pollastri_a_t_inrim.it>.


Requirements
============

To run the code, **Python 2.6 or later** must
already be installed.  The latest release is recommended.  Python is
available from http://www.python.org/.

When the Signal plotting method is used also `Matplotlib`_ is required.
This also requires all dependencies of `Matplotlib`_, like `NumPy`_, etc.


Installation
============

1. Open a shell.

2. Get root privileges and install the package. Command::

    pip install bitis


Code Repository
===============

There is also a code repository at `https://github.com/fabriziop/bitis`_ .


.. _Matplotlib: http://matplotlib.org
.. _NumPy: http://numpy.org
.. _https://github.com/fabriziop/bitis: https://github.com/fabriziop/bitis
