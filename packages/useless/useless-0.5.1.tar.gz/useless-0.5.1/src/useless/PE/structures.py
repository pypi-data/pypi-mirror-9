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
from ..common.structures import *
from ..common import parse_cstring
from cached_property import cached_property


class COFF_Header(Structure):
    Magic = PE_DWord
    Machine = PE_Word
    NumberOfSections = PE_Word
    TimeDateStamp = PE_DWord
    PointerToSymbolTable = PE_DWord
    NumberOfSymbols = PE_DWord
    SizeOfOptionalHeader = PE_Word
    Characteristics = PE_Word


class OptionalHeader_StandardFields(Structure):
    Magic = PE_Word
    MajorLinkerVersion = PE_Char
    MinorLinkerVersion = PE_Char
    SizeOfCode = PE_DWord
    SizeOfInitializedData = PE_DWord
    SizeOfUninitializedData = PE_DWord
    AddressOfEntryPoint = PE_DWord
    BaseOfCode = PE_DWord
    BaseOfData = PE_DWord


class OptionalHeader_WindowsFields(Structure):
    ImageBase = PE_DWord
    SectionAlignment = PE_DWord
    FileAlignment = PE_DWord
    MajorOperatingSystemVersion = PE_Word
    MinorOperatingSystemVersion = PE_Word
    MajorImageVersion = PE_Word
    MinorImageVersion = PE_Word
    MajorSubsystemVersion = PE_Word
    MinorSubsystemVersion = PE_Word
    Win32VersionValue = PE_DWord
    SizeOfImage = PE_DWord
    SizeOfHeaders = PE_DWord
    CheckSum = PE_DWord
    Subsystem = PE_Word
    DllCharacteristics = PE_Word
    SizeOfStackReserve = PE_DWord
    SizeOfStackCommit = PE_DWord
    SizeOfHeapReserve = PE_DWord
    SizeOfHeapCommit = PE_DWord
    LoaderFlags = PE_DWord
    NumberOfRvaAndSizes = PE_DWord


class OptionalHeader_DataDirectory(Structure):
    VirtualAddress = PE_DWord
    Size = PE_DWord

    def __init__(self, stream, offset, num):
        super(OptionalHeader_DataDirectory, self).__init__(stream, offset)
        self.Type = DirectoryType(num)

    def is_empty(self):
        return (self.VirtualAddress == 0) and (self.Size == 0)


class Section_Header(Structure):
    Name = PE_NameField
    VirtualSize = PE_DWord
    VirtualAddress = PE_DWord
    SizeOfRawData = PE_DWord
    PointerToRawData = PE_DWord
    PointerToRelocations = PE_DWord
    PointerToLinenumbers = PE_DWord
    NumberOfRelocations = PE_Word
    NumberOfLinenumbers = PE_Word
    Characteristics = PE_DWord


class Export_DirectoryTable(Structure):
    ExportFlags = PE_DWord
    TimeDateStamp = PE_DWord
    MajorVersion = PE_Word
    MinorVersion = PE_Word
    NameRVA = PE_DWord
    OrdinalBase = PE_DWord
    AddressTableEntries = PE_DWord
    NumberOfNamePointers = PE_DWord
    ExportAddressTableRVA = PE_DWord
    NamePointerRVA = PE_DWord
    OrdinalTableRVA = PE_DWord

    def __init__(self, stream, offset, pe):
        self.pe = pe
        super(Export_DirectoryTable, self).__init__(stream, offset)

    @cached_property
    def Name(self):
        return parse_cstring(self.stream, self.pe.resolve_rva(self.NameRVA))

    def get_symbols(self):
        for i in range(0, self.NumberOfNamePointers):
            self.stream.seek(self.pe.resolve_rva(self.NamePointerRVA)+4*i)
            name_rva = PE_DWord.parse(self.stream)
            name = parse_cstring(self.stream, self.pe.resolve_rva(name_rva))

            self.stream.seek(self.pe.resolve_rva(self.OrdinalTableRVA+2*i))
            ordinal = PE_Word.parse(self.stream)

            eat_offset = self.pe.resolve_rva(self.ExportAddressTableRVA)\
                + 8*ordinal
            eat = Export_AddressTable(self.stream, eat_offset)

            yield(name, eat)


class Export_AddressTable(Structure):
    ExportRVA = PE_DWord
    ForwarderRVA = PE_DWord


class Import_DirectoryTable(Structure):
    ImportLookupTableRVA = PE_DWord
    TimeDateStamp = PE_DWord
    ForwarderChain = PE_DWord
    NameRVA = PE_DWord
    ImportAddressTableRVA = PE_DWord

    def __init__(self, stream, offset, pe):
        self.pe = pe
        super(Import_DirectoryTable, self).__init__(stream, offset)

    def is_empty(self):
        return not any([getattr(self, x) != 0
                        for x in self.get_fields_names()])

    @cached_property
    def Name(self):
        return parse_cstring(self.stream, self.pe.resolve_rva(self.NameRVA))

    def get_import_lookup_table(self):
        ilt_offset = self.pe.resolve_rva(self.ImportLookupTableRVA)

        self.stream.seek(ilt_offset)
        i = 0
        while True:
            # we do the seek everytime because this is an iterator
            self.stream.seek(ilt_offset + i*PE_DWord.length)
            ilt_entry = PE_DWord.parse(self.stream)
            i += 1

            if(ilt_entry == 0):
                break
            else:
                yield ilt_entry

    def resolve_import_lookup_entry(self, il):
        ORDINAL_NAME_MASK = 0x80000000
        ORDINAL_MASK = 0xffff

        if (il & ORDINAL_NAME_MASK) > 0:
            # ordinal
            return il & ORDINAL_MASK
        else:
            return parse_cstring(self.stream, self.pe.resolve_rva(il) + 2)

    def get_imported_symbols(self):
        for il in self.get_import_lookup_table():
            yield self.resolve_import_lookup_entry(il)
