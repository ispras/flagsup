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
