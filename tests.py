import unittest
from itertools import zip_longest

import pandas as pd

from base_types import ExcelConstants, CellValue, CellPosition, CellOffset, ExcelCell
from position_finders import FirstRowNumFinder, FirstColNumFinder, FirstCellPositionFinder, AllRowNumsFinder
from data import simple_data, duplicates_data


class TestTDS(unittest.TestCase):
    def setUp(self):
        self.simple_df = pd.DataFrame.from_dict(data=simple_data['data'], columns=simple_data['columns'],
                                                orient='index')
        self.duplicates_df = pd.DataFrame.from_dict(data=duplicates_data['data'], columns=duplicates_data['columns'],
                                                    orient='index')

    # @unittest.skip
    def test_cell_position(self):
        cells_offsets_results = [
            (CellOffset(col=-1, row=-1), CellPosition(col=0, row=0)),
            (CellOffset(col=0, row=-1), CellPosition(col=1, row=0)),
            (CellOffset(col=1, row=-1), CellPosition(col=2, row=0)),
            (CellOffset(col=1, row=0), CellPosition(col=2, row=1)),
            (CellOffset(col=1, row=1), CellPosition(col=2, row=2)),
            (CellOffset(col=0, row=1), CellPosition(col=1, row=2)),
            (CellOffset(col=-1, row=1), CellPosition(col=0, row=2)),
            (CellOffset(col=-1, row=0), CellPosition(col=0, row=1)),
            (CellOffset(col=0, row=0), CellPosition(col=1, row=1)),
            (CellOffset(col=-2, row=-2), CellPosition(col=0, row=0)),
            (CellOffset(col=1, row=-2), CellPosition(col=2, row=0)),
            (CellOffset(col=-2, row=1), CellPosition(col=0, row=2)),
        ]
        for cell_offset, result_cell_position in cells_offsets_results:
            self.assertEqual(CellPosition(col=1, row=1) + cell_offset, result_cell_position)

        cells_positions_results = [
            (CellPosition(col=1, row=1), CellPosition(col=2, row=2)),
            (CellPosition(col=2, row=2), CellPosition(col=3, row=3)),
            (CellPosition(col=1, row=2), CellPosition(col=2, row=3)),
            (CellPosition(col=2, row=1), CellPosition(col=3, row=2)),
        ]
        for cell_position, result_cell_position in cells_positions_results:
            self.assertEqual(CellPosition(col=1, row=1) + cell_position, result_cell_position)

        incomplete_cells_positions_results = [
            (CellPosition(), CellPosition(), CellPosition()),
            (CellPosition(col=1), CellPosition(col=1), CellPosition(col=2)),
            (CellPosition(row=1), CellPosition(row=1), CellPosition(row=2)),
            (CellPosition(col=1), CellPosition(row=1), CellPosition(col=1, row=1)),
            (CellPosition(col=1, row=1), CellPosition(row=1), CellPosition(col=1, row=2)),
            (CellPosition(col=1, row=1), CellPosition(col=1), CellPosition(col=2, row=1)),
        ]
        for first_cell_position, second_cell_position, result_cell_position in incomplete_cells_positions_results:
            self.assertEqual(first_cell_position + second_cell_position, result_cell_position)

        self.assertRaises(Exception, CellPosition, col=-1, row=-1)
        self.assertRaises(Exception, CellPosition, col=-1)
        self.assertRaises(Exception, CellPosition, row=-1)

    # @unittest.skip
    def test_cell_rownum_finder(self):
        cell_values_results = [
            (CellValue('SKU'), CellPosition(row=0)),
            (CellValue('*ГЛИЦИН-КАНОН ТБ ПОДЪЯЗЫЧ 1000 МГ №10'), CellPosition(row=5)),
            (CellValue(7458), CellPosition(row=10)),
            (CellValue(274254), CellPosition(row=15)),
            (CellValue(234637), CellPosition(row=20)),
            (CellValue(3012), CellPosition(row=25)),
            (CellValue('Общий итог'), CellPosition(row=0)),
        ]
        position_finder = FirstRowNumFinder(df=self.simple_df)
        for cell_value, result in cell_values_results:
            self.assertEqual(position_finder.res(cell_value), result)

    # @unittest.skip
    def test_cell_colnum_finder(self):
        cell_values_results = [
            (CellValue('SKU'), CellPosition(col=0)),
            (CellValue(2012), CellPosition(col=1)),
            (CellValue(2013), CellPosition(col=2)),
            (CellValue(2014), CellPosition(col=3)),
            (CellValue(2015), CellPosition(col=4)),
            (CellValue(2016), CellPosition(col=5)),
            (CellValue('Общий итог'), CellPosition(col=0)),
        ]
        position_finder = FirstColNumFinder(df=self.simple_df)
        for cell_value, result in cell_values_results:
            self.assertEqual(position_finder.res(cell_value), result)

    # @unittest.skip
    def test_cell_position_finder(self):
        cell_values_results = [
            (CellValue('SKU'), CellPosition(col=0, row=0)),
            (CellValue('Общий итог'), CellPosition(col=6, row=0)),
            (CellValue(7458), CellPosition(col=1, row=10)),
            (CellValue(6059), CellPosition(col=5, row=16)),
            (CellValue('ЭКСХОЛ КАПС 250 МГ №10'), CellPosition(col=0, row=197)),
            (CellValue(105153489.25), CellPosition(col=6, row=204)),
        ]
        position_finder = FirstCellPositionFinder(df=self.simple_df)
        for cell_value, result in cell_values_results:
            self.assertEqual(position_finder.res(cell_value), result)

    # @unittest.skip
    def test_excell_cell(self):
        self.assertEqual(ExcelCell(cell_name='A1').cell_position, CellPosition(col=0, row=0))
        excell_cell = ExcelCell(cell_name='b2')
        self.assertEqual(excell_cell.cell_position, CellPosition(col=1, row=1))
        self.assertLessEqual(ExcelCell(cell_name='A1'), ExcelCell(cell_name='B1'))
        self.assertLessEqual(ExcelCell(cell_name='A1'), ExcelCell(cell_name='A2'))
        self.assertLess(ExcelCell(cell_name='A1'), ExcelCell(cell_name='B2'))
        self.assertEqual(ExcelCell(cell_name='A1'), ExcelCell(cell_name='A1'))

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
            self.assertEqual(ExcelCell(cell_name='B2') + cell_offset, result_excell_cell)

        self.assertRaises(Exception, ExcelCell, cell_name='b2c')
        self.assertRaises(Exception, ExcelCell, cell_name='2c')
        self.assertRaises(Exception, ExcelCell, cell_name='b')
        self.assertRaises(Exception, ExcelCell, cell_name='1')
        self.assertRaises(Exception, ExcelCell, cell_name='a@')
        self.assertRaises(Exception, ExcelCell, cell_name='a1-')
        self.assertRaises(Exception, ExcelCell, cell_name='aaaaa1')
        self.assertRaises(Exception, ExcelCell, cell_name='ш1')
        self.assertRaises(Exception, ExcelCell, cell_name='a' + str(ExcelConstants.MAX_EXCEL_ROWS_COUNT + 10))

    def test_all_row_nums_finder(self):
        all_row_nums = AllRowNumsFinder(df=self.duplicates_df)
        cell_values_results = [
            (
                CellValue('*АРИТЕЛ ПЛЮС ТБ П/О 2,5МГ+6,25МГ №30'),
                [CellPosition(row=1), CellPosition(row=3)]
            ),
            (
                CellValue(1099),
                [CellPosition(row=2), CellPosition(row=7), CellPosition(row=9)]
            ),
            (CellValue(-999), [])
        ]
        for cell_value, expected_result_positions in cell_values_results:
            fact_result_positions = list(all_row_nums.res(cell_value))
            if fact_result_positions:
                zip_result = zip_longest(fact_result_positions, expected_result_positions)
                for fact_position, expected_position in zip_result:
                    self.assertEqual(fact_position, expected_position)
            else:
                self.assertEqual(fact_result_positions, expected_result_positions)
                self.assertEqual(fact_result_positions, cell_values_results[-1][1])
