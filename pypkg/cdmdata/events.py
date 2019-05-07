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


def periods(
        events,
        span_lo=None,
        span_hi=None,
        value=None,
        zero_values=(0, None),
        min_len=0,
        backoff=0,
        output_zero=0,
):
    """
    Yield disjoint intervals corresponding to different values of the
    given events.

    Converts a sequence of events that approximately represent a signal
    into a guess at the underlying piecewise constant signal (a sequence
    of intervals that partitions a span of time, where each interval has
    a value).  Assumes the given events are sorted by their start times.
    The conversion gives each interval a minimum length, unions
    intervals with the same value and then puts them in sequence by
    truncating an interval at the start of the next interval with a
    different, nonzero value (with optional back-off).  Finally, fills
    in gaps with zero values.  This is intended to be useful for
    constructing event "eras" where the values of an event are mutually
    exclusive (e.g. different dosages of a medication).

    For example, in the following, the top collection of intervals would
    be converted into the bottom sequence of intervals given min_len=6
    and backoff=2.

    --------------------------------------------------
                      222  22
       11111  111 11111                  11 11111
    00000                 00000 000000
    --------------------------------------------------
    00 111111 1111111 22222222222 000000 111111111 000
    --------------------------------------------------

    events:
        Iterable of events.
    span_lo:
        Start (if any) of span to which events are clipped.
    span_hi:
        End (if any) of span to which events are clipped.
    value:
        Function to extract values from events: value(event) -> object.
        Default uses `esal.Event.value`.
    zero_values:
        Set of values to treat as zero (non-signal) and ignore.
    min_len:
        Minimum length of each interval (prior to any truncation).
    backoff:
        Size of gap between intervals.  A larger gap increases the
        chances that an underlying transition from one value to the next
        happened in the gap.
        [TODO technically also need a starting lag / offset]
    output_zero:
        Value to use when filling in between nonzero values.
    """
    prds = []
    # Lengthen and clip nonzero periods
    for ev in events:
        # Ensure a minimum length before clipping
        lo = ev.when.lo
        hi = max(ev.when.hi, lo + min_len)
        val = value(ev) if value is not None else ev.value
        # Discard any events that are "non-events" (have zero value) or
        # that are outside the allowed span
        if (val in zero_values or
            (span_lo is not None and hi < span_lo) or
            (span_hi is not None and lo > span_hi)):
            continue
        # Clip to allowed span
        if span_hi is not None:
            hi = min(hi, span_hi)
        if span_lo is not None:
            lo = max(lo, span_lo)
        prds.append((lo, hi, val))
    # Merge and sequentialize periods
    mrg_idx = 0
    prd_idx = 1
    while prd_idx < len(prds):
        lo1, hi1, val1 = prds[mrg_idx]
        lo2, hi2, val2 = prds[prd_idx]
        # Merge periods with the same value
        if hi1 >= lo2 and val1 == val2:
            prds[mrg_idx] = (lo1, hi2, val1)
            del prds[prd_idx]
        else:
            # Put periods in sequence by removing overlaps
            if hi1 > lo2:
                prds[mrg_idx] = (lo1, lo2, val1)
            mrg_idx += 1
            prd_idx += 1
    # Yield periods with intervening zero periods as needed.  Separate
    # periods by backing off from the following nonzero event (if there
    # is one).
    zero_lo = span_lo
    for (idx, (lo, hi, val)) in enumerate(prds):
        # Yield a preceding zero period if it would be non-empty after
        # backing off from the current event
        zero_hi = lo - backoff
        if zero_lo < zero_hi:
            yield (esal.Interval(zero_lo, zero_hi), output_zero)
        # Back off from the following nonzero event if there is one
        hi_bk = (max(min(hi, prds[idx + 1][0] - backoff), lo)
                 if idx + 1 < len(prds)
                 else hi)
        yield (esal.Interval(lo, hi_bk), val)
        # Increment.  Delay the zero period by the backoff amount.
        zero_lo = hi_bk + backoff
    if zero_lo < span_hi:
        yield (esal.Interval(zero_lo, span_hi), output_zero)
