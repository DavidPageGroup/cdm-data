"""Working with event data, events, and event sequences"""

# Copyright (c) 2019 Aubrey Barnard.
#
# This is free, open software licensed under the [MIT License](
# https://choosealicense.com/licenses/mit/).


import csv
import itertools as itools
import json as _json
import operator

import esal

from . import records


# Data format


def header(time_type=float):
    """
    Return a header that describes the fields of an event record in a
    table of events.

    The header is (id:int, lo:time_type, hi:time_type, cat:str, typ:str,
    val:str, jsn:str).

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


# Facts and events


def value(event):
    """
    Return the value of an event that was constructed by `sequence`.
    """
    return event.value[0]


def json(event):
    """
    Parse the JSON of an event that was constructed by `sequence`.
    """
    jsn = event.value[1]
    return _json.loads(jsn) if isinstance(jsn, str) else jsn


# Event sequences


def sequence(
        event_records,
        event_sequence_id=None,
        header_nm2idx=header_nm2idx,
):
    """
    Construct an event sequence from the given records and return it.

    Any record in which the fields `lo` and `hi` are both `None` is
    treated as a fact.  All other records are treated as events.

    event_records:
        Iterable of event records where each record is an indexable
        collection of values.
    event_sequence_id:
        ID for constructed event sequence.
    header_nm2idx:
        Mapping of event record field names to their indices in the
        record.  Must include at least the following names: id, lo, hi,
        cat, typ, val, jsn.
    """
    # Unpack indices of event record fields
    id_idx = header_nm2idx['id']
    lo_idx = header_nm2idx['lo']
    hi_idx = header_nm2idx['hi']
    cat_idx = header_nm2idx['cat']
    typ_idx = header_nm2idx['typ']
    val_idx = header_nm2idx['val']
    jsn_idx = header_nm2idx['jsn']
    # Collect facts and events
    facts = []
    evs = []
    for ev_rec in event_records:
        # Fill in the ID if it hasn't been set
        if event_sequence_id is None:
            event_sequence_id = ev_rec[id_idx]
        # Get the event interval in order to distinguish between facts
        # and events
        lo = ev_rec[lo_idx]
        hi = ev_rec[hi_idx]
        # Missing times indicate a fact
        if lo is None and hi is None:
            fact = ((ev_rec[cat_idx], ev_rec[typ_idx]), ev_rec[val_idx])
            facts.append(fact)
        # Otherwise this record is an event
        else:
            ev = esal.Event(
                esal.Interval(ev_rec[lo_idx], ev_rec[hi_idx]),
                (ev_rec[cat_idx], ev_rec[typ_idx]),
                (ev_rec[val_idx], ev_rec[jsn_idx]))
            evs.append(ev)
    return esal.EventSequence(evs, facts, event_sequence_id)


def read_sequences(
        csv_event_records,
        header=header(),
        parse_id=None,
        include_ids=None,
        parse_record=None,
        include_record=None,
        transform_record=None,
        sequence_constructor=sequence,
):
    """
    Read event records and yield event sequences.

    csv_event_records:
        Iterable of list<str>, as from `csv.reader`.
    header:
        Indexable collection of (name, type) pairs indicating the names
        and data types of the fields of each record.  Must include at
        least the following names: id, lo, hi, cat, typ, val, jsn.
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
    sequence_constructor:
        Function to construct an event sequence given an iterable of
        event records and a sequence ID:
        sequence_constructor(iter<list<object>>, object) ->
        esal.EventSequence.
    """
    # Make mapping of header names to indices
    nm2idx = {field[0]: i for (i, field) in enumerate(header)}
    id_idx = nm2idx['id']
    # Make group-by function
    if parse_id is None:
        group_by = operator.itemgetter(id_idx)
    else:
        group_by = lambda rec: parse_id(rec[id_idx])
    # Loop to process each sequence of events that share the same ID
    for rec_id, group in itools.groupby(csv_event_records, group_by):
        # Process this sequence or skip it?
        if include_ids is None or rec_id in include_ids:
            # Assemble the event records into an event sequence
            yield sequence_constructor(records.process(
                group, parse_record, include_record, transform_record,
            ), rec_id)
