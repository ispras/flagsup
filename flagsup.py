#!/usr/bin/env python3

import sys
from itertools import count

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
                    producer = die.attributes['DW_AT_producer'].value
                    if producer not in flag_sets:
                        flag_sets[producer] = {}
                    if comp_dir not in flag_sets[producer]:
                        flag_sets[producer][comp_dir] = set()
                    flag_sets[producer][comp_dir].add(die.get_full_path())
                except KeyError:
                    pass

# XXX: perhaps flag_sets should become an object with fields and mehtods...
def n_cus(producer):
    global flag_sets
    return sum(len(flag_sets[producer][paths]) for paths in flag_sets[producer])

flag_sets = {} # producer -> (comp_dir -> set(full_paths))

process_file(sys.argv[1])

producers = sorted(flag_sets, key=n_cus, reverse=True)

canonical = producers[0]
print('Canonical compile string (%d compile units): \n%s' %
      (n_cus(canonical), canonical))
print('compile dirs (units):')
for comp_dir in flag_sets[canonical]:
    print("\t%s (%d)" % (comp_dir, len(flag_sets[canonical][comp_dir])))
print()

for producer,i in zip(producers[1:], count(start=2)):
    print("Diff for flag set %d (%d compile units):" % (i, n_cus(producer)))
    print("+++:", b" ".join(sorted(set(producer.split()) - set(canonical.split()))))
    print("---:", b" ".join(sorted(set(canonical.split()) - set(producer.split()))))
    print('compile dirs (units):')
    for comp_dir in flag_sets[producer]:
        print("\t%s (%d)" % (comp_dir, len(flag_sets[producer][comp_dir])))
    print()
