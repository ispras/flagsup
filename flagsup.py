#!/usr/bin/env python3

import sys

from elftools.elf.elffile import ELFFile

def process_file(filename):
    global flag_sets

    with open(filename, 'rb') as f:
        elffile = ELFFile(f)

        if not elffile.has_dwarf_info():
            print('File has no DWARF info.')
            return

        dwarfinfo = elffile.get_dwarf_info()

        for cu in dwarfinfo.iter_CUs(): # compile unit
            for die in cu.iter_DIEs(): # debugging information entry
                try:
                    comp_dir = die.attributes['DW_AT_comp_dir'].value
                    if comp_dir not in flag_sets:
                        flag_sets[comp_dir] = {}
                    producer = die.attributes['DW_AT_producer'].value
                    if producer not in flag_sets[comp_dir]:
                        flag_sets[comp_dir][producer] = []
                    flag_sets[comp_dir][producer] += [die.get_full_path()]
                except KeyError:
                    pass

flag_sets = {} # comp_dir -> (producer -> [full_paths])

process_file(sys.argv[1])

for comp_dir in flag_sets:
    for producer in flag_sets[comp_dir]:
        print ("%s : %d" % (producer, len(flag_sets[comp_dir][producer])))
