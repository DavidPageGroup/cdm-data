"""Working with records and tabular data"""

# Copyright (c) 2019 Aubrey Barnard.
#
# This is free, open software licensed under the [MIT License](
# https://choosealicense.com/licenses/mit/).


import csv


def read(csv_file, csv_format, n_header_lines=0):
    """
    Read and yield records from the given CSV file.

    csv_file:
        Iterable of strings.
    csv_format:
        Dictionary of [CSV format parameters](
        https://docs.python.org/3/library/csv.html#dialects-and-formatting-parameters)
        to be passed to `csv.reader`.
    n_header_lines:
        Number of header lines to skip before yielding records.
    """
    csv_reader = csv.reader(csv_file, **csv_format)
    rec_iter = iter(csv_reader)
    # Skip any header
    for _ in range(n_header_lines):
        next(rec_iter)
    return rec_iter


def mk_parser(header, null_values=('',)):
    """
    Return a function that will parse a record according to the given
    header.

    header:
        Indexable collection of (name, parse_type) pairs where
        parse_type<T>(str) -> T parses a string into a value of the
        desired type.
    null_values:
        Set of unparsed values to replace with None instead of parsing.
    """
    hdr_len = len(header)
    def parse_record(record):
        return [(parse(text) if text not in null_values else None)
                for ((_, parse), text) in zip(header, record)]
    return parse_record

# header = list(zip(string.ascii_lowercase, (int, datetime.date.fromisoformat, datetime.date.fromisoformat, str, str, int, float, float)))
# raw_record = ['123456789', '2013-11-13', '2019-04-30', 'cluster', 'penumbra', '987654321', '1.23456789', '9.87654321']
# timeit.timeit(setup='prsr = data.mk_record_parser(header)', stmt='prsr(raw_record)', globals=globals())
