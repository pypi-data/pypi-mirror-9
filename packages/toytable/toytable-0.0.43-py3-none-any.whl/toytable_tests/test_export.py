import unittest
from six import StringIO
from toytable import TableTestMixin
from toytable import table_literal
from toytable import Table
import csv


class TestExport(unittest.TestCase, TableTestMixin):

    def setUp(self):
        self.s = [
            ('A', int),
            ('B', float),
            ('C', str),
        ]
        self.t = Table(self.s)

        self.t.extend([
            [1, 0.0, 'x'],
            [2, 5.0, 'y'],
            [3, 10.0, 'z'],
        ])

    def test_export_csv(self):
        output_file = StringIO()
        self.t.to_csv(output_file=output_file)
        output_file.seek(0)
        reader = csv.DictReader(output_file)
        row = next(reader)
        self.assertEqual(row, {"A":"1", "B":"0.0", "C":"x"})

    def test_export_csv_with_dialect(self):
        output_file = StringIO()
        self.t.to_csv(output_file=output_file, dialect="excel")
        output_file.seek(0)
        reader = csv.DictReader(output_file, dialect="excel")
        row = next(reader)
        self.assertEqual(row, {"A":"1", "B":"0.0", "C":"x"})

    def test_export_csv_with_dialect_types(self):
        output_file = StringIO()
        self.t.to_csv(output_file=output_file, dialect="excel", descriptions=True)
        output_file.seek(0)
        reader = csv.DictReader(output_file, dialect="excel")

        self.assertEqual(next(reader), {"A (int)":"1", "B (float)":"0.0", "C (str)":"x"})


    def test_export_csv_with_dialect_tab(self):
        output_file = StringIO()
        self.t.to_csv(output_file=output_file, dialect="excel-tab")
        output_file.seek(0)
        reader = csv.DictReader(output_file, dialect="excel-tab")
        row = next(reader)
        self.assertEqual(row, {"A":"1", "B":"0.0", "C":"x"})


if __name__ == '__main__':
    unittest.main()
