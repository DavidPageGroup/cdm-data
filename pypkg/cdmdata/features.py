"""
Functionality for applying feature functions to event sequences to
create feature vectors
"""

# Copyright (c) 2019 Aubrey Barnard.
#
# This is free, open software licensed under the [MIT License](
# https://choosealicense.com/licenses/mit/).


import collections
import csv
import datetime
import json
import sys

from . import core
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
        modules=None,
        constructor_prefix='mk_func__',
):
    """
    Look up or create and return the feature function described by the
    function field in the given feature record.

    The function field can be the name of a function, the name of a
    function constructor (when prefixed with `constructor_prefix`), or a
    lambda expression.

    feature_record:
        List of values agreeing with `header`.
    function_index:
        Index of function field in record.
    modules:
        List of modules in which to look for functions.  (Looks in this
        module by default.)
    constructor_prefix:
        Prefix that identifies functions that construct feature
        functions.
    """
    func_text = feature_record[function_index]
    # Compile feature functions given as lambdas
    if func_text.startswith('lambda'):
        return compile_lambda(func_text)
    # Look up function
    else:
        mk_func = core.lookup(
            constructor_prefix + func_text, [globals()], modules)
        if mk_func is not None:
            return mk_func(feature_record)
        else:
            return core.lookup(func_text, [globals()], modules)


def mk_functions(feature_records, modules=None,
                 constructor_prefix='mk_func__'):
    """
    Create a return a list of feature functions based on the given
    feature records.

    feature_records:
        Iterable of feature records.
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
            feat_rec, func_idx, modules, constructor_prefix)
        if feat_func is None:
            raise ValueError(
                'Feature {}: Failed to find / construct function: {!r}'
                .format(feat_rec[id_idx], feat_rec[func_idx]))
        functions.append(feat_func)
    return functions


def map_to_functions(features, functions):
    """
    Create and return a mapping of feature keys to feature functions.

    Each feature's key is a (tbl, typ) pair.  A key can map to multiple
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


# Feature functions
#
# A feature function always takes 2 arguments: an example, and an event
# sequence


"""Mapping of names to atomic data types"""
nm2type = {t.__name__: t for t in (bool, float, int, str)}


def get_argument(arguments, index=None, key=None):
    """
    Return the indicated (by index or key) argument, or the argument
    itself if `arguments` is an atomic type.
    """
    if isinstance(arguments, list) and len(arguments) > 0:
        return arguments[index]
    elif isinstance(arguments, dict) and len(arguments) > 0:
        return arguments[key]
    elif (isinstance(arguments, (int, float, str, bool))
          or arguments is None):
        return arguments
    else:
        raise ValueError('Unrecognized arguments value: {!r}'
                         .format(args))


def event_sequence_id(example, event_sequence):
    """
    Feature function: Return the ID of the given event sequence.
    """
    return event_sequence.id


def mk_func__example_field(feature_record):
    """
    Create and return a feature function that returns the value of the
    indicated example field.

    Which field is indicated in the arguments field of the example
    record.  The field value is converted to the indicated data type.
    """
    _, _, _, _, _, data_type_name, _, args = feature_record
    ret_type = nm2type[data_type_name]
    field_idx = get_argument(args, 0, 'field_index')
    def featfunc__example_field(example, event_sequence):
        return ret_type(example[field_idx])
    return featfunc__example_field


def mk_func__year_of_fact(feature_record):
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


def mk_func__fact_matches(feature_record):
    """
    Create and return a feature function that returns true when an event
    sequence contains a matching fact.

    A fact matches when it has the key (tbl, typ) and the value from the
    given feature record.  The resulting boolean is converted to the
    indicated data type.
    """
    _, _, ev_cat, ev_typ, ev_val, data_type_name, _, _ = feature_record
    ret_type = nm2type[data_type_name]
    def featfunc__fact_matches(example, event_sequence):
        return ret_type(event_sequence.fact((ev_cat, ev_typ)) == ev_val)
    return featfunc__fact_matches


def mk_func__has_event(feature_record):
    """
    Create and return a feature function that returns true when an event
    sequence contains the indicated event.

    The (tbl, typ) pair of the feature record is the event type.  The
    resulting boolean is converted to the indicated data type.
    """
    _, _, ev_cat, ev_typ, _, data_type_name, _, _ = feature_record
    ret_type = nm2type[data_type_name]
    def featfunc__count_events(example, event_sequence):
        return ret_type(
            event_sequence.has_type((ev_cat, ev_typ)))
    return featfunc__count_events


def mk_func__count_events(feature_record):
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
