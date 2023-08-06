# GridWalker
An iterable multi-dimensional grid used for exhaustive search and dimensional
problem solving.

## Description
Defines a Grid object which allows for efficient iteration across an arbitrary
number of dimensions. The  grid objects allow for iteration, multi-dimensional
select, and multi-dimensional slicing.

Accessing a grid follows the `__getitem__` convention of `[index]`. To retrieve
a multi-dimensional selection either `[index1, index2]` or `[(index1, index2)]`
may be used to specify the ordered dimensions of the grid to subselect. Any of
the index requests can be replaced by a slice object such that
`[index1, start2:end2:step2]` is a legal request.

Slices provide SubGrid objects which act as grids, but map their referenced data
back to the original grid object. This allows for repeated slicing of a grid with
near constant memory overhead at the cost of layered slice requests for each
change on the original data.

There are several provided Grids which are setup for efficiency for the given
data type. So far those include IntGrid, FloatGrid, and ObjectGrid -- the latter
of which is a general solution without efficient storage. These grid types
define the data being stored, rather than the indexing scheme. All grids use an
integer based indexing, though there are plans to create a float range grid which
does the float to index mapping behind the interface.

Note that creating grids with many dimensions can take up an extremely large amount
of memory, even when using an efficient scheme. This extends to a very long
iteration times as the number of elements to visit grows exponentially.
Take a 5 dimensional grid with 10 values for each dimension. this makes a 10^5
element grid -- which is 100k iterables -- and would take ~400kb of storage space.
The same grid with 100 values for each dimension would have 40 billion elements
and take more than 37GB of memory to store.

## Dependencies
* pydatawrap
* numpy

## Setup
### Installation
From source:

    python settup.py install

From pip:

    pip install gridwalker

## Features
* Multi-Dimensional grid definitions with arbitrary number of dimensions
* Iteration and assignment through efficient means across any dimensional assignment

## Navigating the Repo
### gridwalker
The implementation files for the repository.

### tests
All unit tests for the repo.

## Language Preferences
* Google Style Guide
* Object Oriented (with a few exceptions)

## TODO
* Create float index grids for floating precision grid iteration

## Author
Author(s): Matthew Seal

&copy; Copyright 2013, [OpenGov](http://opengov.com)
