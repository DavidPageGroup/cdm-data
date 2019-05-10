"""Working with records and tabular data"""

# Copyright (c) 2019 Aubrey Barnard.
#
# This is free, open software licensed under the [MIT License](
# https://choosealicense.com/licenses/mit/).


import csv

from . import core


@core.deprecated(
    '`cdmdata.records.read` is deprecated and will be removed in v0.3.  ' # TODO
    'Use `read_csv` instead.')
def read(csv_file, csv_format, n_header_lines=0):
    """
    Read records from the given CSV file.  Return an iterable of
    records.

    csv_file: Iterable<str>
    csv_format: dict<str, object>
        Dictionary of [CSV format parameters](
        https://docs.python.org/3/library/csv.html#dialects-and-formatting-parameters)
        to be passed to `csv.reader`.
    n_header_lines: int
        Number of header lines to skip before returning records.
    """
    records = csv.reader(csv_file, **csv_format)
    # Skip any header, but do so safely in case there are not enough
    # lines
    for _ in range(n_header_lines):
        rec = next(records, None)
        if rec is None:
            break
    return records


@core.deprecated(
    '`cdmdata.records.load` is deprecated and will be removed in v0.3.  ' # TODO
    'Use `read_csv` instead.')
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


def read_csv(
        csv_filename,
        csv_format,
        header,
        detect_header=True,
        include_record=None,
        transform_record=None,
):
    """
    Read and yield records from the given CSV file.

    Opens the file, reads records according to the given CSV format,
    parses the records according to the given header, optionally filters
    and transforms the records, and closes the file.

    csv_filename:
        Passed to `core.open`.
    csv_format: dict<str, object>
        Dictionary of [CSV format parameters](
        https://docs.python.org/3/library/csv.html#dialects-and-formatting-parameters)
        to be passed to `csv.reader`.
    header:
        Sequence of (name, type) pairs that describe the columns of the
        CSV.  Passed to `mk_parser`.
    detect_header: bool | function(int, list<str>)->bool
        Whether and how to detect records in the file that are part of
        its header.  If `True`, use the field names in the given header
        to make a detector function.  If a detector function, apply it
        successively to each (record-index, record) pair from the top of
        the file and discard each such record until it returns `False`.
        (This will have to do until someone implements a rewindable
        stream that can be used with the CSV sniffer.)
    include_record:
        Passed to `process`.
    transform_record:
        Passed to `process`.
    """
    # Create a function to parse each row
    parser = mk_parser(header)
    # Use or make detector for header if requested
    is_header = None
    if callable(detect_header):
        is_header = detect_header
    elif detect_header is True:
        is_header = is_header_if_has_fields(*(f[0] for f in header))
    # Open the file or stream
    with core.open(csv_filename, 'rt') as file:
        # Read records from the CSV.  `csv.reader` is its own iterator,
        # so no need to call `iter` on it.
        records = csv.reader(file, **csv_format)
        # Skip the header (if any) if desired
        if is_header is not None:
            rec = None
            for idx, rec in enumerate(records):
                if not is_header(idx, rec):
                    break
                # Discard the record if it is part of the header
                rec = None
            # Process the first non-header record.  This must be done
            # separately unless the implementation is changed to use a
            # pushback iterator, which is much costlier over many
            # records than just doing one more call to `process`.
            if rec is not None:
                yield from process(
                    (rec,), parser, include_record, transform_record)
        # Process all the records and yield them
        yield from process(
            records, parser, include_record, transform_record)


def is_header_if_first_n_lines(n_header_lines=0):
    """
    Return a header detector function that considers the first N lines
    of a CSV file to be the header.
    """
    def is_header(index, record):
        return index < n_header_lines
    return is_header


def is_header_if_has_fields(*fields):
    """
    Return a header detector function that considers a record to be part
    of the CSV header if it matches the given fields.

    fields: tuple<str>
        Strings that are expected to be among the fields of any records
        in the CSV header.
    """
    fields = set(fields)
    def is_header(index, record):
        return fields <= set(record)
    return is_header


def mk_parser(header, null_values=('',)):
    """
    Return a function that will parse a record according to the given
    header.

    header: Sequence<(str, function<T>(str)->T)>
        Indexable collection of (name, func) pairs where the function
        parses a string into a value of the desired type.
    null_values: Collection<str>
        Set of unparsed values to replace with `None` instead of
        parsing.
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

    records: Iterable<list<str>>
    parse_record: function(list<str>)->list<object>
        Function to convert the text fields of each record into usable
        values.
    include_record: function(list<object>)->bool
        Predicate that returns whether a record should be included or
        discarded.  Applied after parsing a record.
    transform_record: function(list<object>)->list<object>
        Function to transform a record before it is converted into an
        event.  Applied after including / discarding records.
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
