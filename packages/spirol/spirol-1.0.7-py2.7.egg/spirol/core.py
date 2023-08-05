#    -*- coding: utf-8 -*-

from spirol.errors import InputFormatError
from spirol.impl_factory import spirol_factory
from spirol.utils import SpirolType


class spirol_core(object):
    """
    A generator iterator that takes a two dimensional iterator as input and outputs
    items from the iterator in a clockwise circular non-repeating shrinking spiral
    until the input iterator is exhausted.
    """
    NUM_MAX_ITEMS_TO_PRINT = 10

    def __init__(self, array, size, spirol_type=SpirolType.SPIRAL_CIRCULAR_OUTSIDE_IN, verbose=False,
                 print_max_items=NUM_MAX_ITEMS_TO_PRINT, **kwargs):
        """
        A spirol instance contains a specific implementation of a spirol iterator. This iterator is configurable.
        :see: SpirolType
        :param array: two-dimensional iterable containing the required data.
        :param size: tuple (num_rows, num_cols) in the array.
        :param verbose: bool True: output debugging info, False - otherwise.
        :param print_max_items: int(number of items to show in _str__ output).
        :param kwargs: specific kwargs to define the 'spirol_type' behaviour further.
        :attention: No validity is done on the input array because it is assumed that the input array is an iterable
            (which may be a generator - and we want to use generators if at all possible to save memory given that the
            input array may be unbounded.
        :return:
        """
        iterator = spirol_factory(spirol_type)
        self._iterator = iterator(array, size=size, verbose=verbose, print_max_items=print_max_items,
                                  **kwargs)

    @property
    def verbose(self):
        return self._iterator.verbose

    @property
    def size(self):
        return self._iterator.size

    @property
    def array(self):
        return self._iterator.array

    @property
    def print_max_items(self):
        return self._iterator.print_max_items

    def __iter__(self):
        for (row, col) in self._iterator:
            try:
                yield self.array[row][col]
            except IndexError as e:
                raise InputFormatError(e)

    def scan(self):
        results = []
        for (row, col) in self._iterator.scan():
            try:
                results.append(self.array[row][col])
            except IndexError as e:
                raise InputFormatError(e)
        return results

    @property
    def description(self):
        return self._iterator.description

    @property
    def impl(self):
        return self._iterator

    def __repr__(self):
        return 'spirol%s' % self.description

    def __unicode__(self):
        return str(self)

    def __str__(self):
        def max_items(l=self.print_max_items):
            items = [i for i in self.scan()]
            l = min(l, len(items))
            if len(items) > l:
                a = ', '.join([str(i) for i in items[:int(int(l / 2))]])
                b = ', '.join([str(i) for i in items[len(items) - int(l / 2):]])
                return ''.join(['[', '...'.join([a, b]), ']'])
            else:
                return ', '.join(['%s' % items])
        return ': '.join([self.__repr__(), max_items()])

    def __len__(self):
        return len(self.impl)

if __name__ == '__main__':      # pragma: no cover
    pass
