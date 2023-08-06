import re

__all__ = ["to_snake", "Error", "EqualityMixin"]

def to_snake(string):
    """
    Converts a string from camel case to snake case

    :param string: The string to convert
    """
    return re.sub('(?!^)([A-Z]+)', r'_\1', string).lower()

class Error(Exception):
    """
    A base class for all Errors in this module
    """
    pass

class EqualityMixin(object):
    """
    A mixin that implements :func:`__eq__` and :func:`__ne__` by comparing the
    types and internal dictionaries of the two objects
    """
    def __eq__(self, other):
        return (isinstance(other, self.__class__) and self.__dict__ ==
            other.__dict__)
    def __ne__(self, other):
        return not self.__eq__(other)
