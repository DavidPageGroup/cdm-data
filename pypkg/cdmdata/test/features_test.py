"""Tests `features.py`"""

# Copyright (c) 2019, 2021, 2023 Aubrey Barnard.
#
# This is free, open software licensed under the [MIT License](
# https://choosealicense.com/licenses/mit/).


import unittest

import esal

from .. import features


class FunctionTest(unittest.TestCase):

    def setUp(self):
        ev = esal.Event
        itvl1 = esal.Interval('2019-04-09', '2019-04-10')
        itvl2 = esal.Interval('2019-04-09')
        self.ev_seq = esal.EventSequence(
            events=[
                ev(itvl1, ('mx', '4'), ('lo', None)),
                ev(itvl1, ('mx', '4'), ('hi', None)),
                ev(itvl1, ('mx', '5'), ('lo', None)),
                ev(itvl1, ('mx', '8'), ('hi', None)),
                ev(itvl1, ('mx', '0'), ('lo', None)),
                ev(itvl1, ('mx', '2'), ('ok', None)),
                ev(itvl1, ('mx', '1'), ('ok', None)),
                ev(itvl1, ('mx', '8'), ('ok', None)),
                ev(itvl2, ('dx', '2'), (None, None)),
                ev(itvl2, ('dx', '0'), (None, None)),
                ev(itvl2, ('dx', '7'), (None, None)),
                ev(itvl2, ('dx', '2'), (None, None)),
                ev(itvl2, ('dx', '1'), (None, None)),
                ev(itvl2, ('dx', '3'), (None, None)),
                ev(itvl1, ('rx', '0'), (None, None)),
                ev(itvl1, ('rx', '5'), (None, None)),
                ev(itvl1, ('rx', '0'), (None, None)),
                ev(itvl1, ('rx', '4'), (None, None)),
                ev(itvl1, ('rx', '1'), (None, None)),
                ev(itvl1, ('px', '3'), (None, None)),
                ev(itvl1, ('px', '2'), (None, None)),
                ev(itvl1, ('px', '5'), (None, None)),
                ev(itvl1, ('px', '2'), (None, None)),
                ev(itvl1, ('ox', '0'), (None, None)),
                ev(itvl1, ('ox', '6'), (None, None)),
                ev(itvl1, ('vx', '1'), (None, None)),
                ev(itvl1, ('vx', '1'), (None, None)),
                ev(itvl1, ('xx', None), (None, None)),
            ],
            facts=[
                (('bx', 'dob'), '1949-04-09'),
                (('bx', 'ethn'), '1'),
                (('bx', 'gndr'), 'M'),
                (('bx', 'race'), '2'),
                (('hx', 'cancer-father'), 'yes'),
                (('hx', 'cancer-mother'), 'no'),
            ],
            id=808186755,
        )
        self.ev_seq_empty = esal.EventSequence([])

    def test_func__event_sequence_id(self):
        feat_rec = [67420, '_attr-id', '_attr', 'id', None,
                    None, 'event_sequence_id', None]
        feat_func = features.mk_function(feat_rec)
        self.assertEqual(808186755, feat_func(None, self.ev_seq))

    def test_func__example_field(self):
        feat_rec = [25721, '_attr-id', '_attr', 'wgt', None,
                    'float', 'example_field', 6]
        feat_func = features.mk_function(feat_rec)
        ex_rec = [647096516, '+', 'c', '0', '2019-01-01', '2019-07-01',
                  0.5111154238827391]
        self.assertEqual(0.5111154238827391, feat_func(ex_rec, None))

    def test_func__year_of_fact(self):
        feat_recs = [
            [94400, 'bx-dob', 'bx', 'dob', None,
             'int', 'year_of_fact', '%Y-%m-%d'],
            [50096, 'bx-yob', 'bx', 'yob', None,
             'int', 'year_of_fact', '%Y-%m-%d'],
        ]
        expecteds = [1949, 0]
        for idx in range(len(feat_recs)):
            with self.subTest(feat_recs[idx][1]):
                feat_func = features.mk_function(feat_recs[idx])
                self.assertEqual(
                    expecteds[idx], feat_func(None, self.ev_seq))

    def test_func__fact_matches(self):
        feat_recs = [
            [16664, 'bx-gndr-F', 'bx', 'gndr', 'F',
             'int', 'fact_matches', None],
            [54547, 'bx-gndr-M', 'bx', 'gndr', 'M',
             'int', 'fact_matches', None],
            [61122, 'bx-gndr-any', 'bx', 'gndr', 'F,M,O,U',
             'int', 'fact_matches', None],
            [48965, 'bx-gndr-fm', 'bx', 'gndr', 'F-M',
             'int', 'fact_matches', '-'],
        ]
        expecteds = [0, 1, 1, 1]
        for idx in range(len(feat_recs)):
            with self.subTest(feat_recs[idx][1]):
                feat_func = features.mk_function(feat_recs[idx])
                self.assertEqual(
                    expecteds[idx], feat_func(None, self.ev_seq))
                self.assertEqual(0, feat_func(None, self.ev_seq_empty))

    def test_func__has_event(self):
        feat_recs = [
            [92760, 'dx-1', 'dx', '1', None, 'int', 'has_event', None],
            [98707, 'px-2', 'px', '2', None, 'int', 'has_event', None],
            [30099, 'rx-3', 'rx', '3', None, 'int', 'has_event', None],
            [38896, 'vx-4', 'vx', '4', None, 'int', 'has_event', None],
        ]
        expecteds = [1, 1, 0, 0]
        for idx in range(len(feat_recs)):
            with self.subTest(feat_recs[idx][1]):
                feat_func = features.mk_function(feat_recs[idx])
                self.assertEqual(
                    expecteds[idx], feat_func(None, self.ev_seq))
                self.assertEqual(0, feat_func(None, self.ev_seq_empty))

    def test_func__n_events(self):
        feat_rec = [65211, '_attr-n_events', '_attr', 'n_events', None,
                    'int', 'n_events', None]
        feat_func = features.mk_function(feat_rec)
        self.assertEqual(28, feat_func(None, self.ev_seq))
        self.assertEqual(0, feat_func(None, self.ev_seq_empty))

    def test_func__count_events(self):
        feat_recs = [
            [92760, 'dx-1', 'dx', '1', None, 'int', 'count_events', None],
            [98707, 'px-2', 'px', '2', None, 'int', 'count_events', None],
            [30099, 'rx-3', 'rx', '3', None, 'int', 'count_events', None],
            [38896, 'vx-4', 'vx', '4', None, 'int', 'count_events', None],
        ]
        expecteds = [1, 2, 0, 0]
        for idx in range(len(feat_recs)):
            with self.subTest(feat_recs[idx][1]):
                feat_func = features.mk_function(feat_recs[idx])
                self.assertEqual(
                    expecteds[idx], feat_func(None, self.ev_seq))
                self.assertEqual(0, feat_func(None, self.ev_seq_empty))

    def test_func__proportion_events(self):
        feat_recs = [
            [92761, 'dx-2', 'dx', '2', None,
             'float', 'proportion_events', None],
            [98708, 'px-3', 'px', '3', None,
             'float', 'proportion_events', None],
            [30096, 'rx-0', 'rx', '0', None,
             'float', 'proportion_events', None],
            [38894, 'vx-2', 'vx', '2', None,
             'float', 'proportion_events', None],
        ]
        n_evs = self.ev_seq.n_events()
        expecteds = [n / n_evs for n in [2, 1, 2, 0]]
        for (feat_rec, exp) in zip(feat_recs, expecteds):
            with self.subTest(feat_rec[1]):
                feat_func = features.mk_function(feat_rec)
                self.assertEqual(exp, feat_func(None, self.ev_seq))
                self.assertEqual(0.0, feat_func(None, self.ev_seq_empty))

    def test_func__count_events_matching(self):
        feat_recs = [
            [63963, 'mx-4-hi', 'mx', '4', 'hi', 'int',
             'count_events_matching', dict(get_value='ev_val_0')],
            [63964, 'mx-4-lo', 'mx', '4', 'lo', 'int',
             'count_events_matching', dict(get_value='ev_val_0')],
            [63965, 'mx-4-ok', 'mx', '4', 'ok', 'int',
             'count_events_matching', dict(get_value='ev_val_0')],
            [26224, 'mx-8-any', 'mx', '8', 'lo,ok,hi', 'int',
             'count_events_matching', dict(get_value='ev_val_0')],
            [26225, 'mx-8-abn', 'mx', '8', 'lo;hi;ab', 'int',
             'count_events_matching',
             dict(delimiter=';', get_value='ev_val_0')],
        ]
        def ev_val_0(ev):
            return ev.value[0]
        expecteds = [1, 1, 0, 2, 1]
        for idx in range(len(feat_recs)):
            with self.subTest(feat_recs[idx][1]):
                feat_func = features.mk_function(
                    feat_recs[idx], namespaces=[locals()])
                self.assertEqual(
                    expecteds[idx], feat_func(None, self.ev_seq))
                self.assertEqual(0, feat_func(None, self.ev_seq_empty))

    def test_func__proportion_events_matching(self):
        feat_recs = [
            [63963, 'mx-4-hi', 'mx', '4', 'hi', 'float',
             'proportion_events_matching', dict(get_value='ev_val_0')],
            [63964, 'mx-4-lo', 'mx', '4', 'lo', 'float',
             'proportion_events_matching', dict(get_value='ev_val_0')],
            [63965, 'mx-4-ok', 'mx', '4', 'ok', 'float',
             'proportion_events_matching', dict(get_value='ev_val_0')],
            [26224, 'mx-8-any', 'mx', '8', 'lo,ok,hi', 'float',
             'proportion_events_matching', dict(get_value='ev_val_0')],
            [26225, 'mx-8-abn', 'mx', '8', 'lo;hi;ab', 'float',
             'proportion_events_matching',
             dict(delimiter=';', get_value='ev_val_0')],
        ]
        def ev_val_0(ev):
            return ev.value[0]
        n_evs = self.ev_seq.n_events()
        expecteds = [n / n_evs for n in [1, 1, 0, 2, 1]]
        for (feat_rec, exp) in zip(feat_recs, expecteds):
            with self.subTest(feat_rec[1]):
                feat_func = features.mk_function(
                    feat_rec, namespaces=[locals()])
                self.assertEqual(exp, feat_func(None, self.ev_seq))
                self.assertEqual(0.0, feat_func(None, self.ev_seq_empty))
