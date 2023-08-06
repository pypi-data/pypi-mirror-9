import collections
import numpy as np
import sys
from datawrap import listwrap

class Grid(collections.MutableMapping):
    DimensionParam = collections.namedtuple('DimensionParam', ['first', 'last', 'step'])

    def __init__(self, grid_type, *dimensions):
        '''
        Args:
            grid_type: Defines the numpy type associated with this grid.
            dim_ranges defines the ranges of values in each dimension
                for an arbitrary number of dimensions. The type can be
                a slice or a tuple representing the values of a slice
                (i.e. (-10, 10, 2) starts from -10 and goes to 10 inclusive
                with a step size of 2). Note that slices are normally not
                inclusive.
        '''
        self.dim_ranges = []
        self.dim_restrictions = []
        self.dim_lengths = []

        for dim in dimensions:
            dim_param = self._convert_dim_to_param(dim)
            self.dim_ranges.append(dim_param)
            self.dim_restrictions.append(dim_param)
            self.dim_lengths.append(
                (dim_param.last + dim_param.step - dim_param.first) / dim_param.step)

        # Define our grid now as a numpy array
        self.grid = np.zeros(self.dim_lengths, dtype=grid_type)

    def _convert_dim_to_param(self, dim, default_params=DimensionParam(None,None,1)):
        '''
        Converts various dimension specifications into DimensionParam
        named tuple for use elsewhere in Grid
        '''

        first = last = step = None
        # Short-Circuit for DimensionParams
        if isinstance(dim, self.DimensionParam):
            return dim

        # Check for tuple type
        elif isinstance(dim, tuple):
            if len(dim) > 3 or len(dim) < 1:
                raise self._bad_dim_error(dim)
            elif len(dim) == 1:
                if dim[0] < 0:
                    first = dim[0]
                else:
                    last = dim[0]
            elif len(dim) == 2:
                first, last = dim
            elif len(dim) == 3:
                first, last, step = dim
        # Check for slice
        elif isinstance(dim, slice):
            first = dim.start
            last = dim.stop
            step = dim.step
        else:
            first = last = dim

        # Ensure that we don't have None values
        if first == None:
            first = default_params.first
        if last == None:
            last = default_params.last
        if step == None:
            step = default_params.step

        # Check for violations
        if (first == None or last == None or step == None or
            step < 1 or last < first):
            raise self._bad_dim_error(dim)

        return self.DimensionParam(first, last, step)

    def _bad_dim_error(self, dim):
        err = "Dimension range '%s' has an invalid or length range definition" % str(dim)
        return ValueError(err)

    def _check_against_limits(self, index, dimension):
        '''
        Checks single dimension restrictions on legal indexes.
        '''
        restrictions = self.dim_restrictions[dimension]
        if isinstance(index, slice):
            if ((index.start != None and
                 (index.start < restrictions.first or
                  index.start > restrictions.last)) or
                (index.stop != None and
                 (index.stop < restrictions.first or
                  index.stop > restrictions.last)) or
                (index.step and index.step % restrictions.step != 0) or
                (index.start != None and index.stop != None and
                 index.step > index.stop - index.start)):
                raise KeyError(index)
        else:
            if (index < restrictions.first or
                index > restrictions.last):
                raise KeyError(index)

    def _convert_to_array_index(self, index, dimension=0, depth=0):
        '''
        Converts index values from true locations to internal
        data structure values. It also handles slice requests
        and multi-dimensional requests (including slice multi-dim).
        '''
        drange = self.dim_ranges[dimension]
        restrictions = self.dim_restrictions[dimension]
        if listwrap.non_str_len_no_throw(index) > 0:
            # Don't allow searches beyond one recursion
            if depth > 0:
                raise KeyError(index)
            rebuilt_index = []
            # Rebuild the index element by element
            for dim, sub_index in enumerate(index):
                fixed_sub = self._convert_to_array_index(sub_index, dimension+dim, depth+1)
                rebuilt_index.append(fixed_sub)
            return tuple(rebuilt_index)
        else:
            # Will raise an exception if we're out of bounds
            self._check_against_limits(index, dimension)

        if isinstance(index, slice):
            # Get start index
            if index.start != None:
                start = (index.start - drange.first) / drange.step
            else:
                start = 0
            # Get stop index
            if index.stop != None:
                stop = (index.stop + drange.step - drange.first) / drange.step
            else:
                stop = self.dim_lengths[dimension]-1
            # Get step index
            if index.step != None:
                step = index.step / drange.step
            else:
                step = None
            result = slice(start, stop, step)
        else:
            result = (index - drange.first) / drange.step
        return result

    def _get_single_depth(self, multi_index):
        '''
        Helper method for determining how many single index entries
        there are in a particular multi-index.
        '''
        single_depth = 0
        for sub_index in multi_index:
            if isinstance(sub_index, slice):
                break
            single_depth += 1
        return single_depth

    def __getitem__(self, index):
        '''
        Getitem is rather complicated to handle the various cases
        of dimensional requests and slicing. All of the following
        are legal request types:

        single index: grid[0] => grid_type object
                                 (or SubGrid if not last dimension)
        compound index: grid[0][1] => grid_type object
                                      (or SubGrid if not last dimension)
        multi-index: grid[0, 1] => grid_type object
                                   (or SubGrid if not last dimension)
        slice: grid[0:1] => SubGrid
        slice with step: grid[0:10:2] => SubGrid
        compound slice: grid[0:10][2:8:2] => SubGrid
        multi-slice: grid[0:10, 2:8:2] => SubGrid
        compound mixed (index+slice): grid[0][2:8:2] => SubGrid
        multi-mixed (index+slice): grid[0, 2:8:2] => SubGrid
        '''
        rebuilt_index = self._convert_to_array_index(index)
        index_len = listwrap.non_str_len_no_throw(index)
        # SubGrid request
        if (len(self.dim_ranges) - index_len > 1 or
            (index_len > 0 and isinstance(rebuilt_index[-1], slice)) or
            isinstance(rebuilt_index, slice)):
            # Multi-index request
            if index_len > 0:
                single_depth = self._get_single_depth(index)
                # Single value indices for first single_depth values
                if single_depth > 0:
                    resolved_dims = rebuilt_index[:single_depth]
                    # Cut the grid at the depth position
                    return SubGrid(self.grid[resolved_dims], self.dim_ranges[single_depth:],
                                   self.dim_lengths[single_depth:],
                                   self.dim_restrictions[single_depth:], index[single_depth:])
                # First index in multi-index is a slice
                else:
                    return SubGrid(self.grid, self.dim_ranges, self.dim_lengths,
                                   self.dim_restrictions, index)
            # Slice request
            elif isinstance(rebuilt_index, slice):
                return SubGrid(self.grid, self.dim_ranges, self.dim_lengths,
                               self.dim_restrictions, [index])
            # Index request, but with remaining dimension restrictions
            # Thus still a SubGrid
            else:
                return SubGrid(self.grid[rebuilt_index], self.dim_ranges[1:], self.dim_lengths[1:],
                               self.dim_restrictions[1:])
        # Specific index for all dimensions
        else:
            return self.grid.__getitem__(rebuilt_index)

    def __setitem__(self, index, value):
        '''
        Can set on ranges of values as well individual indices
        '''
        rebuilt_index = self._convert_to_array_index(index)
        self.grid.__setitem__(rebuilt_index, value)

    def __delitem__(self, index):
        '''
        Resets the index to 0 ==> same as __setitem__(self, index, 0)
        '''
        self.__setitem__(index, 0)

    def __len__(self):
        '''
        Gives the length of the highest dimension
        '''
        restrict = self.dim_restrictions[0]
        return (restrict.last - restrict.first + restrict.step) / restrict.step

    def _generate_dim_range(self, dim):
        '''
        Generates a slice of the range for a particular dimension of
        the grid. Thus range(self._generate_dim_range()) produces the
        keys over a particular range.
        '''
        restrict = self.dim_restrictions[dim]
        start = restrict.first
        step = restrict.step
        stop = restrict.last+1
        return slice(start, stop, step)

    def _generate_mapped_grid_ranges(self):
        '''
        Generates the slice ranges of all valid keys for the grid at
        each dimension level.
        '''
        mapped_grid_ranges = []
        for dim in xrange(len(self.dim_restrictions)):
            mapped_grid_ranges.append(self._generate_dim_range(dim))
        return mapped_grid_ranges

    def _generate_true_grid_ranges(self):
        true_grid_ranges = []
        for dim in xrange(len(self.dim_restrictions)):
            restrict = self.dim_restrictions[dim]
            drange = self.dim_ranges[dim]
            start = self._convert_to_array_index(restrict.first, dim)
            step = restrict.step / drange.step
            stop = self._convert_to_array_index(restrict.last, dim)+step
            true_grid_ranges.append(slice(start, stop, step))
        return true_grid_ranges

    def get_raw_data_wrapper(self):
        dim_ranges = self._generate_true_grid_ranges()
        return listwrap.FixedListSubset(self.grid, *dim_ranges)

    def __iter__(self):
        dim_slice = self._generate_dim_range(0)
        return xrange(dim_slice.start, dim_slice.stop, dim_slice.step).__iter__()

    def full_iter(self):
        '''
        Iterates through the entire grid one cell at a time.
        This will touch every dimension point in the grid
        and returns the key associated with that iteration.
        '''
        class Link(object):
            def __init__(self, cursor, next_cursor, depth, prior, next_link):
                self.value = cursor
                self.next_value = next_cursor
                self.depth = depth
                self.prior = prior
                self.next = next_link

        class GridIter(object):
            def __init__(self, grid):
                self.grid = grid
                self.key_grid = []
                self.cursor_links = []
                self.cursor = None
                self.current_key = None
                prior_cursor = None
                # Construct our list of cursors and slices restrictions
                for dim, restrict in enumerate(grid.dim_restrictions):
                    restrict_slice = grid._generate_dim_range(dim)
                    self.key_grid.append(restrict_slice)
                    # Build a linked list of cursors
                    self.cursor = Link(restrict_slice.start,
                                       restrict_slice.start+restrict_slice.step,
                                       dim, prior_cursor, None)
                    self.cursor_links.append(self.cursor)
                    if prior_cursor != None:
                        prior_cursor.next = self.cursor
                    prior_cursor = self.cursor
                # Set the very last cursor so that it initialized to
                # the correct value for beginning iteration.
                if self.cursor != None:
                    self.cursor.next_value = self.cursor.value

            def __iter__(self):
                return self

            def next(self):
                # If our current cursor makes it to a None, we're done
                if self.cursor == None:
                    raise StopIteration()

                # Set our cursor value
                self.cursor.value = self.cursor.next_value

                # Get the slice for our current dimension
                cursor_slice = self.key_grid[self.cursor.depth]

                # Grab our key if we're at the lowest level of the cursors
                if self.cursor.next == None:
                    self.current_key = tuple(map(lambda c: c.value, self.cursor_links))
                else:
                    self.current_key = None

                # Update our value
                self.cursor.next_value += cursor_slice.step

                # Check if we've rotated through the whole dimension
                if self.cursor.value >= cursor_slice.stop:
                    # Reset our dimension cursor and go back up the
                    # cursor list by one
                    self.cursor.next_value = cursor_slice.start
                    self.cursor = self.cursor.prior
                    return self.next()
                # Check if we have and children to iterate
                elif self.cursor.next != None:
                    self.cursor = self.cursor.next
                    return self.next()

                # Return the fullkey, value tuple
                return self.current_key

        return GridIter(self)

    def full_iter_keys(self):
        return self.full_iter()

    def full_iter_values(self):
        '''
        Like full_iter, but return values instead of keys
        '''
        class GridValueIter(object):
            def __init__(self, grid):
                self.grid = grid
                self.griditer = grid.full_iter_keys()

            def __iter__(self):
                return self

            def next(self):
                fullkey = self.griditer.next()
                return self.grid[fullkey]
        return GridValueIter(self)

    def full_iter_items(self):
        '''
        Like full_iter, but return key, value pairs instead of just keys
        '''
        class GridItemIter(object):
            def __init__(self, grid):
                self.grid = grid
                self.griditer = grid.full_iter_keys()

            def __iter__(self):
                return self

            def next(self):
                fullkey = self.griditer.next()
                return (fullkey, self.grid[fullkey])
        return GridItemIter(self)

    def arg_max(self, grid_val_func=lambda k,v: v):
        '''
        Allows for argument maximization across all dimensions of the data.

        Args:
            grid_val_func: The evaluator for a given cell of the grid.
                Evaluators should take the key tuple and value pair and
                return a number which scores the given cell.
        '''
        max_arg = None
        max_score = -sys.maxint
        for key,val in self.full_iter_items():
            check = grid_val_func(key, val)
            if (check > max_score):
                max_score = check
                max_arg = key
        return max_arg

    def arg_min(self, grid_val_func=lambda k,v: v):
        '''
        Allows for argument minimization across all dimensions of the data.

        Args:
            grid_val_func: The evaluator for a given cell of the grid.
                Evaluators should take the key tuple and value pair and
                return a number which scores the given cell.
        '''
        return self.arg_max(lambda k,v: -grid_val_func(k,v))

    def __str__(self):
        '''
        This can be expensive for high dimension grids.
        '''
        mapper = self._generate_dim_range(0)
        if len(self) <= 100:
            return repr(self)
        else:
            mapitems = [(key, self[key]) for key in xrange(mapper.start,
                                                           mapper.start+(100*mapper.step),
                                                           mapper.step)]
            return str(mapitems)[:-1] + ", ... ]"

    def __repr__(self):
        '''
        This can be expensive for high dimension lists.
        '''
        mapper = self._generate_dim_range(0)
        mapitems = [(key, self[key]) for key in xrange(mapper.start,
                                                       mapper.stop,
                                                       mapper.step)]
        return repr(mapitems)

