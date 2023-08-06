==========
BTS format
==========

Definition
----------

The scope of this memo is to describe the BTS, Binary Timed Signal. A format
for compact storage of binary signals in computer memory.
Binary signals are signal that can have only two logic levels/states, zero or one,
true or false.

The *BTS* format is composed by 5 signal elements.

1. The start time, integer or float.
2. The edges times, sequence of integers or floats.
3. The end time, integer or float.
4. The start level, integer or boolean.
5. The time scale, integer or float.

**Start time**

The start time of the signal. Before this time, the signal is not defined.
When it is none, the signal is considered void.

**Edges times**

This sequence stores all the times where the signal changes its level from
0 to 1 or viceversa. 
The edge times sequence may be empty: in this case the signal is constant.
The sequence must be sorted in ascending order.
All elements must have different times.
The first element must be greater or equal to the start time.
The last element must be lower or equal to the end time.

**End time**

The end time of the signal. After this time, the signal is not defined.
The end time must be greater than the start time.
May be none when start is none.

**Start level**

If the edges times sequence has 1 or more items, the start level value
specifies the signal level from the signal start time to the first edge time.
If the edges times sequence is empty, the signal has a constant level
that is equal to the start level value.

**Time scale**

An arbitrary unit of time can be chosen to express the values of times.
The time scale value is the ratio: 1 second / arbitrary time unit.


Python implementation
---------------------

**BITIS** implements the *BTS* format with the *Signal* class. Each BTS
signal is an instance of this class. The five elements of the BTS format
are the five attributes (*start, edges, end, slevel, tscale*) of the *Signal* class.
The sequence *edges* is realized as list of integers or floats.


========================
Pre version 0.9.0 format
========================

Pre 0.9.0 definition
--------------------

The *BTS* format is composed by 3 elements.

1. The change times.
2. The start level.
3. The time scale.

**Change times**

This sequence stores all the times where the signal changes its level from
0 to 1 or viceversa. The first and the last sequence items have a different
meaning: they are respectively the start time and the end time of the signal.
The signal start and end are the boundaries of the signal domain. Outside
this interval, the signal is to be itended as not defined.
The change times sequence may be empty: in this case the signal must
be threated as empty or null. The sequence may have 2 items: in this case
the signal has a constant level along all its domain and there are no level
changes. The sequence may have 3 or more items: in this case the signal has
1 or more level changes. A sequence with only one item is not allowed.
The sequence must be sorted in ascending order.

**Start level**

If the change times sequence has 3 or more items, the start level value
specifies the signal level from the signal start time to the first change time.
If the change times sequence has 2 items, the signal has a constant level
that is equal to the start level value.

**Time scale**

An arbitrary unit of time can be chosen to express the values of change times.
The time scale value is the ratio: 1 second / arbitrary time unit.


Pre 0.9.0 python implementation
-------------------------------

**BITIS** implements the *BTS* format with the *Signal* class. Each BTS
signal is an instance of this class. The three elements of the BTS format
are the three attributes (*times, slevel, tscale*) of the *Signal* class.
The sequence *times* is realized as list of integers or floats.
