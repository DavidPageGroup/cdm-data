Cleaned, Sorted, and Compressed Data
====================================


Contents
--------

The files in this directory are those in the base directory except that
they have been sorted by (only) study ID and compressed.  The goal of
sorting is to make files of this size processable by subject ID without
loading the whole file into memory and without needing a database.  The
goal of compression is to make the files much quicker to load.  (The CPU
time needed for decompression will be less than the time needed to read
the uncompressed file from disk or from over the network.)

Note that XZ compression is well-supported these days: `less` can
natively read XZ-compressed files and Python can read XZ-compressed
files using the `lzma` module (since Python 3.3, 2012).  If your `less`
is older, you may need to use `xzless` instead.  For other purposes,
there are XZ-aware versions of common command line tools available,
e.g. `xzcat`, `xzgrep`, `xzdiff`, etc.  Of course, there is always
`xzcat <file> | ...`.

The same goes for LZ4 support.  Just be sure to use `lz4*` tools, not
`lz*`.  Also, there is no LZ4 support in the Python standard library.

The details of the data processing are in `clean_sort_compress_data.sh`.

Comparison of compression algorithms can be found at
https://catchchallenger.first-world.info/wiki/Quick_Benchmark:_Gzip_vs_Bzip2_vs_LZMA_vs_XZ_vs_LZ4_vs_LZO
and
https://www.rootusers.com/gzip-vs-bzip2-vs-xz-performance-comparison/.


Formats
-------

The files `*_raw_data.csv.xz` appear to have properly quoted fields
using double quotes.  The file `omop_drug_exposure.csv.xz` has fields
that contain double quotes which are not themselves quoted or escaped,
and so should be treated as "literal" CSV: no quoting and no escaping.
You can verify these conclusions by inspecting the lines with double
quotes in the files `*.dblqts`.

My general conclusion is to treat all the medication periods files as
CSV with quoting and all the OMOP files as literal CSV.  But anything
that agrees with the lines in `*.dblqts` is safe.

The precise formats of the files are described in `tables.yaml`.


-----

Copyright (c) 2018 Aubrey Barnard.  This is free software released under
the MIT License.  See `LICENSE.txt` for details.
