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

import struct
from ..common.datatypes import BinaryDataType


class PE_Char(BinaryDataType):
    length = 1
    struct_type = 'B'


class PE_Word(BinaryDataType):
    length = 2
    struct_type = 'H'


class PE_DWord(BinaryDataType):
    length = 4
    struct_type = 'I'


class PE_NameField(BinaryDataType):
    length = 8
    struct_type = 'c'

    @classmethod
    def parse(cls, stream):
        string = ""

        for i in range(0, cls.length):
            char = struct.unpack('c', stream.read(1))[0]

            if char == b'\x00':
                pass
            else:
                string += char.decode()

        return string
