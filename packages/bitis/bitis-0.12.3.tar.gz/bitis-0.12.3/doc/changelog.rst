Changes
*******

Release 0.12.3 (released 9-Dec-2014)
====================================

Changes
-------
* Methods older and newer: rewrite of boundary conditions processing.

Bugs fixed
----------
* Method split: wrong return signal when split at or after self end.
* Method older: wrong end time of return signal.

Documentation
-------------
* Methods split, newer and older: new documentation and layout.


Release 0.12.2 (released 6-Dec-2014)
====================================

Bugs fixed
----------
* Method correlation: fix wrong computation of correlation function when there
  is a mask.
* Method phase: fix initial search width not set to the whole shift range.

Documentation
-------------
* Method correlation: new documentation layout.


Release 0.12.1 (released 3-Dec-2014)
====================================

New features
------------
* Method phase: add correlation value at phase shift.

Bugs fixed
----------
* Method phase: fix incomplete refactoring of other identifier.


Release 0.12.0 (released 1-Dec-2014)
====================================

New features
------------
* Method shift: now skips computations for zero offset.
* New method phase: computation of phase among two signals.

Changes
-------
* Method split: now manage a split time outside signal domain returning the
  proper void signal.
* Method correlation: dropped step_left and step_right arguments, substituted
  skip and width.
* Method plotchar: dropped period argument.
* Method mod2code: now symbol start time is the phase with respect to the sig
  start time.
* Methods noise and square: now require an origin argument.
   
Internals
---------
* Method correlation: refactoring for new arguments skip and width.
* Method correlation: augumented test.
* New method phase: add test.

Documentation
-------------

* Started better layout for function/methods arguments and return patterns.


Release 0.11.2 (released 8-Oct-2014)
====================================

Bugs fixed
----------
* Method plotchar: missing last non flat char after flat chars.


Release 0.11.1 (released 6-Oct-2014)
====================================

Changes
-------
* Method plotchar: now argument max_flat deault is None, was 100 .

Bugs fixed
----------
* Method level: now for time < start return (None,0) .
* Method plotchar: last flat lost when signal end < plot end.
* Method stream: now the newest part is self, was a new allocated signal.
    
Internals
---------
* Method plotchar refactored.
* New test for methods level and plotchar.


Release 0.11.0 (released 1-Oct-2014)
=====================================

Features added
--------------
* Method plotchar: semigraphic signal plot with line drawing characters.

Changes
-------
* Method level: now return None, len(signal) when time is beyond signal end.
* Method elapse: return zero when signal is void, before was none.

Bugs fixed
----------
* Method serial_tx: returned void signal when chars had len == 1.
* Method serial_rx: dead lock when last sample time was before end time and
  after last ege time.

Documentation
-------------
* Add example plot.


Release 0.10.0 (released 26-Sep-2014)
=====================================

Features added
--------------
* Method validate: a consistency checker for signal attributes.
* Method code2mod: code to symbols signal modulator.
* Method mod2code: demodulator by maximum correlation symbol estimation.
* Example "modulation".
* New method end_level: return the ending level of a signal.
* New method older: return the older part of a signal with respect to a given
  time.
* New method newer: return the newer part of a signal with respect to a given
  time.

Changes
-------
* Method test changed to function.
* Signal instancing now validate signal attributes.
* Now, instancing of Signal() generates a void signal.
* Changed return of method split when split time falls outside signal domain.
* Now method serial_tx generate a serial signal with start=origin.

Bugs fixed
----------
* Method chop: wrong chop when split falls on signal end.
* Method __add__: added inplace=false to join call.
* Method level: wrong level returned.
* Method join: changed start and end calls with corresponding attributes.
* Method serial_rx: corrected wrong char start detection and level tests.
* Method noise: missing return argument, the noise signal itself.
* Method append: now update correctly the end time of the result.

Documentation
-------------
* Added the rules of BTS format.

Internals
---------
* Rewrite of void signal handling through all methods and functions.
* New test for methods code2mod and mod2code.
* Refactored method split with method level.
* Added random inplace to spit/join test.
* New test for methods older and newer.
* Method append: now implemented with a call to split.


Release 0.9.0 (released 10-Sep-2014)
====================================

Features added
--------------
* New method level: return the signal level and edge position at a given time.
* Methods shift, reverse, __invert__ now can work inplace: result into self signal.
* New method __nonzero__: return true if the signal is not empty. 

Changes
-------
* All methods and objects changed to work with the new BTS format (v2).
* Removed methods: start, end.

