import unittest

import pandas as pd

from commands import CellPosition, CellOffset, CellValue, RowNumFinder, ColNumFinder
from data import simple_data


class TestTDS(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame(data=simple_data)

    def test_cell_position(self):
        first = CellPosition(col=1, row=1)
        second = CellPosition(col=2, row=2)
        third = CellPosition(col=3, row=3)
        self.assertEqual(first + second, third)

    def test_cell_position_offset(self):
        first = CellPosition(col=1, row=1)
        offset = CellOffset(col=2, row=2)
        third = CellPosition(col=3, row=3)
        self.assertEqual(first + offset, third)

        first = CellPosition(col=1, row=1)
        offset = CellOffset(col=-1, row=-1)
        third = CellPosition(col=0, row=0)
        self.assertEqual(first + offset, third)

    def test_cell_rownum_finder(self):
        cell_value = CellValue('*АРИТЕЛ ПЛЮС ТБ П/О 2,5МГ+6,25МГ №30')
        filter = RowNumFinder(df=self.df)
        self.assertEqual(filter.res(cell_value), CellPosition(row=1))

    def test_cell_colnum_finder(self):
        cell_value = CellValue(10289)
        filter = ColNumFinder(df=self.df)
        self.assertEqual(filter.res(cell_value), CellPosition(col=7))