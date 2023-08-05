#    -*- coding: utf-8 -*-

"""
Various tools used in spirol.

"""

from spirol.errors import InvalidDirection, InvalidCorner, UnknownImplementation


TOP_LEFT = 'tl'
TOP_RIGHT = 'tr'
BOTTOM_RIGHT = 'br'
BOTTOM_LEFT = 'bl'
CLOCKWISE = 'clockwise'
COUNTER_CLOCK = 'counterclock'


class SpirolType(object):
    SPIRAL_CIRCULAR_OUTSIDE_IN = 'spirol_circular_outside_in'
    VALID_TYPES = [SPIRAL_CIRCULAR_OUTSIDE_IN]

    @staticmethod
    def validate(type_):
        if type_ not in SpirolDirection.VALID_DIRECTIONS:
            raise UnknownImplementation(type_, SpirolType.VALID_TYPES)
        return type_


class SpirolDirection(object):
    CLOCKWISE = CLOCKWISE
    COUNTER_CLOCK = COUNTER_CLOCK
    VALID_DIRECTIONS = [CLOCKWISE, COUNTER_CLOCK]

    @staticmethod
    def validate(direction):
        if direction not in SpirolDirection.VALID_DIRECTIONS:
            raise InvalidDirection(direction, SpirolDirection.VALID_DIRECTIONS)
        return direction


class SpirolCorner(object):
    TOP_LEFT = TOP_LEFT
    TOP_RIGHT = TOP_RIGHT
    BOTTOM_RIGHT = BOTTOM_RIGHT
    BOTTOM_LEFT = BOTTOM_LEFT
    VALID_CORNERS = [TOP_LEFT, TOP_RIGHT, BOTTOM_LEFT, BOTTOM_RIGHT]
    _mapping = {
        TOP_LEFT: (0, 0),
        BOTTOM_LEFT: (-1, 0),
        TOP_RIGHT: (0, -1),
        BOTTOM_RIGHT: (-1, -1)}

    @staticmethod
    def validate(corner):
        if corner not in SpirolCorner.VALID_CORNERS:
            raise InvalidCorner(corner, SpirolCorner.VALID_CORNERS)
        return corner

    @staticmethod
    def row(corner, size):
        SpirolCorner.validate(corner)
        value = SpirolCorner._mapping[corner]
        return value[0] if not value[0] else (size['rows'] - 1)

    @staticmethod
    def col(corner, size):
        SpirolCorner.validate(corner)
        value = SpirolCorner._mapping[corner]
        return value[1] if not value[1] else (size['cols'] - 1)

if __name__ == '__main__':      # pragma: no cover
    pass
