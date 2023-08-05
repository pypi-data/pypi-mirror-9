# YTER

Clever, quick iterator functions that make your smile whiter.

This will work with versions of Python 2.6+ and 3.2+. The tests also pass with
recent Pypy and Jython releases.


## Functions

There are many functions that process data from iterators in efficient ways.

* [yany] -- Extended version of the builtin any, test if any values are true
* [yall] -- Extended version of the builtin all, test if all values are true
* [last] -- Get the final value from an iterator
* [head] -- Get the first values from an iterator
* [tail] -- Get the last values from an iterator
* [finish] -- Complete an iterator and get number of values
* [minmax] -- Find the minimum and maximum values from an iterable
* [minmedmax] -- Find the minimum, median, and maximum values from an iterable
* [isiter] -- Test if an object is iterable, but not a string type

## Iterators

There are several iterators that wrap an existing iterator and process it's output.

* [call] -- Iterator that works with mixed callable types
* [percent] -- Iterator that skips a percentage of values
* [flat] -- Iterator of values from a iterable of iterators
* [chunk] -- Iterator of lists with a fixed size from iterable

