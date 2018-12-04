# Purpose and usage

**flagsup** is a compiler flags extractor and summarizer.  It answers the
question "what flags were up?"—during compilation that is—and presents a summary
in a comprehensible way.  It takes a linked ELF file with DWARF debug
information (or just a separate debug info file) as input.

The tool is useful for e.g. big statically linked programs incorporating
multiple independently developed libraries, especially if different build
systems are used to produce them.  The user of the tool can easily check whether
a desired compiler flag is uniformly propagated, see exactly which libraries and
translation units are built with a particular set of flags, and how flag sets
used for compilation of different subsystems differ.

**flagsup** has 2 modes: with and without the `--full` option.  The output
format is meant for humans and strives to be self-explanatory.

# Dependencies

- python 3.x
- [pyelftools](https://github.com/eliben/pyelftools)

# Example output

Here is the ouptut of flagsup (run without the `--full` switch) on a debug
build of the GNU C compiler executable (`cc1`).

```
Canonical compile string (434 compile units):
GNU C++14 8.2.1 20180831 -mtune=generic -march=x86-64 -g3 -O0 -fno-PIE -fno-exceptions -fno-rtti -fasynchronous-unwind-tables
compile dirs (units):
	/mnt/bld/gcc-trunk/gcc (434)

Diff for flag set 2 (41 compile units):
- C++14 -g3 -fno-rtti -fno-exceptions -fno-PIE -fasynchronous-unwind-tables -O0
+ C17 -g -O2
compile dirs (units):
	/mnt/bld/gcc-trunk/libiberty (33)
	/mnt/bld/gcc-trunk/zlib (8)

Diff for flag set 3 (15 compile units):
- -fno-PIE -fasynchronous-unwind-tables
+
compile dirs (units):
	/mnt/bld/gcc-trunk/libcpp (15)

Diff for flag set 4 (5 compile units):
- C++14 -g3 -fno-rtti -fno-exceptions -fno-PIE -fasynchronous-unwind-tables -O0
+ C17 -g -fno-lto -O2
compile dirs (units):
	/mnt/bld/gcc-trunk/libdecnumber (5)

Diff for flag set 5 (1 compile units):
- C++14 -g3 -fno-rtti -fno-exceptions -fno-PIE -fasynchronous-unwind-tables -O0
+ C17 -g -funwind-tables -frandom-seed=state.lo -fPIC -O2
compile dirs (units):
	/mnt/bld/gcc-trunk/libbacktrace (1)

Diff for flag set 6 (1 compile units):
- C++14 -g3 -fno-rtti -fno-exceptions -fno-PIE -fasynchronous-unwind-tables -O0
+ C17 -g -funwind-tables -frandom-seed=backtrace.lo -fPIC -O2
compile dirs (units):
	/mnt/bld/gcc-trunk/libbacktrace (1)

  ...

```

# Implementation details

The tool is written in Python3 though it would not be hard to support Python2 as
well, shall it be needed.

For proper parsing of DWARF structures **flagsup** relies on the
[**pyelftools**](https://github.com/eliben/pyelftools) library.  Specifically,
it looks at the values of `DW_AT_producer` and `DW_AT_comp_dir` attributes to
infer with what compiler and compiler options a particular translation unit was
compiled with and what the working directory was at the time.

Some heuristics are needed to keep the output readable and useful.  From the
DWARF sections we gather information on what tool and what flags were used to
compile each translation unit.  How do we make all of it available to the user
without overwhelming them?  In short, we group the information and show diffs
instead of printing all the flag sets verbatim.  Translation units are grouped
by the flag set.  Inside one flag set, entries are grouped (in `--full` mode; in
the abbreviated output only their number is shown) by `DW_AT_comp_dir` which is
a fairly good approximation of per-library grouping.  The observation behind
this is that the entire library is usually built with a consistent set of flags.
Another trick is the diffs.  We speculate that the flag sets are mostly uniform,
with some deviations.  Therefore it makes sense to compare all the flag sets
against the most frequent ("canonical") producer.  (Comparing all the flag sets
with one another would produce O(n^2) output entries and defeat the purpose of
diffing.)
