"""Working with event data and events"""

# Copyright (c) 2019 Aubrey Barnard.
#
# This is free, open software licensed under the [MIT License](
# https://choosealicense.com/licenses/mit/).


import csv
import itertools as itools
import operator

import esal

from . import records


# Data format


def header(time_type=float):
    """
    Return a header for a table of events.

    time_type:
        Constructor for type of time / date found in event records:
        time_type<T>(str) -> T.
    """
    return (
        ('id', int),
        ('lo', time_type),
        ('hi', time_type),
        ('cat', str),
        ('typ', str),
        ('val', str),
        ('jsn', str), # Do not automatically parse JSON
    )
header_nm2idx = {
    fld[0]: i for (i, fld) in enumerate(header())}


"""Format of CSV tables of events."""
csv_format = dict(
    delimiter='|',
    doublequote=False,
    escapechar='\\',
    lineterminator='\n',
    quotechar='"',
    quoting=csv.QUOTE_MINIMAL,
)


# Event sequences


def read_sequences(
        csv_event_records,
        header=header(),
        parse_id=None,
        include_ids=None,
        parse_record=None,
        include_record=None,
        transform_record=None,
):
    """
    Read event records and yield event sequences.

    csv_event_records:
        Iterable of list<str>, as from `csv.reader`.
    header:
        Indexable collection of (name, type) pairs indicating the names
        and data types of the fields of each record.  Must include the
        following names: id, lo, hi, cat, typ, val, jsn.
    parse_id:
        Function to parse the record ID: parse_id(str) -> object.
    include_ids:
        Set of IDs to include; all other IDs are excluded.  Use to
        short-circuit event record processing and event sequence
        construction.  Each ID is parsed before it is looked up.
    parse_record:
        Passed to `records.process`.
    include_record:
        Passed to `records.process`.
    transform_record:
        Passed to `records.process`.
    """
    # Make mapping of header names to indices
    nm2idx = {field[0]: i for (i, field) in enumerate(header)}
    id_idx = nm2idx['id']
    lo_idx = nm2idx['lo']
    hi_idx = nm2idx['hi']
    cat_idx = nm2idx['cat']
    typ_idx = nm2idx['typ']
    val_idx = nm2idx['val']
    jsn_idx = nm2idx['jsn']
    # Make group-by function
    if parse_id is None:
        group_by = operator.itemgetter(id_idx)
    else:
        group_by = lambda rec: parse_id(rec[id_idx])
    # Loop to process each sequence of events that share the same ID
    for rec_id, group in itools.groupby(csv_event_records, group_by):
        # Skip this sequence?
        if include_ids is not None and rec_id not in include_ids:
            continue
        # Collect facts and events
        facts = []
        evs = []
        for ev_rec in records.process(
                group, parse_record, include_record, transform_record):
            lo = ev_rec[lo_idx]
            hi = ev_rec[hi_idx]
            # Unlimited times indicates a fact
            if lo is None and hi is None:
                fact = ((ev_rec[cat_idx], ev_rec[typ_idx]),
                        ev_rec[val_idx])
                facts.append(fact)
            # Otherwise this record is an event
            else:
                ev = esal.Event(
                    esal.Interval(lo, hi),
                    (ev_rec[cat_idx], ev_rec[typ_idx]),
                    (ev_rec[val_idx], ev_rec[jsn_idx]))
                evs.append(ev)
        yield esal.EventSequence(evs, facts, rec_id)
