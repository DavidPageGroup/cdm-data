"""
Functionality for applying feature functions to event sequences to
create feature vectors, and for creating feature functions from a table
specified in a delimited file.

Example table of feature functions for
* facts
  * demographic / biographic information (bx)
  * custom / computed (cx)
  * medical history (hx)
* events
  * conditions / diagnoses (dx)
  * measurements / labs (mx)
  * observations (ox)
  * procedures (px)
  * drugs (rx)
  * visits (vx)
  * deaths (xx)
```
id|name|tbl|typ|val|data_type|feat_func|args
1|_attr-id|_attr|id||int|event_sequence_id|
2|_attr-wgt|_attr|wgt||float|example_field|6
3|bx-yob|bx|dob||int|year_of_fact|%Y-%m-%d
4|bx-gndr-fem|bx|gndr|F|int|fact_matches|
5|bx-gndr-mal|bx|gndr|M|int|fact_matches|
6|bx-gndr-oth|bx|gndr|O|int|fact_matches|
7|bx-gndr-unk|bx|gndr|U|int|fact_matches|
8|bx-race-1|bx|race|515|int|fact_matches|
9|bx-race-2|bx|race|516|int|fact_matches|
10|bx-ethn-1|bx|ethn|63|int|fact_matches|
11|bx-ethn-2|bx|ethn|64|int|fact_matches|
12|cx-age|cx|age||float|age|date
13|dx-0|dx|0||int|count_events|
14|mx-0|mx|0||int|count_events|
15|mx-0-lo|mx|0|lo|int|count_events_matching|
16|mx-0-ok|mx|0|ok|int|count_events_matching|
17|mx-0-hi|mx|0|hi|int|count_events_matching|
18|ox-0|ox|0||int|count_events|
19|px-0|px|0||int|count_events|
20|rx-0|rx|0||int|count_events|
21|vx-0|vx|0||int|count_events|
22|xx-0|xx|0||int|count_events|
```
"""

# Copyright (c) 2019, 2021, 2023 Aubrey Barnard.
#
# This is free, open software licensed under the [MIT License](
# https://choosealicense.com/licenses/mit/).


import collections
import csv
import datetime
import json
import operator
import sys

import esal

from . import core
from . import events
from . import examples
from . import records


# Feature records


def try_parse_json(text):
    """
    Parse the given JSON and return the constructed object.

    Return the given text unmodified if parsing as JSON fails.  Return
    `None` if the given text is empty.
    """
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def header():
    """Return a header for a table of features."""
    return (
        ('id', int),
        ('name', str),
        ('tbl', str),
        ('typ', str),
        ('val', str),
        ('data_type', str),
        ('feat_func', str),
        ('args', try_parse_json),
    )
header_nm2idx = {
    fld[0]: i for (i, fld) in enumerate(header())}


"""Format of CSV tables of features."""
csv_format = dict(
    delimiter='|',
    doublequote=False,
    escapechar='\\',
    lineterminator='\n',
    quotechar='"',
    quoting=csv.QUOTE_MINIMAL,
)


def compile_lambda(text): # TODO
    return None


def mk_function(
        feature_record,
        function_index=header_nm2idx['feat_func'],
        namespaces=None,
        modules=None,
        constructor_prefix='mk_func__',
):
    """
    Look up or create and return the feature function described by the
    function field in the given feature record.

    The function field can be the name of a function, the name of a
    function constructor (when prefixed with `constructor_prefix`), or a
    lambda expression (TODO).

    feature_record:
        List of values agreeing with `header`.
    function_index:
        Index of function field in record.
    namespaces:
        List of namespaces (dictionaries) in which to look for
        functions.  (Always looks in the namespace of this module as a
        last resort.)
    modules:
        List of modules in which to look for functions.
    constructor_prefix:
        Prefix that identifies functions that construct feature
        functions.
    """
    if namespaces is None:
        namespaces = []
    # Make new list to avoid modifying argument
    namespaces = namespaces + [globals()]
    # Get the function text
    func_text = feature_record[function_index]
    # Compile feature functions given as lambdas
    if func_text.startswith('lambda'):
        return compile_lambda(func_text)
    # Look up function
    else:
        mk_func = core.lookup(
            constructor_prefix + func_text, namespaces, modules)
        if mk_func is not None:
            return mk_func(
                feature_record, namespaces=namespaces, modules=modules)
        else:
            return core.lookup(func_text, namespaces, modules)


