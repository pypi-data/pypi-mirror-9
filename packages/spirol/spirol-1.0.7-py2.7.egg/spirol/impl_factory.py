#    -*- coding: utf-8 -*-


from spirol.errors import UnknownImplementation, NonSpirolInterface
from spirol.impls import spirol_interface
from spirol.impls.spirol_array_iter import spirol_array_iter
from spirol.utils import SpirolType


def spirol_factory(spirol_type):
    """
    A factory the return <type>spirol iterators.
    :param spirol_type: str
    :see: 'SpirolType'.
    :return:
    """
    _mapping = {
        SpirolType.SPIRAL_CIRCULAR_OUTSIDE_IN: spirol_array_iter
    }

    try:
        interface = _mapping[spirol_type]
    except KeyError:
        raise UnknownImplementation(spirol_type)
    else:
        if spirol_interface not in interface.__bases__:     # pragma: no cover
            raise NonSpirolInterface(interface)
        return interface

if __name__ == '__main__':      # pragma: no cover
    pass
