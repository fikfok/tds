import copy
import itertools
from abc import ABC, abstractmethod

import numpy as np
import pandas as pd


class CellValue:
    def __init__(self, value=None):
        self._value = value

    @property
    def value(self):
        return self._value

    def __str__(self):
        return self._value

    def __repr__(self):
        return f'CellValue({self._value})'


class CellPosition:
    """
    Zero-based позиция ячейки.
    """
    def __init__(self, row: int = None, col: int = None):
        self._row = row
        self._col = col

    @property
    def row(self):
        return self._row

    @property
    def col(self):
        return self._col

    def __lt__(self, other):
        return (self._row < other.row and self._col <= other.col) or \
               (self._row <= other.row and self._col < other.col)

    def __le__(self, other):
        return self._row <= other.row and self._col <= other.col

    def __eq__(self, other):
        return self._row == other.row and self._col == other.col

    def __add__(self, other):
        col = self._add_two_values(first=self._col, second=other.col)
        row = self._add_two_values(first=self._row, second=other.row)
        return CellPosition(col=col, row=row)

    def _add_two_values(self, first: [np.integer, int, None], second: [np.integer, int, None]) -> [int, None]:
        res = None
        if isinstance(first, (np.integer, int)) and isinstance(second, (np.integer, int)):
            res = first + second
        elif first is None and isinstance(second, (np.integer, int)):
            res = second
        elif isinstance(first, (np.integer, int)) and second is None:
            res = first
        elif first is None and second is None:
            res = None

        if isinstance(res, (np.integer, int)):
            res = res if res >= 0 else 0
        return res

    def __repr__(self):
        return f'CellPosition(col={self._col}, row={self._row})'


class CellOffset(CellPosition):
    def __repr__(self):
        return f'CellOffset(col={self._col}, row={self._row})'


class ExcelCell:
    """
    One-based адрес ячейки в стиле Excel: А1.
    """
    MAX_EXCEL_COLUMNS_COUNT = 16384
    MAX_EXCEL_ROWS_COUNT = 1048576

    _first_columns_labels = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    _all_columns_labels = list(_first_columns_labels)
    _all_columns_labels += [''.join(item) for item in itertools.product(_first_columns_labels, repeat=3)]
    ALL_COLUMNS_LABELS = _all_columns_labels[:MAX_EXCEL_COLUMNS_COUNT]

    def __init__(self, cell_name: str):
        self._cell_name = cell_name.upper()

        col_alias = ''
        row_alias = ''
        for char in self._cell_name:
            if char.isalpha():
                col_alias += char
            elif char.isdigit():
                row_alias += char
            else:
                raise Exception(f'Wrong char in ExcelCellPosition: "{char}"')
        try:
            col = self.ALL_COLUMNS_LABELS.index(col_alias)
        except Exception:
            raise Exception(f'Wrong column name in ExcelCellPosition: "{col_alias}"')

        try:
            row = int(row_alias)
        except Exception:
            raise Exception(f'Wrong row number in ExcelCellPosition: "{col_alias}"')
        else:
            if row > self.MAX_EXCEL_ROWS_COUNT:
                raise Exception(f'Wrong row number in ExcelCellPosition: "{col_alias}"')

        row -= 1
        self._cell_position = CellPosition(col=col, row=row)

    @property
    def excel_cell(self) -> str:
        return self._cell_name

    @property
    def cell_position(self) -> CellPosition:
        return self._cell_position

    def __lt__(self, other):

    def __le__(self, other):

    def __eq__(self, other):

    def __add__(self, other):
        only CellOffset can be


    def __repr__(self):
        return f'ExcelCell(cell_name="{self._cell_name}")'


class Command:
    def __init__(self, df: pd.DataFrame):
        self._df = df
        self._cell_value = None
        self._fillna_res = True

    @property
    def fillna_res(self):
        return self._fillna_res

    @fillna_res.setter
    def fillna_res(self, value: bool):
        self._fillna_res = value

    @abstractmethod
    def res(self): raise NotImplementedError

    def _filter_df_by_positions(self, start_position: CellPosition, end_position: CellPosition) -> pd.DataFrame:
        res_df = pd.DataFrame()
        if start_position <= end_position:
            row_slice = slice(start_position.row, end_position.row + 1)
            col_slice = slice(start_position.col, end_position.col + 1)
            res_df: pd.DataFrame = self._df.iloc[row_slice, col_slice]
        return res_df

    def __repr__(self):
        cls_name = self.__class__.__name__
        return f"{cls_name}(df)"


class RowNumFinder(Command):
    def res(self, cell_value: CellValue) -> CellPosition:
        # return self._df[self._df.eq(self._cell_value.value).any(axis=1)].index[0]
        row = self._df[self._df.eq(cell_value.value)].any(axis=1).idxmax()
        return CellPosition(row=row)


class RowNumFinderOffset(RowNumFinder):
    def res(self, cell_value: CellValue, cell_offset: CellOffset) -> CellPosition:
        return super().res(cell_value) + cell_offset


class ColNumFinder(Command):
    def res(self, cell_value: CellValue) -> CellPosition:
        col = self._df[self._df.eq(cell_value.value)].any(axis=0).idxmax()
        return CellPosition(col=col)


class ColNumFinderOffset(ColNumFinder):
    def res(self, cell_value: CellValue, cell_offset: CellOffset) -> CellPosition:
        return super().res(cell_value) + cell_offset


class CellPositionFinder(Command):
    def res(self, cell_value: CellValue) -> CellPosition:
        row_num_finder = RowNumFinder(df=self._df)
        col_num_finder = ColNumFinder(df=self._df)
        return row_num_finder.res(cell_value) + col_num_finder.res(cell_value)


class CellPositionFinderOffset(CellPositionFinder):
    def res(self, cell_value: CellValue, cell_offset: CellOffset) -> CellPosition:
        return super().res(cell_value) + cell_offset


class StartEndCellsByValueFilterDF(Command):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cell_pos_finder = CellPositionFinder(df=self._df)

    def res(self, start_cell_value: CellValue, end_cell_value: CellValue):
        start_position = self.cell_pos_finder.res(start_cell_value)
        end_position = self.cell_pos_finder.res(end_cell_value)

        res_df = self._filter_df_by_positions(start_position, end_position)
        if self._fillna_res:
            res_df.fillna(0, inplace=True)
        return res_df


class StartEndCellsByValueOffsetFilterDF(Command):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cell_pos_finder_offset = CellPositionFinderOffset(df=self._df)

    def res(self, start_cell_value: CellValue, end_cell_value: CellValue, start_pos_offset: CellOffset,
            end_pos_offset: CellOffset):
        start_position = self.cell_pos_finder_offset.res(start_cell_value, start_pos_offset)
        end_position = self.cell_pos_finder_offset.res(end_cell_value, end_pos_offset)

        res_df = self._filter_df_by_positions(start_position, end_position)
        if self._fillna_res:
            res_df.fillna(0, inplace=True)
        return res_df


class ByPositionLeftTopRightBottomFilterDF(Command):
    def res(self, start_position: CellPosition, end_position: CellPosition):
        res_df = self._filter_df_by_positions(start_position, end_position)
        if self._fillna_res:
            res_df.fillna(0, inplace=True)
        return res_df