def mk_functions(feature_records, namespaces=None, modules=None,
                 constructor_prefix='mk_func__'):
    """
    Create a return a list of feature functions based on the given
    feature records.

    feature_records:
        Iterable of feature records.
    namespaces:
        Passed to `mk_function`.
    modules:
        Passed to `mk_function`.
    constructor_prefix:
        Passed to `mk_function`.
    """
    id_idx = header_nm2idx['id']
    func_idx = header_nm2idx['feat_func']
    functions = []
    for feat_rec in feature_records:
        feat_func = mk_function(
            feat_rec, func_idx, namespaces, modules, constructor_prefix)
        if feat_func is None:
            raise ValueError(
                'Feature {}: Failed to find / construct function: {!r}'
                .format(feat_rec[id_idx], feat_rec[func_idx]))
        functions.append(feat_func)
    return functions


def map_to_functions(features, functions):
    """
    Create and return a mapping of feature keys to feature functions.

    Each feature's key is a (tbl, typ) pair.  To support applying
    multiple functions to the same data, a key can map to multiple
    feature functions, so the values in the mapping are lists of
    (feature_id, feature_function) pairs.

    features:
        Iterable of feature records.
    functions:
        Corresponding iterable of feature functions.
    """
    feat_key2idsfuncs = collections.defaultdict(list)
    for feat, func in zip(features, functions):
        id, _, tbl, typ, _, _, _, _ = feat
        feat_key2idsfuncs[tbl, typ].append((id, func))
    return feat_key2idsfuncs


def load(
        features_csv_filename,
        csv_format=csv_format,
        header=header(),
        header_detector=True,
        namespaces=None,
        modules=None,
):
    """
    Load features and return a (records, functions, map-to-functions)
    triple.
    """
    feature_records = list(records.read_csv(
        features_csv_filename, csv_format, header, header_detector))
    feature_functions = mk_functions(
        feature_records, namespaces, modules)
    feature_key2idsfuncs = map_to_functions(
        feature_records, feature_functions)
    return feature_records, feature_functions, feature_key2idsfuncs


# Feature functions
#
# A feature function always takes 2 arguments: an example, and an event
# sequence


"""Mapping of names to atomic data types"""
nm2type = {t.__name__: t for t in (bool, float, int, str)}


def get_argument(arguments, index=None, key=None):
    """
    Return the indicated argument.

    If `arguments` is a collection, then the indicated argument value is
    looked up by index or key (depending on the collection).  If
    `arguments` is just a single, atomic value, then that value is
    returned.  Otherwise, an exception is raised.
    """
    if isinstance(arguments, list):
        return arguments[index]
    elif isinstance(arguments, dict):
        return arguments[key]
    elif (isinstance(arguments, (int, float, str, bool))
          or arguments is None):
        return arguments
    else:
        raise ValueError('Unrecognized arguments value: {!r}'
                         .format(args))


def get_option(
        arguments, index=None, key=None, default=None, atomic_ok=True):
    """
    Return the indicated optional argument or a default value.

    If `arguments` is a collection, then the indicated argument value is
    looked up by index or key (depending on the collection).  If
    `arguments` is just a single, atomic value, then that value is
    returned if allowed.  Otherwise, the default value is returned.
    """
    if isinstance(arguments, list) and len(arguments) > index:
        return arguments[index]
    elif isinstance(arguments, dict) and key in arguments:
        return arguments[key]
    elif atomic_ok and isinstance(arguments, (int, float, str, bool)):
        return arguments
    else:
        return default


def event_sequence_id(example, event_sequence):
    """
    Feature function: Return the ID of the given event sequence.
    """
    return event_sequence.id


