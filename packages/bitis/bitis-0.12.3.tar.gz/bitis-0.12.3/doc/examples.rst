==============
Usage examples
==============

Logic operations
----------------

This simple example shows some logic operations supported by the **BITIS**
module.

.. literalinclude:: ../examples/xor_logic.py
    :linenos:
    :language: python
    :lines: 30-

Graphic and semigraphic plot
----------------------------

The following example shows the plotting capabilitites of methods *plot* and
*plotchar*. The method *plot* uses the matplotlib to produce graphic drawing
of the given signal as a square/rectangular wave. The x axis represents the
time, the y axis represents the logical levels. The method *plotchar* uses
the box line drawing characters from unicode for drawing the best approximation
of a graphic representation of the given signal.
Below there are two representations of the same test signal.

.. literalinclude:: ../examples/plot.py
    :linenos:
    :language: python
    :lines: 30-

This is the graphic plotting result using *plot* method.

.. image:: ../examples/plot.png

This is the semigraphic plotting result using *plotchar* method. 
The figure shows a sequence of plotting of the same test signal with increasing
resolution. Resolution is the length of the plotting character string, it is
printed at line beginning and spans from only one chararacter until a string 76 
characters long.

.. literalinclude:: ../examples/plot.txt
    :linenos:

When resolution is too low to represent all signal transition edges, *plotchar*
puts an heavy vertical line as symbol of multiple edges.

In this example, *plotchar* is called with the argument max_flat=4 . This means
that a signal constant level elapsing more than 4 characters is compressed
(in time) to be of length 4 characters. This characters drop is marked
by the 'x' chararacter that can be seen in the last four semigraphic plots.
When this happens, it is important to keep in mind that the x axis time scale
is no more uniform.

Correlation Function
--------------------

The following example shows the plotting of two random signals and their
correlation function.

.. literalinclude:: ../examples/correlation.py
    :linenos:
    :language: python
    :lines: 30-

This is the plotting result.

.. image:: ../examples/correlation.png

Serial signal
-------------

The following example shows the signal of an asynchronous serial interface
coding the ASCII character "U" with 8 character bits, odd parity, 2 stop bits
and 50 baud tranmitting speed.

.. literalinclude:: ../examples/serial_tx.py
    :linenos:
    :language: python
    :lines: 30-

This is the plotting result. The x axis units are milliseconds.

.. image:: ../examples/serial_tx.png

Phase lockin
------------

The following example demonstrate a phase recovery from a disturbed periodic
signal whose undisturbed original is known. The original signal is a
square wave of 50 cycles @1Hz, 50 % duty cycle. A gaussian jitter is added
to the original signal change times and the result is xored with noise pulses
to simulate transmission line disturbances.

.. literalinclude:: ../examples/lockin.py
    :linenos:
    :language: python
    :lines: 30-

The plot shows the original, the
disturbed signal and the correlation among them, correlation that reaches a
maximum when the original has that same phase of the disturbed original. 

.. image:: ../examples/lockin.png

Modulation
----------

The following example shows the generation of a modulated signal, given a
random code and a set of symbols. The modulated signal is obtained concatenating
in time the symbol corresponding to a code value.
Then the modulated signal is demodulated by maximal correlation symbol
estimation. As a byproduct, the signal/symbols correlation matrix is obtained
as shown below.
The example does not take into account any signal alteration by noise.

.. literalinclude:: ../examples/modem.py 
    :linenos:
    :language: python
    :lines: 30-

The plot shows the set of four random symbols. Each symbol has an elapse time
of 4 seconds.

.. image:: ../examples/modem1.png

The plot shows the modulated signal with the boundaries between the symbols.
For each symbol time, the code value is shown.

.. image:: ../examples/modem2.png

The plot shows the symbol correlation matrix of the modulated signal. The
correlation value reaches the maximum where the correlating symbol is equal to
the modulating symbol. For each code time, the symbol with maximum
correlation (+1) is marked in red.


.. image:: ../examples/modem3.png
