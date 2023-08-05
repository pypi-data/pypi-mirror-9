#    -*- coding: utf-8 -*-


class spirol_interface(object):     # pragma: no cover
    """
    Mandatory attributes / properties:
    verbose(bool)
    size(tuple(int(num_rows), int(num_cols)))
    array(2-dimensional array) of input data.
    print_max_len(int(num_values_to_print))
    description
    """

    def __iter__(self):
        """
        Iterator-generator method for determining the result for the given inputs.
        :return: yield result of a single iteration.
        """
        raise NotImplementedError()

    def scan(self):
        """
        Non iterator-generator method for determining the result for the given inputs.
        :return: The result of the iteration.
        """
        raise NotImplementedError()

    def __len__(self):
        """
        Calculate the actual length of the resultant iterable.
        :attention: This performs the iteration and is therefor a potentially expensive computation.
        :return: int
        """
        raise NotImplementedError()

    def __repr__(self):
        """
        Produce a nice programmatic representation of this instance.
        :return: str
        """
        raise NotImplementedError()

    def __str__(self):
        """
        Produce a nice human-readable representation of this instance.
        :return: str
        """
        raise NotImplementedError()
