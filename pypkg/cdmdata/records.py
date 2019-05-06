"""Working with records and tabular data"""

# Copyright (c) 2019 Aubrey Barnard.
#
# This is free, open software licensed under the [MIT License](
# https://choosealicense.com/licenses/mit/).


import csv

from . import core


def read(csv_file, csv_format, n_header_lines=0):
    """
    Read records from the given CSV file.  Return an iterable of
    records.

    csv_file:
        Iterable of strings.
    csv_format:
        Dictionary of [CSV format parameters](
        https://docs.python.org/3/library/csv.html#dialects-and-formatting-parameters)
        to be passed to `csv.reader`.
    n_header_lines:
        Number of header lines to skip before returning records.
    """
    csv_reader = csv.reader(csv_file, **csv_format)
    records = iter(csv_reader)
    # Skip any header
    for _ in range(n_header_lines):
        next(records)
    return records


def load(
        csv_filename,
        csv_format,
        header,
        n_header_lines=1,
        include_record=None,
        transform_record=None,
):
    """
    Read and yield records from the given CSV file.

    Convenience wrapper for `read` that opens (and closes) the file,
    parses the records, and optionally filters and transforms them.

    csv_filename:
        Anything that can be turned into an open file by `core.open`.
    csv_format:
        Passed to `read`.
    header:
        Passed to `mk_parser`.
    n_header_lines:
        Passed to `read`.
    include_record:
        Passed to `process`.
    transform_record:
        Passed to `process`.
    """
    parser = mk_parser(header)
    with core.open(csv_filename, 'rt') as file:
        yield from process(read(file, csv_format, n_header_lines),
                           parser, include_record, transform_record)


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


def process(
        records,
        parse_record=None,
        include_record=None,
        transform_record=None,
):
    """
    Create a pipeline that optionally parses, filters, and transforms
    the given records.  Return an iterable of records.

    records:
        Iterable of list<str>.
    parse_record:
        Function to convert the text fields of each record into usable
        values: parse_record(list<str>) -> list<object>.
    include_record:
        Predicate that returns whether a record should be included or
        discarded: include_record(list<object>) -> bool.  Applied after
        parsing a record.
    transform_record:
        Function to transform a record before it is converted into an
        event: transform_record(list<object>) -> list<object>.  Applied
        after including / discarding records.
    """
    # Parse records if requested
    if parse_record is not None:
        records = map(parse_record, records)
    # Filter records if requested
    if include_record is not None:
        records = filter(include_record, records)
    # Transform records if requested
    if transform_record is not None:
        records = map(transform_record, records)
    return records
