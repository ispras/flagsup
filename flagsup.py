#!/usr/bin/env python3

import sys
import re
from collections import defaultdict

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
                comp_dir_obj = die.attributes.get('DW_AT_comp_dir')
                producer_obj = die.attributes.get('DW_AT_producer')
                if not comp_dir_obj or not producer_obj:
                    continue
                comp_dir = comp_dir_obj.value.decode()
                producer = producer_obj.value.decode()
                flag_sets.setdefault(producer, defaultdict(set))
                flag_sets[producer][comp_dir].add(die.get_full_path())

# XXX: perhaps flag_sets should become an object with fields and mehtods...
def n_cus(producer):
    global flag_sets
    return sum(len(flag_sets[producer][paths]) for paths in flag_sets[producer])

def print_comp_dirs(flag_str, full):
    print('compile dirs (units):')
    for comp_dir in flag_sets[flag_str]:
        print("\t%s (%d)" % (comp_dir, len(flag_sets[flag_str][comp_dir])))
        if full:
            for cu in sorted(flag_sets[flag_str][comp_dir]):
                print("\t\t%s" % cu)
    print()

param_with_arg = re.compile('--param\s+\S+')

def param_split(flag_str):
    """Split a flag string, glueing "--param" to its argument."""
    return (re.findall(param_with_arg, flag_str) +
            re.sub(param_with_arg, '', flag_str).split())

def diff_flagsets(flag_str1, flag_str2):
    return " ".join(sorted(set(param_split(flag_str1)) -
                           set(param_split(flag_str2)),
                           reverse=True))

flag_sets = {} # producer -> (comp_dir -> set(full_paths))

if sys.argv[1] in ("-f", "--full", "-v", "--verbose"):
    full = True
    infile = sys.argv[2]
else:
    full = False
    infile = sys.argv[1]

process_file(infile)

producers = sorted(flag_sets, key=n_cus, reverse=True)

if len(producers) < 1:
    print('%s: no DW_AT_producer strings found in `%s`.'
          % (sys.argv[0], infile), 'Make sure the file has debug information.')
    exit(1)
canonical = producers[0]
print('Canonical compile string (%d compile units): \n%s' %
      (n_cus(canonical), canonical))
print_comp_dirs(canonical, full)

for i, producer in enumerate(producers[1:], start=2):
    print("Diff for flag set %d (%d compile units):" % (i, n_cus(producer)))
    if full:
        print("---", canonical)
        print("+++", producer)
        print("delta:")
    print("-", diff_flagsets(canonical, producer))
    print("+", diff_flagsets(producer, canonical))
    print_comp_dirs(producer, full)
