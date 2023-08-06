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


from prettytable import PrettyTable


class Header(PrettyTable):
    def __init__(self, COFF_header,
                 optional_standard_fields, optional_windows_fields):
        super(Header, self).__init__([
            "Header",
            "Field",
            "Value"
        ])

        self.add_coff_header(COFF_header)
        self.add_optional_standard(optional_standard_fields)
        self.add_optional_windows(optional_windows_fields)

    def add_coff_header(self, ch):
        self.add_row(["COFF", "Magic", hex(ch.Magic)])
        self.add_row(["COFF", "Machine", hex(ch.Machine)])
        self.add_row(["COFF", "NumberOfSections", ch.NumberOfSections])
        self.add_row(["COFF", "TimeDateStamp", ch.TimeDateStamp])
        self.add_row(["COFF", "PointerToSymbolTable", ch.NumberOfSymbols])
        self.add_row(["COFF", "SizeOfOptionalHeader", ch.SizeOfOptionalHeader])
        self.add_row(["COFF", "Characteristics", bin(ch.Characteristics)])

    def add_optional_standard(self, os):
        self.add_row(["Optional Standard", "Magic", hex(os.Magic)])
        self.add_row(["Optional Standard", "Linker Version",
                     "{0}.{1}".format(os.MajorLinkerVersion,
                                      os.MinorLinkerVersion)])

        self.add_row(["Optional Standard", "SizeOfCode", os.SizeOfCode])
        self.add_row(["Optional Standard", "SizeOfInitializedData",
                      os.SizeOfInitializedData])
        self.add_row(["Optional Standard", "SizeOfUninitializedData",
                      os.SizeOfUninitializedData])
        self.add_row(["Optional Standard", "AddressOfEntryPoint",
                      hex(os.AddressOfEntryPoint)])
        self.add_row(["Optional Standard", "BaseOfCode",
                      hex(os.BaseOfCode)])
        self.add_row(["Optional Standard", "BaseOfData",
                      hex(os.BaseOfData)])

    def add_optional_windows(self, ow):
        self.add_row(["Optional Windows", "ImageBase", hex(ow.ImageBase)])
        self.add_row(["Optional Windows", "SectionAlignment",
                      ow.SectionAlignment])
        self.add_row(["Optional Windows", "Operating System Version",
                      "{0}.{1}".format(ow.MajorOperatingSystemVersion,
                                       ow.MinorOperatingSystemVersion)])
        self.add_row(["Optional Windows", "Image Version",
                      "{0}.{1}".format(ow.MajorImageVersion,
                                       ow.MinorImageVersion)])
        self.add_row(["Optional Windows", "Subsystem Version",
                      "{0}.{1}".format(ow.MajorSubsystemVersion,
                                       ow.MinorSubsystemVersion)])
        self.add_row(["Optional Windows", "Win32VersionValue",
                      ow.Win32VersionValue])
        self.add_row(["Optional Windows", "SizeOfImage",
                      ow.SizeOfImage])
        self.add_row(["Optional Windows", "SizeOfHeaders",
                      ow.SizeOfHeaders])
        self.add_row(["Optional Windows", "CheckSum",
                      ow.CheckSum])
        self.add_row(["Optional Windows", "Subsystem",
                      ow.Subsystem])
        self.add_row(["Optional Windows", "DllCharacteristics",
                      bin(ow.DllCharacteristics)])
        self.add_row(["Optional Windows", "SizeOfStackReserve",
                      ow.SizeOfStackReserve])
        self.add_row(["Optional Windows", "SizeOfStackCommit",
                      ow.SizeOfStackCommit])
        self.add_row(["Optional Windows", "SizeOfHeapReserve",
                      ow.SizeOfHeapReserve])
        self.add_row(["Optional Windows", "SizeOfHeapCommit",
                      ow.SizeOfHeapCommit])
        self.add_row(["Optional Windows", "LoaderFlags",
                      bin(ow.LoaderFlags)])
        self.add_row(["Optional Windows", "NumberOfRvaAndSizes",
                      bin(ow.NumberOfRvaAndSizes)])


class Sections(PrettyTable):
    def __init__(self, section_headers):
        super(Sections, self).__init__([
            "Name",
            "VirtualSize",
            "VirtualAddress",
            "SizeOfRawData",
            "PointerToRawData",
            "PointerToRelocations",
            "PointerToLinenumbers",
            "NumberOfRelocations",
            "NumberOfLinenumbers",
            "Characteristics"
        ])

        for sh in section_headers:
            self.add_row(sh)

    def add_row(self, sh):
        super(Sections, self).add_row([
            sh.Name,
            sh.VirtualSize,
            hex(sh.VirtualAddress),
            sh.SizeOfRawData,
            hex(sh.PointerToRawData),
            hex(sh.PointerToRelocations),
            hex(sh.PointerToLinenumbers),
            sh.NumberOfRelocations,
            sh.NumberOfLinenumbers,
            bin(sh.Characteristics)
        ])


class Directories(PrettyTable):
    def __init__(self, directories):
        super(Directories, self).__init__([
            'Type',
            'VirtualAddress',
            'Size'
        ])

        for d in directories:
            self.add_row(d)

    def add_row(self, d):
        super(Directories, self).add_row([
            d.Type.name,
            hex(d.VirtualAddress),
            d.Size
        ])


class ImportTable(PrettyTable):
    def __init__(self, idt):
        super(ImportTable, self).__init__([
            "DLL",
            "Symbol"
        ])

        for dll in idt:
            for symbol in dll.get_imported_symbols():
                self.add_row(dll, symbol)

    def add_row(self, dll, s):
        super(ImportTable, self).add_row([
            dll.Name,
            s
        ])


class ExportTable(PrettyTable):
    def __init__(self, edt):
        super(ExportTable, self).__init__([
            "Symbol",
            "ExportRVA",
            "ForwarderRVA"
        ])

        for symbol in edt.get_symbols():
            self.add_row(symbol)

    def add_row(self, s):
        super(ExportTable, self).add_row([
            s[0],
            hex(s[1].ExportRVA),
            hex(s[1].ForwarderRVA)
        ])
