"""Tests `records.py`"""

# Copyright (c) 2019 Aubrey Barnard.
#
# This is free, open software licensed under the [MIT License](
# https://choosealicense.com/licenses/mit/).


import io
import unittest

from .. import events
from .. import records


class ReadCsvTest(unittest.TestCase):

    csv_format = events.csv_format

    header = events.header(str)

    records1 = [
        [1, None, None, 'bx', 'a', '7', None],
        [2, '1978-01-10', '1981-08-25', 'px', '50', None, None],
        [3, '1978-08-16', '2007-09-17', 'ox', '893', 'lo', None],
        [4, '1978-12-02', '1998-03-23', 'xx', None, None, None],
        [5, '1982-11-17', None, 'dx', '771', None, None],
    ]

    @staticmethod
    def mk_line(record, delimiter='|'):
        return delimiter.join(
            str(x) if x is not None else '' for x in record)

    @staticmethod
    def mk_csv(header=None, records=None, delimiter='|'):
        file = io.StringIO()
        if header is not None:
            print(*(f[0] for f in header), sep=delimiter, file=file)
        if records is not None:
            for record in records:
                print(*(x if x is not None else '' for x in record),
                      sep=delimiter, file=file)
        file.seek(0)
        return file

    def test_empty(self):
        file = io.StringIO()
        recs = records.read_csv(file, self.csv_format, self.header)
        self.assertEqual([], list(recs))

    def test_header_records1(self):
        file = self.mk_csv(
            self.header, self.records1, self.csv_format['delimiter'])
        recs = records.read_csv(file, self.csv_format, self.header)
        self.assertEqual(self.records1, list(recs))

    def test_no_header_records1(self):
        file = self.mk_csv(
            None, self.records1, self.csv_format['delimiter'])
        recs = records.read_csv(file, self.csv_format, self.header)
        self.assertEqual(self.records1, list(recs))

    def test_header_no_records(self):
        file = self.mk_csv(self.header, None, self.csv_format['delimiter'])
        recs = records.read_csv(file, self.csv_format, self.header)
        self.assertEqual([], list(recs))

    def test_is_header_if_first_n_lines(self):
        lines = [''] * 10
        lines.append(self.mk_line(
            self.records1[3], self.csv_format['delimiter']))
        file = io.StringIO('\n'.join(lines)) # No trailing newline!
        recs = records.read_csv(file, self.csv_format, self.header,
                                records.is_header_if_first_n_lines(10))
        self.assertEqual([self.records1[3]], list(recs))

    def test_is_header_if_has_fields(self):
        for field_names in (
                (self.header[0][0],),
                (self.header[-1][0],),
                tuple(f[0] for f in self.header[1:3]),
                tuple(f[0] for f in self.header),
        ):
            with self.subTest(field_names):
                file = self.mk_csv(
                    self.header, [self.records1[2]],
                    self.csv_format['delimiter'])
                recs = records.read_csv(
                    file, self.csv_format, self.header,
                    records.is_header_if_has_fields(*field_names))
                self.assertEqual([self.records1[2]], list(recs))