def mk_func__example_field(
        feature_record, namespaces=None, modules=None):
    """
    Create and return a feature function that returns the value of the
    indicated example field.

    Which field is indicated in the arguments field of the feature
    record.  The field value is converted to the indicated data type.
    """
    _, _, _, _, _, data_type_name, _, args = feature_record
    ret_type = nm2type[data_type_name]
    field_idx = get_argument(args, 0, 'field_index')
    def featfunc__example_field(example, event_sequence):
        return ret_type(example[field_idx])
    return featfunc__example_field


def mk_func__year_of_fact(
        feature_record, namespaces=None, modules=None):
    """
    Create and return a feature function that returns the year of the
    indicated fact.

    Assumes the fact has a string value that is parseable as a datetime.
    The fact key is the (tbl, typ) pair of the feature record.  A date
    format string for `datetime.datetime.strptime` can be provided in
    the arguments field.  The year is converted to the indicated data
    type.
    """
    _, _, ev_cat, ev_typ, _, data_type_name, _, args = feature_record
    ret_type = nm2type[data_type_name]
    datetime_format = get_argument(args, 0, 'date_format')
    def featfunc__year_of_fact(example, event_sequence):
        val = event_sequence.fact((ev_cat, ev_typ))
        if val is None:
            return ret_type()
        dt = datetime.datetime.strptime(val, datetime_format)
        return ret_type(dt.year)
    return featfunc__year_of_fact


def mk_func__fact_matches(
        feature_record, namespaces=None, modules=None):
    """
    Create and return a feature function that returns true when an event
    sequence contains a matching fact.

    A fact matches when it has the key (tbl, typ) and one of the values
    from the given feature record.  The resulting boolean is converted
    to the indicated data type.

    A delimiter (default ',') for the set of matching values can be
    passed as an argument in the feature record.  For example, the
    following feature record uses a dash to separate stage synonyms.

    ```
    15815|hx-742411246-stage|hx|742411246|3-iii-III|str|fact_matches|-
    ```
    """
    _, _, ev_cat, ev_typ, ev_vals, data_type_name, _, args = feature_record
    ret_type = nm2type[data_type_name]
    delimiter = get_option(args, 0, 'delimiter', ',')
    # Handle multiple values
    vals = set(ev_vals.split(delimiter))
    def featfunc__fact_matches(example, event_sequence):
        return ret_type(event_sequence.fact((ev_cat, ev_typ)) in vals)
    return featfunc__fact_matches


def mk_func__has_event(feature_record, namespaces=None, modules=None):
    """
    Create and return a feature function that returns true when an event
    sequence contains the indicated event.

    The (tbl, typ) pair of the feature record is the event type.  The
    resulting boolean is converted to the indicated data type.
    """
    _, _, ev_cat, ev_typ, _, data_type_name, _, _ = feature_record
    ret_type = nm2type[data_type_name]
    def featfunc__has_event(example, event_sequence):
        return ret_type(event_sequence.has_type((ev_cat, ev_typ)))
    return featfunc__has_event


def mk_func__n_events(feature_record, namespaces=None, modules=None):
    """
    Create and return a feature function that counts how many events are
    in an event sequence.

    The (tbl, typ) pair of the feature record is the event type.  The
    count is converted to the indicated data type.
    """
    _, _, ev_cat, ev_typ, _, data_type_name, _, _ = feature_record
    ret_type = nm2type[data_type_name]
    def featfunc__n_events(example, event_sequence):
        return ret_type(event_sequence.n_events())
    return featfunc__n_events


def mk_func__count_events(
        feature_record, namespaces=None, modules=None):
    """
    Create and return a feature function that counts how many times the
    indicated event occurs in an event sequence.

    The (tbl, typ) pair of the feature record is the event type.  The
    count is converted to the indicated data type.
    """
    _, _, ev_cat, ev_typ, _, data_type_name, _, _ = feature_record
    ret_type = nm2type[data_type_name]
    def featfunc__count_events(example, event_sequence):
        return ret_type(
            event_sequence.n_events_of_type((ev_cat, ev_typ)))
    return featfunc__count_events


