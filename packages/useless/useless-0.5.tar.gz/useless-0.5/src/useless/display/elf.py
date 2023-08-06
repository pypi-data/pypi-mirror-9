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


class HeaderTable(PrettyTable):
    def __init__(self, elf_header):
        super(HeaderTable, self).__init__([
            'Type',
            'Machine',
            'Entry Point',
            'Program Header',
            'Section Header',
            "Flags"
        ])

        self.add_row(elf_header)

    def add_row(self, h):
        super(HeaderTable, self).add_row([
            h.e_type,
            h.e_machine,
            hex(h.e_entry),
            "offset: {0} entry size: {1} entries: {2}".format(
                hex(h.e_phoff), h.e_phentsize, h.e_phnum),
            "offset: {0} entry size: {1} entries: {2} strtab offset {3}"
            .format(hex(h.e_shoff), h.e_shentsize,
                    h.e_shnum, hex(h.e_shstrndx)),
            bin(h.e_flags)
        ])


class SectionsTable(PrettyTable):
    def __init__(self, sections):
        super(SectionsTable, self).__init__([
            'Name',
            'Type',
            'Flags',
            'Address',
            'Size',
            "Address Aligment",
            "Link"
        ])

        for s in sections:
            self.add_row(s)

    def add_row(self, s):
        super(SectionsTable, self).add_row([
            "offset: {0} value: {1}".format(hex(s.sh_name), s.name),
            s.sh_type.__repr__(),
            bin(s.sh_flags),
            "address: {0} offset {1}".format(hex(s.sh_addr), hex(s.sh_offset)),
            "size: {0} entry size {1}".format(s.sh_size, s.sh_entsize),
            s.sh_addralign,
            s.sh_link
        ])


class SymbolsTable(PrettyTable):
    def __init__(self, symbols):
        super(SymbolsTable, self).__init__([
            "Name",
            "Info",
            "Other",
            "Section Table Index",
            "Value",
            "Size"
        ])

        for s in symbols:
            self.add_row(s)

    def add_row(self, s):
        super(SymbolsTable, self).add_row([
            "offset: {0} value {1}".format(s.st_name, s.name),
            s.st_info,
            s.st_other,
            hex(s.st_shndx),
            hex(s.st_value),
            s.st_size
        ])
