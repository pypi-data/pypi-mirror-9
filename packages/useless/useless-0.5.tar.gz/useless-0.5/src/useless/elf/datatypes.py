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


class ELF_Sword(BinaryDataType):
    length = 4
    struct_type = 'I'


class ELF_Word(ELF_Sword):
    struct_type = 'i'


class ELF_Xword(BinaryDataType):
    length = 8
    struct_type = 'Q'


class ELF_Sxword(BinaryDataType):
    length = 8
    struct_type = 'q'


class ELF_Half(BinaryDataType):
    length = 2
    struct_type = 'H'


class ELF_Unsigned_Char(BinaryDataType):
    length = 1
    struct_type = 'B'


class ELF_Addr(BinaryDataType):
    length = 8
    struct_type = 'Q'


class ELF_Off(ELF_Xword):
    pass