def mk_func__proportion_events(
        feature_record, namespaces=None, modules=None):
    """
    Create and return a feature function that is essentially
    'count_events(...) / n_events(...)'.
    """
    _, _, ev_cat, ev_typ, _, data_type_name, _, _ = feature_record
    ret_type = nm2type[data_type_name]
    def featfunc__proportion_events(example, event_sequence):
        n_typ = event_sequence.n_events_of_type((ev_cat, ev_typ))
        n_evs = event_sequence.n_events()
        return ret_type(n_typ / n_evs if n_evs > 0 else 0)
    return featfunc__proportion_events


def mk_func__count_events_matching(
        feature_record, namespaces=None, modules=None):
    """
    Create and return a feature function that counts how many times the
    indicated event occurs in an event sequence with values matching the
    specified ones.

    An event matches when it has the event type specified as the (tbl,
    typ) pair in the given feature record, and when it has one of the
    values from the feature record.  The resulting count is converted to
    the data type indicated in the feature record.

    There are two optional arguments to the feature function
    construction: (1) a delimiter (default ',') for the set of matching
    values (as for `fact_matches`), and (2) the name of the function to
    use to extract the query value from an event.  If not specified, the
    query value is just the event value.  For example, the following
    feature record specifies a feature that counts abnormal lab results,
    where the lab result code is stored as part of the event value and
    the function `get_lab_code` extracts it.

    ```
    28195|mx-364688946-ab|mx|364688946|lo;hi;ab|int|count_events_matching|[";", "get_lab_code"]
    ```
    """
    _, _, ev_cat, ev_typ, ev_vals, data_type_name, _, args = feature_record
    ret_type = nm2type[data_type_name]
    delimiter = get_option(args, 0, 'delimiter', ',')
    get_value = get_option(args, 1, 'get_value')
    get_value = (core.lookup(get_value, namespaces, modules)
                 if isinstance(get_value, str)
                 else operator.attrgetter('value'))
    # Handle multiple values
    vals = set(ev_vals.split(delimiter))
    def featfunc__count_events_matching(example, event_sequence):
        return ret_type(sum(
            1 for ev in event_sequence.events((ev_cat, ev_typ))
            if get_value(ev) in vals))
    return featfunc__count_events_matching


def mk_func__proportion_events_matching(
        feature_record, namespaces=None, modules=None):
    """
    Create and return a feature function that is essentially
    'count_events_matching(...) / n_events(...)'.
    """
    _, _, ev_cat, ev_typ, ev_vals, data_type_name, _, args = feature_record
    ret_type = nm2type[data_type_name]
    delimiter = get_option(args, 0, 'delimiter', ',')
    get_value = get_option(args, 1, 'get_value')
    get_value = (core.lookup(get_value, namespaces, modules)
                 if isinstance(get_value, str)
                 else operator.attrgetter('value'))
    # Handle multiple values
    vals = set(ev_vals.split(delimiter))
    def featfunc__proportion_events_matching(example, event_sequence):
        n_mat = sum(1 for ev in event_sequence.events((ev_cat, ev_typ))
                    if get_value(ev) in vals)
        n_evs = event_sequence.n_events()
        return ret_type(n_mat / n_evs if n_evs > 0 else 0)
    return featfunc__proportion_events_matching


# Feature vectors


def vector(feature_key2idsfuncs, example, event_sequence,
           always_keys=set()):
    """
    Create a feature vector by applying the given feature functions to
    the given example and event sequence and return it.

    Runs quickly by applying only those feature functions whose keys
    match the fact keys or event types of the event sequence.

    Creates a sparse feature vector by storing only those feature values
    that evaluate to `True`.

    feature_key2idsfuncs:
        Mapping of feature keys to lists of (feature-ID,
        feature-function) pairs as created by `map_to_functions`.
    example:
        Example record.  Only needed if feature functions will access
        it.
    event_sequence: esal.EventSequence
        Only needed if feature functions will access it.
    always_keys:
        Set of keys whose feature functions should always be applied.
        Useful for computing features whose keys do not appear in the
        facts or events of the event sequence, such as features of the
        example.
    """
    # Sparse mapping of feature IDs to values
    fv = {}
    # Use each fact and event key to look up the corresponding feature
    for key in (event_sequence.fact_keys() |
                event_sequence.types() | always_keys):
        ids_funcs = feature_key2idsfuncs.get(key)
        if ids_funcs is not None:
            for feat_id, feat_func in ids_funcs:
                value = feat_func(example, event_sequence)
                if value:
                    fv[feat_id] = value
    return fv