class SubGrid(Grid):
    '''
    Wraps the Grid object with a constructor which builds a
    subset of the parent grid. This should only be used by
    Grid objects. Edits to this grid affect the parent grid
    which constructed this SubGrid.
    '''
    def __init__(self, grid, dim_ranges, dim_lengths, dim_restrictions, add_restrictions=None):
        self.dim_ranges = dim_ranges
        self.dim_lengths = dim_lengths
        self.dim_restrictions = dim_restrictions
        self.grid = grid

        # Do this check/assignment After the others
        if add_restrictions:
            if len(add_restrictions) > self.dim_restrictions:
                raise ValueError("Length of restrictions exceeds dimension limits of data")
            add_restrictions = self._convert_restrictions(add_restrictions)
            self.dim_restrictions = self._combine_restrictions(self.dim_restrictions, add_restrictions)

    def _convert_restrictions(self, restrictions):
        '''
        Helper method to convert all restrictions in the input
        list into DimensionParam objects.
        '''
        converted = []
        for i, restrict in enumerate(restrictions):
            converted.append(self._convert_dim_to_param(restrict, self.dim_restrictions[i]))
        return converted

    def _combine_restrictions(self, first_restrictions, second_restrictions):
        '''
        Combines dimensional restrictions from two sources
        '''
        combined_params = []
        for i in xrange(max(len(first_restrictions), len(second_restrictions))):
            first_param = first_restrictions[i] if i < len(first_restrictions) else None
            second_param = second_restrictions[i] if i < len(second_restrictions) else None

            # Check all 4 cases
            if first_param == None and second_param != None:
                combined_params.append(second_param)
            elif first_param != None and second_param == None:
                combined_params.append(first_param)
            elif first_param != None and second_param != None:
                first = max(first_param.first, second_param.first)
                last = min(first_param.last, second_param.last)
                step = max(first_param.step, second_param.step)
                small_step = min(first_param.step, second_param.step)
                if step % small_step != 0:
                    raise ValueError("Dimension restriction step sizes are not "+
                                     "multiples of each other ("+str(first_param.step)+
                                     ", "+str(second_param.step)+")")

                param = self.DimensionParam(first, last, step)
                if last < first:
                    raise ValueError("Dimension restriction is NULL set "+str(param))
                combined_params.append(param)
            else:
                # This should never be reached
                raise ValueError("Could not combine restrictions")
        return combined_params

class FloatGrid(Grid):
    '''
    Defines a grid with floating values at each dimension point.
    '''
    def __init__(self, *dimensions):
        Grid.__init__(self, np.float, *dimensions)

class IntGrid(Grid):
    '''
    Defines a grid with integer values at each dimension point.
    '''
    def __init__(self, *dimensions):
        Grid.__init__(self, np.int, *dimensions)

class ObjectGrid(Grid):
    '''
    Defines a grid with arbitrary object values at each dimension point.
    '''
    def __init__(self, *dimensions):
        Grid.__init__(self, object, *dimensions)

# TODO add dimension mappers as optional argument to allow floating or string indexes
