"""
Functionality for applying feature functions to event sequences to
create feature vectors
"""

# Copyright (c) 2019 Aubrey Barnard.
#
# This is free, open software licensed under the [MIT License](
# https://choosealicense.com/licenses/mit/).


import csv
import datetime
import json
import sys

from . import core


# Feature records


def header():
    return (
        ('id', int),
        ('name', str),
        ('tbl', str),
        ('typ', str),
        ('val', str),
        ('data_type', str),
        ('feat_func', str),
        ('args', json.loads),
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


def read(features_csv_filename, csv_format=csv_format): # FIXME
    # Read and parse the feature records
    return list(parse_records(
        schema.feature_header(), read_records(
            features_csv_filename, csv_format)))


def compile_lambda(text): # TODO
    return None


def mk_function(
        feature_record,
        function_index=header_nm2idx['feat_func'],
        modules=None,
        constructor_prefix='mk_func__',
):
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
    return event_sequence.id


def mk_func__example_field(feature_record):
    _, _, _, _, _, data_type_name, _, args = feature_record
    ret_type = nm2type[data_type_name]
    field_idx = get_argument(args, 0, 'field_index')
    def featfunc__example_field(example, event_sequence):
        return ret_type(example[field_idx])
    return featfunc__example_field


def mk_func__year_of_fact(feature_record):
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
    _, _, ev_cat, ev_typ, ev_val, data_type_name, _, _ = feature_record
    ret_type = nm2type[data_type_name]
    def featfunc__fact_matches(example, event_sequence):
        return ret_type(event_sequence.fact((ev_cat, ev_typ)) == ev_val)
    return featfunc__fact_matches


def mk_func__has_event(feature_record):
    _, _, ev_cat, ev_typ, _, data_type_name, _, _ = feature_record
    ret_type = nm2type[data_type_name]
    def featfunc__count_events(example, event_sequence):
        return ret_type(
            event_sequence.has_type((ev_cat, ev_typ)))
    return featfunc__count_events


def mk_func__count_events(feature_record):
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