def write_vector(label, feature_vector, output=sys.stdout):
    """
    Write the given feature vector in SVMLight format to the given
    output.

    In SVMLight format, each line has the following syntax:

        <label> (" " <feature-id> ":" <feature-value>)*

    Writes feature (ID, value) pairs in ascending order of feature ID.

    label:
        Class label or regression value.
    feature_vector:
        Mapping of feature IDs to feature values.
    output:
        Output stream.
    """
    print(label, sep='', end='', file=output)
    for feat_id in sorted(feature_vector.keys()):
        print(' ', feat_id, ':', feature_vector[feat_id],
              sep='', end='', file=output)
    print(file=output)


def mk_feature_vectors(
        events_csv_filename,
        examples_csv_filename,
        features_csv_filename,
        events_csv_format=events.csv_format,
        examples_csv_format=examples.csv_format,
        features_csv_format=csv_format,
        events_header=events.header(),
        examples_header=examples.header(),
        features_header=header(),
        events_header_detector=True,
        examples_header_detector=True,
        features_header_detector=True,
        include_event_record=None,
        transform_event_record=None,
        include_example_record=None,
        always_feature_keys=(),
        feature_function_namespaces=None,
        feature_function_modules=None,
):
    """
    Make and yield feature vectors.

    Yields (example-label, example-weight, feature-vector) triples.
    """
    # Unpack events header
    ev_hdr_nm2idx = {f[0]: i for i, f in enumerate(events_header)}
    ev_id_idx = ev_hdr_nm2idx['id']
    # Unpack examples header
    ex_hdr_nm2idx = {f[0]: i for i, f in enumerate(examples_header)}
    ex_id_idx = ex_hdr_nm2idx['id']
    ex_lo_idx = ex_hdr_nm2idx['lo']
    ex_hi_idx = ex_hdr_nm2idx['hi']
    # Load example definitions
    exs = records.read_csv(
        examples_csv_filename, examples_csv_format, examples_header,
        examples_header_detector, include_record=include_example_record)
    # Collect examples by ID
    id2ex = collections.defaultdict(list)
    for ex in exs:
        id2ex[ex[ex_id_idx]].append(ex)
    # Load feature definitions
    _, _, feat_key2idsfuncs = load(
        features_csv_filename,
        features_csv_format,
        features_header,
        features_header_detector,
        feature_function_namespaces,
        feature_function_modules,
    )
    # Create a feature vector for each example definition.  Only
    # construct event sequences for IDs that have examples.
    for ev_seq in events.read_sequences(
            records.read_csv(
                events_csv_filename,
                events_csv_format,
                events_header,
                header_detector=events_header_detector,
                parser=False,
            ),
            header=events_header,
            parse_id=events_header[ev_id_idx][1],
            include_ids=id2ex,
            parse_record=records.mk_parser(events_header),
            include_record=include_event_record,
            transform_record=transform_event_record,
    ):
        # Skip any IDs without examples
        for ex in id2ex.get(ev_seq.id, ()):
            # Create a subsequence that includes all the events that
            # overlap the example period
            itvl = esal.Interval(ex[ex_lo_idx], ex[ex_hi_idx])
            subseq = ev_seq.subsequence(ev_seq.events_overlapping(
                itvl.lo, itvl.hi, itvl.is_lo_open, itvl.is_hi_open))
            # Create feature vector
            fv = vector(
                feat_key2idsfuncs, ex, subseq, always_feature_keys)
            # Yield example and its feature fector
            yield ex, fv
