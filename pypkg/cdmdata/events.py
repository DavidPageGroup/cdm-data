"""Working with event data and events"""

# Copyright (c) 2019 Aubrey Barnard.
#
# This is free, open software licensed under the [MIT License](
# https://choosealicense.com/licenses/mit/).


import csv
import itertools as itools
import json as _json
import operator

import esal


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


csv_format = dict(
    delimiter='|',
    doublequote=False,
    escapechar='\\',
    lineterminator='\n',
    quotechar='"',
    quoting=csv.QUOTE_MINIMAL,
)


# Facts and events


def mk_fact_constructor(header_nm2idx):
    """
    Make and return a function that constructs a fact from an event
    record using the given header.

    The returned function constructs the key and value of a fact as
    ((cat, typ), val).
    """
    cat_idx = header_nm2idx['cat']
    typ_idx = header_nm2idx['typ']
    val_idx = header_nm2idx['val']
    def fact_constructor(event_record):
        return ((event_record[cat_idx], event_record[typ_idx]),
                event_record[val_idx])
    return fact_constructor


def mk_event_constructor(header_nm2idx):
    """
    Make and return a function that constructs an event from an event
    record using the given header.

    The returned function constructs an event where the event time is
    the interval •(lo, hi)•, the event type is (cat, typ), and the event
    value is (val, jsn).
    """
    lo_idx = header_nm2idx['lo']
    hi_idx = header_nm2idx['hi']
    cat_idx = header_nm2idx['cat']
    typ_idx = header_nm2idx['typ']
    val_idx = header_nm2idx['val']
    jsn_idx = header_nm2idx['jsn']
    def event_constructor(event_record):
        return esal.Event(
            esal.Interval(event_record[lo_idx], event_record[hi_idx]),
            (event_record[cat_idx], event_record[typ_idx]),
            (event_record[val_idx], event_record[jsn_idx]))
    return event_constructor


def value(event):
    """
    Return the value of an event that was constructed by
    `event_constructor`.
    """
    return event.value[0]


def json(event):
    """
    Parse the JSON of an event that was constructed by
    `event_constructor`.
    """
    jsn = event.value[1]
    return _json.loads(jsn) if isinstance(jsn, str) else jsn


# Event sequences


def sequence(
        event_records,
        ev_seq_id=None,
        header_nm2idx=header_nm2idx,
        fact_constructor=None,
        event_constructor=None,
):
    """
    Construct an event sequence from the given records and return it.

    Any record in which the fields `lo` and `hi` are both `None` is
    treated as a fact.  All other records are treated as events.

    event_records:
        Iterable of event records where each record is an indexable
        collection of values.
    header_nm2idx:
        Mapping of event record field names to their indices in the
        record.  Must include at least the following names: id, lo, hi,
        cat, typ, val, jsn.
    fact_constructor:
        Function to construct a fact from an event record:
        fact_constructor(event_record) -> (key, value).  If `None`, call
        `mk_fact_constructor(header_nm2idx)`.
    event_constructor:
        Function to construct an event from an event record:
        event_constructor(event_record) -> esal.Event.  If `None`, call
        `mk_event_constructor(header_nm2idx)`.
    """
    # Make constructors if needed
    if fact_constructor is None:
        fact_constructor = mk_fact_constructor(header_nm2idx)
    if event_constructor is None:
        event_constructor = mk_event_constructor(header_nm2idx)
    # Unpack indices of event record fields
    id_idx = header_nm2idx['id']
    lo_idx = header_nm2idx['lo']
    hi_idx = header_nm2idx['hi']
    # Collect facts and events
    facts = []
    evs = []
    for ev_rec in event_records:
        # Fill in the ID if it hasn't been set
        if ev_seq_id is None:
            ev_seq_id = ev_rec[id_idx]
        # Get the event interval in order to distinguish between facts
        # and events
        lo = ev_rec[lo_idx]
        hi = ev_rec[hi_idx]
        # Missing times indicate a fact
        if lo is None and hi is None:
            fact = fact_constructor(ev_rec)
            facts.append(fact)
        # Otherwise this record is an event
        else:
            ev = event_constructor(ev_rec)
            evs.append(ev)
    return esal.EventSequence(evs, facts, ev_seq_id)


def mk_sequence_constructor(
        header_nm2idx=header_nm2idx,
        fact_constructor=None,
        event_constructor=None,
):
    """
    Make and return a closure of `sequence` that binds the given
    arguments, leaving `event_records` and `ev_seq_id` unbound.

    Makes `fact_constructor` and `event_constructor` as needed using the
    corresponding `mk_*_constructor` functions.
    """
    # Make fact or event constructors if needed
    if fact_constructor is None:
        fact_constructor = mk_fact_constructor(header_nm2idx)
    if event_constructor is None:
        event_constructor = mk_event_constructor(header_nm2idx)
    def sequence_constructor(event_records, ev_seq_id=None):
        return sequence(event_records, ev_seq_id, header_nm2idx,
                        fact_constructor, event_constructor)


def read_sequences(
        csv_event_records,
        header=header(),
        parse_id=None,
        include_ids=None,
        parse_record=None,
        include_record=None,
        transform_record=None,
        sequence_constructor=None,
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
    sequence_constructor:
        Function to construct an event sequence given an iterable of
        event records and a sequence ID:
        sequence_constructor(iter<list<object>>, int) ->
        esal.EventSequence.
    """
    # Make mapping of header names to indices
    nm2idx = {field[0]: i for (i, field) in enumerate(header)}
    id_idx = nm2idx['id']
    # Make sequence constructor if needed
    if sequence_constructor is None:
        sequence_constructor = mk_sequence_constructor(nm2idx)
    # Make group-by function
    if parse_id is None:
        group_by = operator.itemgetter(id_idx)
    else:
        group_by = lambda rec: parse_id(rec[id_idx])
    # Make event record processing pipeline
    def process_event_records(ev_recs):
        # Parse the records
        if parse_record is not None:
            ev_recs = map(parse_record, ev_recs)
        # Filter the records
        if include_record is not None:
            ev_recs = filter(include_record, ev_recs)
        # Transform the records
        if transform_record is not None:
            ev_recs = map(transform_record, ev_recs)
        return ev_recs
    # Loop to process each sequence of events that share the same ID
    for rec_id, group in itools.groupby(csv_event_records, group_by):
        # Process this sequence or skip it?
        if include_ids is None or rec_id in include_ids:
            # Assemble the event records into an event sequence
            yield sequence_constructor(
                process_event_records(group), rec_id)
