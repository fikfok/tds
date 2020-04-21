import unittest

import pandas as pd

from commands import CellPosition, CellOffset, CellValue, RowNumFinder, ColNumFinder, ExcelCell, ExcelConstants
from data import simple_data


class TestTDS(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame(data=simple_data)

    def test_cell_position(self):
        first = CellPosition(col=1, row=1)
        second = CellPosition(col=2, row=2)
        third = CellPosition(col=3, row=3)
        self.assertEqual(first + second, third)

        self.assertRaises(Exception, CellPosition, col=-1, row=-1)
        self.assertRaises(Exception, CellPosition, col=-1)
        self.assertRaises(Exception, CellPosition, row=-1)

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

    def test_excell_cell(self):
        excell_cell = ExcelCell(cell_name='A1')
        self.assertEqual(excell_cell.cell_position, CellPosition(col=0, row=0))
        excell_cell = ExcelCell(cell_name='b2')
        self.assertEqual(excell_cell.cell_position, CellPosition(col=1, row=1))
        self.assertLessEqual(ExcelCell(cell_name='A1'), ExcelCell(cell_name='B1'))
        self.assertLessEqual(ExcelCell(cell_name='A1'), ExcelCell(cell_name='A2'))
        self.assertLess(ExcelCell(cell_name='A1'), ExcelCell(cell_name='B2'))
        self.assertEqual(ExcelCell(cell_name='A1'), ExcelCell(cell_name='A1'))

        start_excell_cell = ExcelCell(cell_name='B2')
        cells_offsets_results = [
            (CellOffset(col=-1, row=-1), ExcelCell(cell_name='A1')),
            (CellOffset(col=0, row=-1), ExcelCell(cell_name='B1')),
            (CellOffset(col=1, row=-1), ExcelCell(cell_name='C1')),
            (CellOffset(col=1, row=0), ExcelCell(cell_name='C2')),
            (CellOffset(col=1, row=1), ExcelCell(cell_name='C3')),
            (CellOffset(col=0, row=1), ExcelCell(cell_name='B3')),
            (CellOffset(col=-1, row=1), ExcelCell(cell_name='A3')),
            (CellOffset(col=-1, row=0), ExcelCell(cell_name='A2')),
            (CellOffset(col=0, row=0), ExcelCell(cell_name='B2')),
        ]
        for cell_offset, result_excell_cell in cells_offsets_results:
            self.assertEqual(start_excell_cell + cell_offset, result_excell_cell)

        self.assertRaises(Exception, ExcelCell, cell_name='b2c')
        self.assertRaises(Exception, ExcelCell, cell_name='2c')
        self.assertRaises(Exception, ExcelCell, cell_name='b')
        self.assertRaises(Exception, ExcelCell, cell_name='1')
        self.assertRaises(Exception, ExcelCell, cell_name='a@')
        self.assertRaises(Exception, ExcelCell, cell_name='a1-')
        self.assertRaises(Exception, ExcelCell, cell_name='aaaaa1')
        self.assertRaises(Exception, ExcelCell, cell_name='ш1')
        self.assertRaises(Exception, ExcelCell, cell_name='a' + str(ExcelConstants.MAX_EXCEL_ROWS_COUNT + 10))
