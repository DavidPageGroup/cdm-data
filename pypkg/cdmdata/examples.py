"""Working with example definitions"""

# Copyright (c) 2019 Aubrey Barnard.
#
# This is free, open software licensed under the [MIT License](
# https://choosealicense.com/licenses/mit/).


import csv


def header(time_type=float):
    """
    Return a header that describes the fields of an example record in a
    table of example definitions.

    time_type:
        Constructor for type of time / date found in example records:
        time_type<T>(str) -> T.

    An example record describes a span of time where a subject has a
    particular label, treatment status, and classification.  It also has
    fields for storing a weight and a number of events.  Specifically,
    the fields of an example record are:

    id: int
        Subject ID.
    lo: time_type
        Start of example period.
    hi: time_type
        End of example period.
    lbl: str
        Semantic label for the example period.
    trt: str
        Treatment / Control status.
    cls: str
        Classification.
    wgt: float
        Example weight.  Perhaps the length of the period.
    n_evs: int
        Number of events during the example period.
    jsn: str
        Any extra information in JSON format.

    The fields of an example record are defined by how you use them.
    For example, patient 123456789 took drug A from 2005-11-22 to
    2006-08-16.  Since this study compares drug A to drug B, they are a
    control.  However, they were diagnosed with X during this period,
    which makes them positive for outcome X.  Thus, their record might
    be:

        123456789|2005-11-22|2006-08-16|rx-A:dx-X|c|+|267.0|13|{"age": 50}
    """
    return (
        ('id', int),
        ('lo', time_type),
        ('hi', time_type),
        ('lbl', str),
        ('trt', str),
        ('cls', str),
        ('wgt', float),
        ('n_evs', int),
        ('jsn', str),
    )
header_nm2idx = {
    fld[0]: i for (i, fld) in enumerate(header())}


"""Format of CSV tables of examples."""
csv_format = dict(
    delimiter='|',
    doublequote=False,
    escapechar='\\',
    lineterminator='\n',
    quotechar='"',
    quoting=csv.QUOTE_MINIMAL,
)
