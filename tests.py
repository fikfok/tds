import unittest
from itertools import zip_longest

import numpy as np
import pandas as pd

from base_types import ExcelConstants, CellValue, CellPosition, CellOffset, ExcelCell, NeighborCell, \
    ExactValueFinder, ExactValuesFinder, RegexFinder, NeighborsContainer, CellOffsetAction, StartWithFinder, \
    EndWithFinder
from position_finders import FirstRowNumFinder, FirstColNumFinder, FirstCellPositionFinder, AllRowNumsFinder, \
    AllCellPositionsFinder, AllColNumsFinder
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
            (CellOffset(col=-2, row=-2), CellPosition(col=-1, row=-1)),
            (CellOffset(col=1, row=-2), CellPosition(col=2, row=-1)),
            (CellOffset(col=-2, row=1), CellPosition(col=-1, row=2)),
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

        self.assertTrue(CellPosition(col=1))
        self.assertTrue(CellPosition(row=1))
        self.assertTrue(CellPosition(col=1, row=1))
        self.assertFalse(CellPosition())
        self.assertEqual(CellPosition(), CellPosition())
        self.assertNotEqual(CellPosition(), CellPosition(col=1))
        self.assertNotEqual(CellPosition(), CellPosition(row=1))
        self.assertNotEqual(CellPosition(), CellPosition(col=1, row=1))

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
            (CellValue('Qwerty'), CellPosition()),
            (CellValue(-999), CellPosition()),
        ]
        finder = FirstRowNumFinder(df=self.simple_df)
        for cell_value, result_position in cell_values_results:
            finder.value_finder = ExactValueFinder(cell_value=cell_value)
            self.assertEqual(finder.get_position(), result_position)

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
            (CellValue('Qwerty'), CellPosition()),
            (CellValue(-999), CellPosition()),

        ]
        finder = FirstColNumFinder(df=self.simple_df)
        for cell_value, result_positions in cell_values_results:
            finder.value_finder = ExactValueFinder(cell_value)
            self.assertEqual(finder.get_position(), result_positions)

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
        finder = FirstCellPositionFinder(df=self.simple_df)
        for cell_value, result_position in cell_values_results:
            finder.value_finder = ExactValueFinder(cell_value)
            self.assertEqual(finder.get_position(), result_position)

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

    # @unittest.skip
    def test_all_row_nums_finder(self):
        finder = AllRowNumsFinder(df=self.duplicates_df)
        cell_values_results = [
            (
                CellValue('*АРИТЕЛ ПЛЮС ТБ П/О 2,5МГ+6,25МГ №30'),
                [CellPosition(row=1), CellPosition(row=3)]
            ),
            (
                CellValue(1099),
                [CellPosition(row=2), CellPosition(row=7), CellPosition(row=9)]
            ),
            (
                CellValue(''),
                [CellPosition(row=1), CellPosition(row=5), CellPosition(row=12)]
            ),
            (
                CellValue(),
                [CellPosition(row=1), CellPosition(row=5), CellPosition(row=12)]
            ),
            (
                CellValue(0),
                [CellPosition(row=counter) for counter in range(1, 11)]
            ),
            (CellValue('Qwerty'), []),
            (CellValue(-999), [])
        ]
        for cell_value, expected_result_positions in cell_values_results:
            finder.value_finder = ExactValueFinder(cell_value=cell_value)
            fact_result_positions = finder.get_all_positions()
            self.assertEqual(len(expected_result_positions), len(fact_result_positions))
            if fact_result_positions:
                zip_result = zip_longest(fact_result_positions, expected_result_positions)
                for fact_position, expected_position in zip_result:
                    self.assertEqual(fact_position, expected_position)
            else:
                self.assertEqual(fact_result_positions, expected_result_positions)
                self.assertEqual(fact_result_positions, cell_values_results[-1][1])

    # @unittest.skip
    def test_all_col_nums_finder(self):
        finder = AllColNumsFinder(df=self.duplicates_df)
        cell_values_results = [
            (
                CellValue('Общий итог'),
                [CellPosition(col=0), CellPosition(col=6)]
            ),
            (
                CellValue(2256),
                [CellPosition(col=1), CellPosition(col=6)]
            ),
            (
                CellValue(''),
                [
                    CellPosition(col=0),
                    CellPosition(col=1),
                    CellPosition(col=2),
                    CellPosition(col=3),
                    CellPosition(col=4),
                    CellPosition(col=5),
                    CellPosition(col=6),
                ]
            ),
            (
                CellValue(),
                [
                    CellPosition(col=0),
                    CellPosition(col=1),
                    CellPosition(col=2),
                    CellPosition(col=3),
                    CellPosition(col=4),
                    CellPosition(col=5),
                    CellPosition(col=6),
                ]
            ),
            (
                CellValue(0),
                [CellPosition(col=counter) for counter in range(2, 6)]
            ),
            (CellValue('Qwerty'), []),
            (CellValue(-999), [])
        ]
        for cell_value, expected_result_positions in cell_values_results:
            finder.value_finder = ExactValueFinder(cell_value=cell_value)
            fact_result_positions = finder.get_all_positions()
            if fact_result_positions:
                zip_result = zip_longest(fact_result_positions, expected_result_positions)
                for fact_position, expected_position in zip_result:
                    self.assertEqual(fact_position, expected_position)
            else:
                self.assertEqual(fact_result_positions, expected_result_positions)
                self.assertEqual(fact_result_positions, cell_values_results[-1][1])

    # @unittest.skip
    def test_neighbor(self):
        data_set = [
            (CellPosition(col=0, row=0), CellValue(4302), CellOffset(col=1, row=1), True),
            (CellPosition(col=1, row=1), CellValue('SKU'), CellOffset(col=-1, row=-1), True),
            (CellPosition(col=1, row=1), CellValue(2012), CellOffset(col=0, row=-1), True),
            (CellPosition(col=1, row=1), CellValue(2013), CellOffset(col=1, row=-1), True),
            (CellPosition(col=1, row=1), CellValue(5987), CellOffset(col=1, row=0), True),
            (CellPosition(col=1, row=1), CellValue(3143), CellOffset(col=1, row=1), True),
            (CellPosition(col=1, row=1), CellValue(1099), CellOffset(col=0, row=1), True),
            (
                CellPosition(col=1, row=1),
                CellValue('*АРИТЕЛ ПЛЮС ТБ П/О 5МГ+6,25МГ №30'),
                CellOffset(col=-1, row=1),
                True
            ),
            (
                CellPosition(col=1, row=1),
                CellValue('*АРИТЕЛ ПЛЮС ТБ П/О 2,5МГ+6,25МГ №30'),
                CellOffset(col=-1, row=0),
                True
            ),
            (CellPosition(col=1, row=1), CellValue(4302), CellOffset(col=0, row=0), True),
            (CellPosition(col=0, row=0), CellValue(1), CellOffset(col=1, row=1), False),
        ]
        for cell_position, cell_value, cell_offset, result in data_set:
            neighbor = NeighborCell(df=self.simple_df, cell_value=cell_value, cell_offset=cell_offset)
            self.assertEqual(neighbor.is_neighbor(cell_position), result)

    # @unittest.skip
    def test_cell_value(self):
        cell_values_numbers_results = [
            (CellValue(1), CellValue(1)),
            (CellValue(0), CellValue(0)),
            (CellValue(1.0), CellValue(1)),
            (CellValue(0.1), CellValue(0.1)),
            (CellValue(0.10), CellValue(0.1)),
            (CellValue(0.100), CellValue(0.1)),
            (CellValue(0.1000), CellValue(0.1)),
            (CellValue(0.10000), CellValue(0.1)),
            (CellValue(0.100000), CellValue(0.1)),
            (CellValue(0.1000000), CellValue(0.1)),
            (CellValue(0.10000000), CellValue(0.1)),
            (CellValue(0.100000000), CellValue(0.1)),
            (CellValue(0.1000000000), CellValue(0.1)),
            (CellValue(0.11), CellValue(0.11)),
            (CellValue(0.111), CellValue(0.111)),
            (CellValue(0.1111), CellValue(0.1111)),
            (CellValue(0.11111), CellValue(0.11111)),
            (CellValue(0.111111), CellValue(0.111111)),
            (CellValue(0.1111111), CellValue(0.1111111)),
            (CellValue(0.11111111), CellValue(0.11111111)),
            (CellValue(0.111111111), CellValue(0.111111111)),
            (CellValue(0.1111111111), CellValue(0.1111111111)),
            (CellValue(0.1111111111 + 0.1111111111), CellValue(0.2222222222)),
            (CellValue(1 + 1), CellValue(2)),
            (CellValue(1 + 0.11), CellValue(1.11)),
            (CellValue(1 + 0.111), CellValue(1.111)),
            (CellValue(1 + 0.1111), CellValue(1.1111)),
            (CellValue(1 + 0.11111), CellValue(1.11111)),
            (CellValue(1 + 0.111111), CellValue(1.111111)),
            (CellValue(1 + 0.1111111), CellValue(1.1111111)),
            (CellValue(1 + 0.11111111), CellValue(1.11111111)),
            (CellValue(1 + 0.111111111), CellValue(1.111111111)),
            (CellValue(1 + 0.1111111111), CellValue(1.1111111111)),
            (CellValue(1 + 0.1111111111 + 0.1111111111), CellValue(1.2222222222)),
            (CellValue(0.1 + 0.01), CellValue(0.11)),
            (CellValue(0.11 + 0.001), CellValue(0.111)),
            (CellValue(0.11 + 0.0011), CellValue(0.1111)),
            (CellValue(0.1 + 0.01111), CellValue(0.11111)),
            (CellValue(0.111 + 0.000111), CellValue(0.111111)),
            (CellValue(1 * 1.1), CellValue(1.1)),
            (CellValue(1.1 * 1.1), CellValue(1.2100000000000002)),
            (CellValue(1 / 3), CellValue(0.3333333333333333)),
            (CellValue(10.0/5.0), CellValue(2)),
        ]

        cell_values_strings_results = [
            (CellValue('Qwerty'), CellValue('Qwerty')),
            (CellValue('Qwerty '), CellValue('Qwerty ')),
            (CellValue(' Qwerty '), CellValue(' Qwerty ')),
            (CellValue(' Qwerty'), CellValue(' Qwerty')),
            (CellValue('123'), CellValue('123')),
            (CellValue('123A'), CellValue('123A')),
            (CellValue('A123A'), CellValue('A123A')),
            (CellValue('A123'), CellValue('A123')),
            (CellValue(''), CellValue('')),
            (CellValue(), CellValue('')),
            (CellValue(''), CellValue()),
            (CellValue('0'), CellValue('0')),
            (CellValue(' '), CellValue(' ')),
        ]

        for cell_value, result in cell_values_numbers_results:
            self.assertEqual(cell_value, result)
            self.assertEqual(CellValue(cell_value.value / 3), CellValue(result.value / 3))
            self.assertEqual(CellValue(-1 * cell_value.value), CellValue(-1 * result.value))
            self.assertEqual(CellValue(10 * cell_value.value), CellValue(10 * result.value))
            self.assertEqual(CellValue(-10 * cell_value.value), CellValue(-10 * result.value))

        for value in np.arange(0, 2, 0.3):
            self.assertEqual(CellValue(value), CellValue(value))
            self.assertEqual(CellValue(value * 0.1), CellValue(value * 0.1))
            self.assertEqual(CellValue(value / 3), CellValue(value / 3))
            self.assertEqual(CellValue(value + 10), CellValue(value + 10))
            self.assertEqual(CellValue(value - 999), CellValue(value - 999))

        for cell_value, result in cell_values_numbers_results:
            self.assertNotEqual(CellValue(-1 * cell_value.value + 1), CellValue(-1 * result.value))
            self.assertNotEqual(CellValue(-1 * cell_value.value + 0.1), CellValue(-1 * result.value))
            self.assertNotEqual(CellValue(10 * cell_value.value + 1), CellValue(10 * result.value))
            self.assertNotEqual(CellValue(10 * cell_value.value + 1.1), CellValue(10 * result.value))
            self.assertNotEqual(CellValue(-10 * cell_value.value + 1), CellValue(-10 * result.value))
            self.assertNotEqual(CellValue(-10 * cell_value.value + 1.1), CellValue(-10 * result.value))

        for cell_value, result in cell_values_strings_results:
            self.assertEqual(cell_value, result)
            str_val = str(cell_value)
            self.assertEqual(CellValue('' + str_val), CellValue('' + str_val))
            self.assertEqual(CellValue('' + str_val + ''), CellValue('' + str_val + ''))
            self.assertEqual(CellValue(str_val + ''), CellValue(str_val + ''))
            self.assertEqual(CellValue(str_val.replace('e', '\n')), CellValue(str_val.replace('e', '\n')))
            self.assertEqual(CellValue(str_val.replace('e', '\t')), CellValue(str_val.replace('e', '\t')))
            self.assertEqual(CellValue(str_val.replace('e', ' ')), CellValue(str_val.replace('e', ' ')))

        # Проверка оператора "in"
        cell_values = [
            CellValue(0),
            CellValue(0.1),
            CellValue(-0.1),
            CellValue(1),
            CellValue(-1),
            CellValue(1.1),
            CellValue(-1.1),
            CellValue('A'),
            CellValue(),
            CellValue(''),
        ]
        for ind in range(len(cell_values)):
            self.assertIn(cell_values[ind], cell_values)
        self.assertNotIn(CellValue(999), cell_values)
        self.assertNotIn(CellValue(-999), cell_values)
        self.assertNotIn(CellValue('Qwerty'), cell_values)

        self.assertTrue(CellValue('A'))
        self.assertTrue(CellValue(' '))
        self.assertTrue(CellValue(1))

        self.assertFalse(CellValue())
        self.assertFalse(CellValue(''))

        # TODO: datetime, datetime + timezone, time, 1E+4, 1.1 != '1.1'

    # @unittest.skip
    def test_all_positions(self):
        cell_values_results = [
            (CellValue(4302), [CellPosition(col=1, row=1), CellPosition(col=1, row=3)]),
            (CellValue(2256), [CellPosition(col=1, row=8), CellPosition(col=6, row=8)]),
            (CellValue('Общий итог'), [CellPosition(col=6, row=0), CellPosition(col=0, row=11)]),
            (CellValue(-999), []),
            (CellValue('Qwerty'), []),
            (
                CellValue(''),
                [
                    CellPosition(col=6, row=1),
                    CellPosition(col=5, row=5),
                    CellPosition(col=0, row=12),
                    CellPosition(col=1, row=12),
                    CellPosition(col=2, row=12),
                    CellPosition(col=3, row=12),
                    CellPosition(col=4, row=12),
                    CellPosition(col=5, row=12),
                    CellPosition(col=6, row=12)
                ]
            ),
            (CellValue(0), [
                CellPosition(col=3, row=1),
                CellPosition(col=4, row=1),
                CellPosition(col=5, row=1),
                CellPosition(col=3, row=2),
                CellPosition(col=4, row=2),
                CellPosition(col=5, row=2),
                CellPosition(col=3, row=3),
                CellPosition(col=4, row=3),
                CellPosition(col=5, row=3),
                CellPosition(col=2, row=4),
                CellPosition(col=3, row=4),
                CellPosition(col=4, row=4),
                CellPosition(col=5, row=4),
                CellPosition(col=3, row=5),
                CellPosition(col=4, row=5),
                CellPosition(col=2, row=6),
                CellPosition(col=3, row=6),
                CellPosition(col=4, row=6),
                CellPosition(col=5, row=6),
                CellPosition(col=4, row=7),
                CellPosition(col=5, row=7),
                CellPosition(col=2, row=8),
                CellPosition(col=3, row=8),
                CellPosition(col=4, row=8),
                CellPosition(col=5, row=8),
                CellPosition(col=2, row=9),
                CellPosition(col=3, row=9),
                CellPosition(col=5, row=9),
                CellPosition(col=2, row=10),
                CellPosition(col=3, row=10),
                CellPosition(col=4, row=10),
                CellPosition(col=5, row=10),
            ])
        ]
        finder = AllCellPositionsFinder(df=self.duplicates_df)
        for cell_value, results in cell_values_results:
            finder.value_finder = ExactValueFinder(cell_value=cell_value)
            finder_results = finder.get_all_positions()
            self._check_results(expected_result=results, finder_result=finder_results)

    # @unittest.skip
    def test_cell_values_finder(self):
        cell_values_results = [
            (
                [CellValue(3143), CellValue(2525)],
                [CellPosition(col=2, row=2), CellPosition(col=2, row=5), CellPosition(col=2, row=7)]
            ),
            (
                [CellValue('Общий итог'), CellValue()],
                [
                    CellPosition(col=6, row=0),
                    CellPosition(col=6, row=1),
                    CellPosition(col=5, row=5),
                    CellPosition(col=0, row=11),
                    CellPosition(col=0, row=12),
                    CellPosition(col=1, row=12),
                    CellPosition(col=2, row=12),
                    CellPosition(col=3, row=12),
                    CellPosition(col=4, row=12),
                    CellPosition(col=5, row=12),
                    CellPosition(col=6, row=12),
                ]
            ),

        ]
        finder = AllCellPositionsFinder(df=self.duplicates_df)
        for cell_values, results in cell_values_results:
            finder.value_finder = ExactValuesFinder(cell_values=cell_values)
            finder_results = finder.get_all_positions()
            self._check_results(expected_result=results, finder_result=finder_results)

    # @unittest.skip
    def test_cell_value_finder_with_neighbors(self):
        cell_values_neighbors_results = [
            (
                CellValue(2525),
                [NeighborCell(df=self.duplicates_df, cell_value=CellValue('Общий итог'), cell_offset=CellOffset(col=-2, row=6))],
                [CellPosition(col=2, row=5)]
            ),
            (
                CellValue(0),
                [NeighborCell(df=self.duplicates_df, cell_value=CellValue(), cell_offset=CellOffset(col=0, row=-1))],
                [CellPosition(col=5, row=6)]
            ),
            (
                CellValue('Общий итог'),
                [NeighborCell(df=self.duplicates_df, cell_value=CellValue(), cell_offset=CellOffset(col=0, row=1))],
                [CellPosition(col=6, row=0), CellPosition(col=0, row=11)]
            ),
            (
                CellValue('Общий итог'),
                [NeighborCell(df=self.duplicates_df, cell_value=CellValue(''), cell_offset=CellOffset(col=0, row=1))],
                [CellPosition(col=6, row=0), CellPosition(col=0, row=11)]
            ),
            (
                CellValue('Общий итог'),
                [
                    NeighborCell(df=self.duplicates_df, cell_value=CellValue(), cell_offset=CellOffset(col=0, row=1)),
                    NeighborCell(df=self.duplicates_df, cell_value=CellValue(), cell_offset=CellOffset(col=1, row=1)),
                ],
                [CellPosition(col=0, row=11)]
            ),
            (
                CellValue('Общий итог'),
                [
                    NeighborCell(df=self.duplicates_df, cell_value=CellValue(), cell_offset=CellOffset(col=0, row=1)),
                    NeighborCell(df=self.duplicates_df, cell_value=CellValue(''), cell_offset=CellOffset(col=1, row=1)),
                ],
                [CellPosition(col=0, row=11)]
            ),
            (
                CellValue('Общий итог'),
                [
                    NeighborCell(df=self.duplicates_df, cell_value=CellValue(''), cell_offset=CellOffset(col=0, row=1)),
                    NeighborCell(df=self.duplicates_df, cell_value=CellValue(''), cell_offset=CellOffset(col=1, row=1)),
                ],
                [CellPosition(col=0, row=11)]
            ),
            (
                CellValue('Общий итог'),
                [
                    NeighborCell(df=self.duplicates_df, cell_value=CellValue(''), cell_offset=CellOffset(col=0, row=1)),
                    NeighborCell(df=self.duplicates_df, cell_value=CellValue(), cell_offset=CellOffset(col=1, row=1)),
                ],
                [CellPosition(col=0, row=11)]
            ),

        ]
        finder = AllCellPositionsFinder(df=self.duplicates_df)
        for cell_value, neighbors, results in cell_values_neighbors_results:
            finder.value_finder = ExactValueFinder(cell_value=cell_value)
            finder.neighbors_container = NeighborsContainer(neighbors=neighbors)
            finder_results = finder.get_all_positions()
            self._check_results(expected_result=results, finder_result=finder_results)

    # @unittest.skip
    def test_cell_values_finder_with_neighbors(self):
        cell_values_neighbors_results = [
            (
                [CellValue(3143), CellValue(2525)],
                [NeighborCell(df=self.duplicates_df, cell_value=CellValue(4690), cell_offset=CellOffset(col=-1, row=0))],
                [CellPosition(col=2, row=5)]
            ),
        ]
        finder = AllCellPositionsFinder(df=self.duplicates_df)
        for cell_values, neighbors, results in cell_values_neighbors_results:
            finder.value_finder = ExactValuesFinder(cell_values=cell_values)
            finder.neighbors_container = NeighborsContainer(neighbors=neighbors)
            finder_results = finder.get_all_positions()
            self._check_results(expected_result=results, finder_result=finder_results)

    # @unittest.skip
    def test_regex_cell_value_pattern(self):
        patterns_results = [
            (
                '.*КАНОН.*\d{4}.*',
                [CellPosition(col=0, row=5)]
            ),
            (
                '.*АРИТЕЛ ПЛЮС(?!.*2,5).*',
                [CellPosition(col=0, row=2), CellPosition(col=0, row=7), CellPosition(col=0, row=10)]
            ),
        ]
        finder = AllCellPositionsFinder(df=self.duplicates_df)
        for pattern, results in patterns_results:
            finder.value_finder = RegexFinder(cell_value=CellValue(pattern))
            finder_results = finder.get_all_positions()
            self._check_results(expected_result=results, finder_result=finder_results)

    # @unittest.skip
    def test_cell_value_finder_with_offset(self):
        cell_values_results = [
            (CellValue('SKU'), CellOffset(col=1, row=0), [CellPosition(col=1, row=0)]),
            (CellValue('SKU'), CellOffset(col=-10, row=-10), []),
            (
                CellValue('Общий итог'),
                CellOffset(col=0, row=1),
                [
                    CellPosition(col=6, row=1),
                    CellPosition(col=0, row=12),
                ]
            ),
            (CellValue('Общий итог'), CellOffset(col=0, row=2), [CellPosition(col=6, row=2)]),
        ]
        finder = AllCellPositionsFinder(df=self.duplicates_df)
        for cell_value, cell_offset, results in cell_values_results:
            finder.value_finder = ExactValueFinder(cell_value=cell_value)
            finder.cell_offset_action = CellOffsetAction(cell_offset=cell_offset)
            finder_results = finder.get_all_positions()
            self._check_results(expected_result=results, finder_result=finder_results)

    # @unittest.skip
    def test_startwith(self):
        patterns_results = [
            (
                '*',
                [
                    CellPosition(col=0, row=1), CellPosition(col=0, row=2), CellPosition(col=0, row=3),
                    CellPosition(col=0, row=4), CellPosition(col=0, row=5), CellPosition(col=0, row=6),
                    CellPosition(col=0, row=7), CellPosition(col=0, row=8), CellPosition(col=0, row=9),
                    CellPosition(col=0, row=10), CellPosition(col=0, row=11), CellPosition(col=0, row=12),
                    CellPosition(col=0, row=13), CellPosition(col=0, row=14), CellPosition(col=0, row=15),
                ]
            ),
            (
                'НЕБИВОЛОЛ-',
                [CellPosition(col=0, row=132), CellPosition(col=0, row=133)]
            ),
            (
                '102',
                []
            ),
            # TODO ДОбавить ещё проверки. Вариант котороый есть ив текстовой ячейке и числовой
        ]
        finder = AllCellPositionsFinder(df=self.simple_df)
        for value, results in patterns_results:
            finder.value_finder = StartWithFinder(cell_value=CellValue(value))
            finder_results = finder.get_all_positions()
            self._check_results(expected_result=results, finder_result=finder_results)

    # @unittest.skip
    def test_endwith(self):
        patterns_results = [
            (
                '2,5МГ+6,25МГ №30',
                [CellPosition(col=0, row=1), CellPosition(col=0, row=3)]
            ),
            (
                '25',
                []
            ),
            # TODO ДОбавить ещё проверки. Вариант котороый есть ив текстовой ячейке и числовой
        ]
        finder = AllCellPositionsFinder(df=self.duplicates_df)
        for value, results in patterns_results:
            finder.value_finder = EndWithFinder(cell_value=CellValue(value))
            finder_results = finder.get_all_positions()
            self._check_results(expected_result=results, finder_result=finder_results)

    @unittest.skip
    def test_regex_finder_with_offset_neighbors(self):
        patterns_results = [
            (
                '^\*АРИТЕЛ.*',

            )
        ]

    def _check_results(self, expected_result: list, finder_result: list):
        self.assertEqual(len(expected_result), len(finder_result))
        for index, finder_cell_position in enumerate(finder_result):
            self.assertEqual(expected_result[index], finder_cell_position)
