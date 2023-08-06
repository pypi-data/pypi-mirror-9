"""
The MIT License (MIT)

Copyright (c) 2015 Riccardo Cagnasso

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


import collections
from .datatypes import BinaryDataType
from .enums import BinaryEnum
import inspect


class OrderedClass(type):
    """
        Class with fields ordered in order of declaration
    """

    @classmethod
    def __prepare__(metacls, name, bases, **kwds):
        return collections.OrderedDict()

    def __new__(cls, name, bases, namespace, **kwds):
        result = type.__new__(cls, name, bases, dict(namespace))
        result.members = tuple(namespace)
        return result


class Structure(metaclass=OrderedClass):
    """
        Structure is the main brick for useless.

        All data structures like Headers or tables entries in ELF or PE/COFF
        specifications, will be represented with a Structure class.

        When a Structure class is initialized, all BinaryDataType/BinaryEnum
        will be iterated in order on declaration and the "parse" method will be
        called, sobstituting the value of the field with the result. This
        is inspired by SQLAlchemy Declarative.
    """

    def __init__(self, stream, offset=0):
        self.stream = stream

        self.stream.seek(offset)

        for attrname in self.__class__.get_fields_names():
            setattr(self, attrname, getattr(
                self, attrname).parse(self.stream))

    @classmethod
    def get_fields_names(cls):
        for attrname in cls.members:
            attr = getattr(cls, attrname)
            if inspect.isclass(attr):
                if issubclass(attr, BinaryDataType) or\
                        issubclass(attr, BinaryEnum):
                    yield attrname

    @classmethod
    def get_size(cls):
        """
            Total byte size of fields in this structure => total byte size of
            the structure on the file
        """
        return sum([getattr(cls, name).length
                    for name in cls.get_fields_names()])

    def __repr__(self):
        fields = "\n".join(
            ["\t{0} = {1}".format(attrname, getattr(self, attrname).__repr__())
                for attrname in self.__class__.get_fields_names()])

        return "{0} \n {1}".format(self.__class__.__name__, fields)
