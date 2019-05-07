"""Tests `events.py`"""

# Copyright (c) 2019 Aubrey Barnard.
#
# This is free, open software licensed under the [MIT License](
# https://choosealicense.com/licenses/mit/).


import unittest

import esal

from .. import events


class PeriodsTest(unittest.TestCase):

    def test_empty(self):
        evs = []
        expected = [
            (esal.Interval(0, 9), 0),
        ]
        actual = list(events.periods(evs, 0, 9))
        self.assertEqual(expected, actual)

    def test_fill_span(self):
        evs = [
            esal.Event(esal.Interval(2, 3), 'a', 1),
        ]
        expected = [
            (esal.Interval(1, 2), 0),
            (esal.Interval(2, 3), 1),
            (esal.Interval(3, 4), 0),
        ]
        actual = list(events.periods(evs, 1, 4))
        self.assertEqual(expected, actual)

    def test_limit_to_span(self):
        evs = [
            esal.Event(esal.Interval(1, 9), 'a', 1),
        ]
        expected = [
            (esal.Interval(3, 7), 1),
        ]
        actual = list(events.periods(evs, 3, 7))
        self.assertEqual(expected, actual)

    def test_empty_span(self):
        evs = [
            esal.Event(esal.Interval(3, 5), 'a', 1),
            esal.Event(esal.Interval(4, 6), 'a', 2),
            esal.Event(esal.Interval(5, 5), 'a', 3),
            esal.Event(esal.Interval(5, 7), 'a', 4),
        ]
        expected = [
            (esal.Interval(5, 5), 1),
            (esal.Interval(5, 5), 2),
            (esal.Interval(5, 5), 3),
            (esal.Interval(5, 5), 4),
        ]
        actual = list(events.periods(evs, 5, 5))
        self.assertEqual(expected, actual)

    def test_merge(self):
        evs = [
            esal.Event(esal.Interval(1, 4), 'a', 1),
            esal.Event(esal.Interval(4, 8), 'a', 1),
            esal.Event(esal.Interval(6, 9), 'a', 2),
        ]
        expected = [
            (esal.Interval(0, 1), 0),
            (esal.Interval(1, 6), 1),
            (esal.Interval(6, 9), 2),
        ]
        actual = list(events.periods(evs, 0, 9))
        self.assertEqual(expected, actual)

    def test_overlapping_intervals(self):
        evs = [
            esal.Event(esal.Interval(1, 3), 'a', 1),
            esal.Event(esal.Interval(2, 4), 'a', 2),
            esal.Event(esal.Interval(3, 5), 'a', 1),
            esal.Event(esal.Interval(4, 6), 'a', 0),
            esal.Event(esal.Interval(5, 7), 'a', 2),
            esal.Event(esal.Interval(6, 8), 'a', 1),
        ]
        expected = [
            (esal.Interval(0, 1), 0),
            (esal.Interval(1, 2), 1),
            (esal.Interval(2, 3), 2),
            (esal.Interval(3, 5), 1),
            (esal.Interval(5, 6), 2),
            (esal.Interval(6, 8), 1),
            (esal.Interval(8, 9), 0),
        ]
        actual = list(events.periods(evs, 0, 9))
        self.assertEqual(expected, actual)

    def test_same_points(self):
        evs = [
            esal.Event(esal.Interval(1, 1), 'a', 1),
            esal.Event(esal.Interval(1, 1), 'a', 1),
            esal.Event(esal.Interval(1, 1), 'a', 2),
            esal.Event(esal.Interval(1, 1), 'a', 2),
        ]
        expected = [
            (esal.Interval(1, 1), 1),
            (esal.Interval(1, 1), 2),
        ]
        actual = list(events.periods(evs, 1, 1))
        self.assertEqual(expected, actual)

    def test_zero_values(self):
        evs = [
            esal.Event(esal.Interval(1, 7), 'a', '0'),
        ]
        expected = [
            (esal.Interval(0, 1), 0),
            (esal.Interval(1, 7), '0'),
            (esal.Interval(7, 9), 0),
        ]
        actual = list(events.periods(evs, 0, 9, zero_values=(0,)))
        self.assertEqual(expected, actual)
        expected = [
            (esal.Interval(0, 9), 0),
        ]
        actual = list(events.periods(evs, 0, 9, zero_values=('0',)))
        self.assertEqual(expected, actual)

    def test_min_len(self):
        evs = [
            esal.Event(esal.Interval(1, 1), 'a', 1),
            esal.Event(esal.Interval(4, 5), 'a', 1),
            esal.Event(esal.Interval(7, 9), 'a', 1),
        ]
        expected = [
            (esal.Interval(1, 3), 1),
            (esal.Interval(3, 4), 0),
            (esal.Interval(4, 6), 1),
            (esal.Interval(6, 7), 0),
            (esal.Interval(7, 9), 1),
        ]
        actual = list(events.periods(evs, 1, 9, min_len=2))
        self.assertEqual(expected, actual)

    def test_min_len_drop_empty_zero_val(self):
        evs = [
            esal.Event(esal.Interval(0, 2), 'a', 0),
            esal.Event(esal.Interval(2, 2), 'a', 1),
            esal.Event(esal.Interval(2, 4), 'a', 0),
            esal.Event(esal.Interval(4, 4), 'a', 2),
            esal.Event(esal.Interval(4, 9), 'a', 0),
        ]
        expected = [
            (esal.Interval(2, 4), 1),
            (esal.Interval(4, 6), 2),
        ]
        actual = list(events.periods(evs, 2, 6, min_len=2))
        self.assertEqual(expected, actual)

    def test_min_len_limit_to_span(self):
        evs = [
            esal.Event(esal.Interval(1, 1), 'a', 1),
        ]
        expected = [
            (esal.Interval(2, 5), 1),
        ]
        actual = list(events.periods(evs, 2, 5, min_len=7))
        self.assertEqual(expected, actual)

    def test_backoff_non_overlapping(self):
        evs = [
            esal.Event(esal.Interval(1, 1), 'a', 1),
            esal.Event(esal.Interval(5, 5), 'a', 2),
        ]
        expected = [
            (esal.Interval(1, 3), 1),
            (esal.Interval(5, 8), 2),
        ]
        actual = list(events.periods(evs, 1, 8, min_len=3, backoff=2))
        self.assertEqual(expected, actual)

    def test_backoff_overlapping(self):
        evs = [
            esal.Event(esal.Interval(1, 1), 'a', 1),
            esal.Event(esal.Interval(5, 5), 'a', 2),
        ]
        expected = [
            (esal.Interval(1, 4), 1),
            (esal.Interval(5, 9), 2),
        ]
        actual = list(events.periods(evs, 1, 9, min_len=5, backoff=1))
        self.assertEqual(expected, actual)

    def test_backoff_too_much(self):
        evs = [
            esal.Event(esal.Interval(1, 1), 'a', 1),
            esal.Event(esal.Interval(5, 5), 'a', 2),
        ]
        expected = [
            (esal.Interval(1, 1), 1),
            (esal.Interval(5, 9), 2),
        ]
        actual = list(events.periods(evs, 1, 9, min_len=5, backoff=5))
        self.assertEqual(expected, actual)

    def test_backoff_zero_val(self):
        evs = [
            esal.Event(esal.Interval(2, 3), 'a', 1),
            esal.Event(esal.Interval(5, 6), 'a', 1),
            esal.Event(esal.Interval(9, 10), 'a', 1),
        ]
        expected = [
            (esal.Interval(0, 1), 0),
            (esal.Interval(2, 3), 1),
            (esal.Interval(5, 6), 1),
            (esal.Interval(7, 8), 0),
            (esal.Interval(9, 10), 1),
        ]
        actual = list(events.periods(evs, 0, 11, backoff=1))
        self.assertEqual(expected, actual)
        expected.append((esal.Interval(11, 12), 0))
        actual = list(events.periods(evs, 0, 12, backoff=1))
        self.assertEqual(expected, actual)

    def test_backoff_drop_empty_zero_val(self):
        evs = [
            esal.Event(esal.Interval(1, 2), 'a', 1),
            esal.Event(esal.Interval(3, 4), 'a', 1),
        ]
        expected = [
            (esal.Interval(1, 2), 1),
            (esal.Interval(3, 4), 1),
        ]
        actual = list(events.periods(evs, 0, 4, backoff=1))
        self.assertEqual(expected, actual)
