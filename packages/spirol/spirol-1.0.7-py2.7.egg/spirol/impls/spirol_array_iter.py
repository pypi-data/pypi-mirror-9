# -*- coding: utf-8 -*-

from __future__ import print_function

from shifty import shift_left

from spirol.impls import spirol_interface
from spirol.utils import SpirolCorner, SpirolDirection

try:
    xrange
except NameError:
    xrange = range


class _IterationComplete(Exception):
    pass


class _IterationDone(Exception):
    pass


class spirol_array_iter(spirol_interface):
    """
    A generator iterator that takes a two dimensional iterator as input and outputs
    [tuple(row, col)] from the iterator in a clockwise circular non-repeating shrinking spiral
    until the input iterator is exhausted.
    """
    NUM_MAX_ITEMS_TO_PRINT = 10
    DEFAULT_CORNER = SpirolCorner.TOP_LEFT
    DEFAULT_DIRECTION = SpirolDirection.CLOCKWISE

    def __init__(self, array, size, verbose=True,
                 print_max_items=NUM_MAX_ITEMS_TO_PRINT,
                 **kwargs):
        """
        :type array: two-dimensional iterable containing the required data.
        :type size: tuple (num_rows, num_cols) in the array.
        :type verbose: bool True: output debugging info, False - otherwise.
        :param debug: bool False - yield as iterator, True: otherwise.
        :param kwargs: specific kwargs to define this iterator's behaviour further.
        :attention: No validity is done on the input array because it is assumed that the input array is an iterable
            (which may be a generator - and we want to use generators if at all possible to save memory given that the
            input array may be unbounded.
        """
        size = self._validate_size(size)
        self._size = {'rows': size[0], 'cols': size[1]}
        self._array = array
        self._verbose = bool(verbose)
        self._print_max_items = int(
            print_max_items) if print_max_items else spirol_array_iter.NUM_MAX_ITEMS_TO_PRINT
        self._kwargs = kwargs
        kwargs['corner'] = SpirolCorner.validate(
            kwargs.get('corner', self.DEFAULT_CORNER))
        kwargs['direction'] = SpirolDirection.validate(
            kwargs.get('direction', self.DEFAULT_DIRECTION))

    def _scanners(self):
        _scanners = {
            SpirolDirection.CLOCKWISE: self.clockwise,
            SpirolDirection.COUNTER_CLOCK: self.counter_clock,
        }
        corner = self._kwargs['corner']
        row = SpirolCorner.row(corner, self.size)
        col = SpirolCorner.col(corner, self.size)
        return _scanners[self.direction], (row, col)

    @staticmethod
    def _validate_size(size):
        if not isinstance(size, (tuple, list)):
            raise ValueError('size must be a tuple(num_rows, num_cols)')
        return size

    @property
    def corner(self):
        return self._kwargs['corner']

    @corner.setter
    def corner(self, corner):
        self._kwargs['corner'] = SpirolCorner.validate(corner)

    @property
    def direction(self):
        return self._kwargs['direction']

    @direction.setter
    def direction(self, direction):
        self._kwargs['direction'] = SpirolDirection.validate(direction)

    @property
    def clockwise(self):
        shifts = {SpirolCorner.TOP_LEFT: 0,
                  SpirolCorner.TOP_RIGHT: 1,
                  SpirolCorner.BOTTOM_RIGHT: 2,
                  SpirolCorner.BOTTOM_LEFT: 3}
        return shift_left(['scan_right', 'scan_down', 'scan_left', 'scan_up'],
                          shifts[self.corner])

    @property
    def counter_clock(self):
        shifts = {SpirolCorner.TOP_LEFT: 0,
                  SpirolCorner.BOTTOM_LEFT: 1,
                  SpirolCorner.BOTTOM_RIGHT: 2,
                  SpirolCorner.TOP_RIGHT: 3}
        return shift_left(['scan_down', 'scan_right', 'scan_up', 'scan_left'],
                          shifts[self.corner])

    @property
    def array(self):
        return self._array

    @array.setter
    def array(self, array):
        self._array = array

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, size):
        self._size = self._validate_size(size)

    @property
    def verbose(self):
        return self._verbose

    @verbose.setter
    def verbose(self, verbose):
        self._verbose = bool(verbose)

    @property
    def print_max_items(self):
        return self._print_max_items

    @print_max_items.setter
    def print_max_items(self, print_max_items):
        if print_max_items:
            self._print_max_items = print_max_items
        return print_max_items

    @property
    def description(self):
        return '(%s, %s, %s from %s)' % (
        self._size['rows'], self._size['cols'], self.direction, self.corner)

    def __repr__(self):
        return 'spirol_array_iter%s' % self.description

    def __unicode__(self):
        return str(self)

    def __str__(self):
        def max_items(l=self._print_max_items):
            items = [i for i in iter(self)]
            l = min(l, len(items))
            if len(items) > l:
                a = ', '.join([str(i) for i in items[:l / 2]])
                b = ', '.join([str(i) for i in items[len(items) - l / 2:]])
                return ''.join(['[', '...'.join([a, b]), ']'])
            else:
                return ', '.join(['%s' % items])

        return ': '.join([self.__repr__(), max_items()])

    def __len__(self):
        return len([i for i in iter(self)])

    def scan(self):
        results = [i for i in self]
        self._verbose and print(results)
        return results

    def __iter__(self):
        def scan_right(row, col, row_end, col_end, row_start, col_start):
            #   Can we go right?
            if not (col_end - col_start) > 0:
                self._verbose and print('Cannot go right')
                raise _IterationComplete()
            else:
                for col in xrange(col_start, col_end):
                    yield (row, col)
                raise _IterationDone(row, col)

        def scan_down(row, col, row_end, col_end, row_start, col_start):
            #   Can we go down?
            if not (row_end - row_start) > 0:
                self._verbose and print('Cannot go down')
                raise _IterationComplete()
            else:
                for row in xrange(row_start, row_end):
                    yield (row, col)
                raise _IterationDone(row, col)

        def scan_left(row, col, row_end, col_end, row_start, col_start):
            #   Can we go left?
            if not (col_end - col_start) > 0:
                self._verbose and print('Cannot go left')
                raise _IterationComplete()
            else:
                for col in xrange(col_end - 1, col_start - 1, -1):
                    yield (row, col)
                raise _IterationDone(row, col)

        def scan_up(row, col, row_end, col_end, row_start, col_start):
            #   Can we go up?
            if not (row_end - row_start) > 0:
                self._verbose and print('Cannot go up')
                raise _IterationComplete()
            else:
                for row in xrange(row_end - 1, row_start - 1, -1):
                    yield (row, col)
                raise _IterationDone(row, col)

        col_start = row_start = row = col = 0

        col_end = self._size['cols']
        row_end = self._size['rows']

        increments_right = (0, 1, 0, 0)
        increments_down = (1, 0, 0, 0)
        increments_left = (0, 0, 0, -1)
        increments_up = (0, 0, -1, 0)

        increments_right_cw_start = (1, 0, 0, 0)
        increments_down_cw_start = (0, 0, 0, -1)
        increments_left_cw_start = (0, 0, -1, 0)
        increments_up_cw_start = (0, 1, 0, 0)

        increments_right_cc_start = (0, 0, -1, 0)
        increments_down_cc_start = (0, 1, 0, 0)
        increments_left_cc_start = (1, 0, 0, 0)
        increments_up_cc_start = (0, 0, 0, -1)
        #                                             method_name: [method, if_start, if_not_start]:
        _mapping = {SpirolDirection.CLOCKWISE: {
        'scan_right': [scan_right, increments_right_cw_start, increments_right],
        'scan_down': [scan_down, increments_down_cw_start, increments_down],
        'scan_left': [scan_left, increments_left_cw_start, increments_left],
        'scan_up': [scan_up, increments_up_cw_start, increments_up]},

                    SpirolDirection.COUNTER_CLOCK: {
                    'scan_right': [scan_right, increments_right_cc_start,
                                   increments_right],
                    'scan_down': [scan_down, increments_down_cc_start,
                                  increments_down],
                    'scan_left': [scan_left, increments_left_cc_start,
                                  increments_left],
                    'scan_up': [scan_up, increments_up_cc_start,
                                increments_up]},
        }

        scanners, (row, col) = self._scanners()

        try:
            while True:
                for i in scanners:
                    m = _mapping[self.direction][i]
                    try:
                        for result in m[0](row, col, row_end, col_end,
                                           row_start, col_start):
                            if result is not None:
                                row, col = result
                                yield (row, col)
                    except _IterationDone:
                        row_start += m[1][0]
                        col_start += m[1][1]
                        row_end += m[1][2]
                        col_end += m[1][3]
        except _IterationComplete:
            pass


if __name__ == '__main__':  # pragma: no cover
    pass
