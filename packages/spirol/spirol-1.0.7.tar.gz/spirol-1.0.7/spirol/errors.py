#    -*- coding: utf-8 -*-


class InputFormatError(Exception):
    """
    The input array over which the spirol is iterating is not a pure two dimensional array.
        ie: the number of elements in the input array is not equal to the sum of the array dimensions.
    """
    pass


class UnknownImplementation(ValueError):
    pass


class InvalidDirection(ValueError):
    pass


class InvalidCorner(ValueError):
    pass


class NotSupportedError(Exception):
    pass


class NonSpirolInterface(TypeError):
    pass

if __name__ == '__main__':      # pragma: no cover
    pass