Bugs fixed
----------
* Fix method reverse: now works when signal start != 0.
* Fix method split when split time falls on signal start or end and after last edge.
* Fix method chop.
* Fix methods __eq__ and __ne__: now work when operands are None.
* Fix function serial_rx. Now work with constant (no edges) signals. Eliminated
  spurious status generation.

Internals
---------
* Method _intersect now returns as last edge position the position plus one.
* Added tests for inplace/noinplace testing.


Release 0.8.0 (released 26-Aug-2014)
====================================

Features added
--------------
* New method chop: divide a signal in a sequence of contiguous signal of
  given period.
* Method correlation now has a mask argument: if mask signal is not none, the
  correlation is computed only where mask=1.
* Method join now has an inplace arguments. When true, no new signal is
  generated for the join result. Self signal is used instead.
* Method pwm2bin now can convert by synchronouos symbols correlation.
* Method split now has an inplace argument. When true, no new signal is
  generated for the newer signal part. Self signal is used instead.
* Method split, when splitting on a signal change time, now assigns the change
  to the start of the newer signal part.

Changes
-------
* Methods start, end, elapsed now return None when the signal time changes
  sequence is empty.
* Method bin2pwm now signal start=origin and signal end is not extended.

Bugs fixed
----------
* Fix method correlation stepping limits for defaults.
* Fix method split splitting on a change time: now correct end of older part
  and correct start of newer part are generated.
  start of newer were generated.
* Fix method serial_rx bit time computation: use floats.

Internals
---------
* Added test for method chop.
* Added test for new the convertion mode (sync symb corr) of method pwm2bin.


Release 0.7.1 (released 3-Feb-2014)
===================================

Bugs fixed
----------
* Fix inequality test: missing __ne__ method.

Internals
---------
* Optimized "and" and "or" operator for constant signals.


Release 0.7.0 (released 27-Jan-2014)
====================================

Features added
--------------
* Add buf_step to method stream.
* Add return self to in place working method clone_into.

Incompatible changes
--------------------
* Change step_start, step_num with step_left, step_right in method correlation.
* Change correlation unittest from a graphic one to procedural only.


Release 0.6.0 (released 16-Dec-2013)
====================================

Features added
--------------
* Add method clone_into.
* Add method concatenate: add operator.
* Add method stream.
* Add method elapse returning the signal elapse time.
* Add example to demonstrate phase recovery from a noisy signal (lockin).
* Add examples, module reference, bts format, change log to doc pages.
* Add unittest for stream.

Incompatible changes
--------------------
* Change start level with active argument in noise method.

Bugs fixed
----------
* Fix method append: make it return the signal with the append result.
* Fix shift in correlation method.
* Fix time shift computation in correlaton method: was delayed by 1 step size.

Internals
---------
* Change method append: check arguments with assert.
* Refactor method split.


Release 0.5.0 (released 9-Dec-2013)
===================================

Features added
--------------
* Embed y limits setting into plot method.
* Add method square for signal generation of a periodc square wave.
* Add a more fine control in correlation function computation.
* Add signal append method.
* Add method start, return signal start time.
* Add method end, return signal end time.
* Add method len, return signal change times sequence length.

Incompatible changes
--------------------
* Change start times computation in bin2pwn, serial_tx to minimize
  time elapse from start to first change.

Bugs fixed
----------
* Fix 0.4.0 release changelog: missing changes.

Internals
---------
* Change noise from method to function.
* Change examples for changed noise method.


Release 0.4.0 (released 2-Dec-2013)
===================================

Features added
--------------
* Add signal split method.
* Add two signals join method.
* Add unittest for split and join.
* Add float times capability to BTS signals.

Incompatible changes
--------------------
* Uniformate pwm2bin arguments to bin2pwm methods.
* Add tscale=1. argument in bin2pwm.
* Change to tscale=1. argument in serial_tx.

Bugs fixed
----------
* Fix slevel setup, signal start and end in bin2pwm.

Internals
---------
* Rewrite jitter method.


Release 0.3.0 (released 11-Nov-2013)
====================================

Features added
--------------
* Add async serial transmitter (bits.serial_tx method) from chars to BTS
  serial line signal.
* Add async serial receiver (bitis.serial_rx method) from BTS serial line
  to chars.
* Add async serial transmitter example: serial_tx.py.
* Add unittest for async serial tx and rx.
* Modified plot method: only 0,1 ticks on y axis.


Release 0.2.0 (released 4-Nov-2013)
===================================

Features added
--------------
* Add PWM coder and decoder between a BTS signal (PWM) and a binary code.
* New correlation example.


Release 0.1.0 (released 29-Oct-2013)
====================================

* First release.
