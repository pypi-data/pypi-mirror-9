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

from cached_property import cached_property
from useless.PE.structures import *
from useless.PE.datatypes import *
from ..common import parse_cstring

PE_HEADER_OFFSET_CONSTANT = 0x3c


class PE_File(object):
    """
        PE_File represents a PE dynamic object and provides methods to
        access all data structures
    """

    def __init__(self, stream):
        self.stream = stream

        self.stream.seek(PE_HEADER_OFFSET_CONSTANT)
        self.pe_header_offset = PE_Word.parse(stream)

    @cached_property
    def coff_header(self):
        return COFF_Header(self.stream, self.pe_header_offset)

    @cached_property
    def optional_standard_fields(self):
        return OptionalHeader_StandardFields(
            self.stream,
            self.pe_header_offset + COFF_Header.get_size())

    @cached_property
    def optional_windows_fields(self):
        offset = self.pe_header_offset +\
            COFF_Header.get_size() +\
            OptionalHeader_StandardFields.get_size()
        return OptionalHeader_WindowsFields(self.stream, offset)

    @property
    def optional_data_directories(self):
        """
            Data directories entries are somewhat wierd.

            First of all they have no direct type information in it, the type
            is assumed from the position inside the table. For this reason
            there are often "null" entries, with all fields set to zero.

            Here we parse all the entries, assign the correct type via position
            and then filter out the "null" ones.

            Even if the algorithm itself if quite simple, figuring it required
            a huge amount of time staring at PE/COFF specification with a 8O
            like expression thinking "WTF? WTF! WTF? WHY?!"
        """
        base_offset = self.pe_header_offset +\
            COFF_Header.get_size() +\
            OptionalHeader_StandardFields.get_size() +\
            OptionalHeader_WindowsFields.get_size()

        for i in range(0, self.optional_windows_fields.NumberOfRvaAndSizes):
            offset = base_offset + i*OptionalHeader_DataDirectory.get_size()
            header = OptionalHeader_DataDirectory(self.stream, offset, i)

            if not header.is_empty():
                yield header

    @property
    def section_headers(self):
        base_offset = self.pe_header_offset +\
            COFF_Header.get_size() +\
            OptionalHeader_StandardFields.get_size() +\
            OptionalHeader_WindowsFields.get_size() +\
            OptionalHeader_DataDirectory.get_size() * \
            self.optional_windows_fields.NumberOfRvaAndSizes

        for i in range(0, self.coff_header.NumberOfSections):
            offset = base_offset + i*Section_Header.get_size()
            yield Section_Header(self.stream, offset)

    def get_section_of_rva(self, rva):
        for s in self.section_headers:
            if s.VirtualAddress <= rva and\
               (s.VirtualAddress + s.VirtualSize) > rva:
                return s

    def resolve_rva(self, rva):
        """
            RVAs are supposed to be used with the image of the file in memory.
            There's no direct algorithm to calculate the offset of an RVA in
            the file.

            What we do here is to find the section that contains the RVA and
            then we calculate the offset between the RVA of the section
            and the offset of the section in the file. With this offset, we can
            compute the position of the RVA in the file
        """
        containing_section = self.get_section_of_rva(rva)

        in_section_offset = containing_section.PointerToRawData -\
            containing_section.VirtualAddress

        return in_section_offset + rva

    @cached_property
    def dir_export_table(self):
        export_header = list(self.optional_data_directories)[0]
        export_offset = self.resolve_rva(export_header.VirtualAddress)

        return Export_DirectoryTable(self.stream, export_offset, self)

    @property
    def dir_import_table(self):
        """
            import table is terminated by a all-null entry, so we have to
            check for that
        """
        import_header = list(self.optional_data_directories)[1]
        import_offset = self.resolve_rva(import_header.VirtualAddress)

        i = 0
        while True:
            offset = import_offset + i*Import_DirectoryTable.get_size()
            idt = Import_DirectoryTable(self.stream, offset, self)

            if idt.is_empty():
                break
            else:
                yield idt

            i += 1
