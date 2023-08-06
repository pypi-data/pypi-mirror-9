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


from .datatypes import *
from .enums import *
from ..common import parse_cstring
from ..common.structures import *
from cached_property import cached_property


class ELF_Header(Structure):
    e_type = ELF_Half
    e_machine = ELF_Half
    e_version = ELF_Word
    e_entry = ELF_Addr
    e_phoff = ELF_Off
    e_shoff = ELF_Off
    e_flags = ELF_Word
    e_ehsize = ELF_Half
    e_phentsize = ELF_Half
    e_phnum = ELF_Half
    e_shentsize = ELF_Half
    e_shnum = ELF_Half
    e_shstrndx = ELF_Half

    def __init__(self, stream, offset=0):
        super(ELF_Header, self).__init__(stream, offset)


class ELF_SectionHeader(Structure):
    sh_name = ELF_Word
    sh_type = ELF_SectionType
    sh_flags = ELF_Xword
    sh_addr = ELF_Addr
    sh_offset = ELF_Off
    sh_size = ELF_Xword
    sh_link = ELF_Word
    sh_info = ELF_Word
    sh_addralign = ELF_Xword
    sh_entsize = ELF_Xword

    def __init__(self, stream, offset=0, elf=None):
        self.elf = elf

        super(ELF_SectionHeader, self).__init__(stream, offset)

    @property
    def name(self):
        return self.elf.section_string_table.get_string(self.sh_name)


class ELF_StringTable(object):
    def __init__(self, stream, offset):
        self.stream = stream
        self.offset = offset

    def get_string(self, string_offset):
        return parse_cstring(self.stream, self.offset+string_offset)


class ELF_Symbol(Structure):
    st_name = ELF_Word
    st_info = ELF_Unsigned_Char
    st_other = ELF_Unsigned_Char
    st_shndx = ELF_Half
    st_value = ELF_Addr
    st_size = ELF_Xword

    def __init__(self, stream, offset=0, header=None):
        self.elf_header = header

        super(ELF_Symbol, self).__init__(stream, offset)

    @property
    def name(self):
        return self.elf_header.dynsym_string_table.get_string(self.st_name)
