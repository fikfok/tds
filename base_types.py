import itertools
from abc import ABC, abstractmethod

import numpy as np
import pandas as pd

from finder_conditions import FinderConditions, FinderConditionContainer


class ExcelConstants:
    MAX_EXCEL_COLUMNS_COUNT = 16384
    MAX_EXCEL_ROWS_COUNT = 1048576

    _first_columns_labels = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    _all_columns_labels = list(_first_columns_labels)
    _all_columns_labels += [''.join(item) for item in itertools.product(_first_columns_labels, repeat=3)]
    ALL_COLUMNS_LABELS = _all_columns_labels[:MAX_EXCEL_COLUMNS_COUNT]


class CellValue:
    """
    Хранит одиночное значение. Если будет передано '', то будет считаться, что это None
    """
    def __init__(self, value=None):
        if isinstance(value, str) and value == '':
            self._value = None
        else:
            self._value = value

    @property
    def value(self):
        return self._value

    def __eq__(self, another):
        if isinstance(self._value, float) and isinstance(another.value, float):
            # Т.к. в данном случае не стоит задача проверки близости двух значений друг к другу,
            # а необходимо проверить идентичность написанного.
            res = str(self._value) == str(another.value)
        elif pd.isnull(self._value) and pd.isnull(another.value):
            res = True
        else:
            res = self._value == another.value
        return res

    def __bool__(self):
        return False if self._value is None else True

    def __str__(self):
        return '' if self._value is None else str(self._value)

    def __repr__(self):
        return f'CellValue("{self._value}")' if isinstance(self._value, str) else f'CellValue({self._value})'


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

    @property
    def excel_cell(self) -> str:
        res = ''
        if self._col is not None and self._row is not None:
            res = ExcelConstants.ALL_COLUMNS_LABELS[self._col] + str(self._row + 1)
        else:
            # TODO Продумать этот вариант
            pass
        return res

    def __lt__(self, other):
        return (self._row < other.row and self._col <= other.col) or \
               (self._row <= other.row and self._col < other.col)

    def __le__(self, other):
        return self._row <= other.row and self._col <= other.col

    def __eq__(self, other):
        return self._row == other.row and self._col == other.col

    def __add__(self, other):
        # TODO Принять решение позже с чем можно складывать
        # if not isinstance(other, CellOffset):
        #     raise Exception('The second operand must be instance of CellOffset class')
        col = self._add_two_values(first=self._col, second=other.col)
        row = self._add_two_values(first=self._row, second=other.row)
        return CellPosition(col=col, row=row)

    def __bool__(self):
        return bool(self._col) or bool(self._row)

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
        return res

    def in_scope(self, df: pd.DataFrame):
        rows_cnt, col_cnt = df.shape
        return 0 <= self._row < rows_cnt and 0 <= self._col < col_cnt

    def __repr__(self):
        return f'CellPosition(col={self._col}, row={self._row})'


class CellOffset(CellPosition):
    """
    Смещение. Может хранить отрицательные значения.
    """
    def __init__(self, row: int = None, col: int = None):
        self._row = row
        self._col = col

    def __repr__(self):
        return f'CellOffset(col={self._col}, row={self._row})'


class ExcelCell:
    """
    One-based адрес ячейки в стиле Excel: А1.
    """
    def __init__(self, cell_name: str):
        self._cell_name = cell_name.upper()

        col_alias = ''
        row_alias = ''

        aliases_mask = ''
        char_type = ''
        for char in self._cell_name:
            if char.isalpha():
                char_type = 'c'
            elif char.isdigit():
                char_type = 'd'

            if aliases_mask:
                if aliases_mask[-1] != char_type:
                    aliases_mask += char_type
            else:
                aliases_mask += char_type

            if char.isalpha():
                col_alias += char
            elif char.isdigit():
                row_alias += char
            else:
                raise Exception(f'Wrong char in ExcelCellPosition: "{char}"')

        if aliases_mask != 'cd':
            raise Exception(f'Wrong excel cell name format: "{cell_name}"')

        try:
            col = ExcelConstants.ALL_COLUMNS_LABELS.index(col_alias)
        except Exception:
            raise Exception(f'Wrong column name in ExcelCellPosition: "{col_alias}"')

        try:
            row = int(row_alias)
        except Exception:
            raise Exception(f'Wrong row number in ExcelCellPosition: "{col_alias}"')
        else:
            if row > ExcelConstants.MAX_EXCEL_ROWS_COUNT:
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
        return self.cell_position < other.cell_position

    def __le__(self, other):
        return self.cell_position <= other.cell_position

    def __eq__(self, other):
        return self.cell_position == other.cell_position

    def __add__(self, other):
        if not isinstance(other, CellOffset):
            raise Exception('The second operand must be instance of CellOffset class')
        new_cell_position = self.cell_position + other
        return ExcelCell(cell_name=new_cell_position.excel_cell)

    def __repr__(self):
        return f'ExcelCell(cell_name="{self._cell_name}")'


class ConditionChecker:
    def __init__(self, func, **kwargs):
        self._func = func
        self._kwargs = kwargs

    def check(self):
        return self._func(**self._kwargs)


class PositionFinderAbstract(ABC):
    def __init__(self, df: pd.DataFrame = None, sr: pd.Series = None):
        if (df is None and sr is None) or (df is not None and sr is not None):
            raise Exception('Either the "df" or "sr" must be specified')
        self._df = df
        self._sr = sr
        self.conditions = FinderConditionContainer()

    @abstractmethod
    def get_position(self): raise NotImplementedError

    def get_all_positions(self):
        return list(self.get_position())

    def __repr__(self):
        cls_name = self.__class__.__name__
        if self._df is not None:
            msg = f"{cls_name}(df)"
        else:
            msg = f"{cls_name}(sr)"
        return msg


class FilterDfAbstract(ABC):
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
    def _filter(self, *args, **kwargs): raise NotImplementedError

    def res(self, *args, **kwargs) -> pd.DataFrame:
        df = self._filter(*args, **kwargs)
        df.reset_index(inplace=True, drop=True)
        df.columns = range(df.shape[1])

        if self._fillna_res:
            df.fillna(0, inplace=True)
        return df

    def _filter_df_ltrb(self, start_position: CellPosition, end_position: CellPosition) -> pd.DataFrame:
        res_df = pd.DataFrame()
        if start_position and end_position and start_position <= end_position:
            row_slice = slice(start_position.row, end_position.row + 1)
            col_slice = slice(start_position.col, end_position.col + 1)
            res_df: pd.DataFrame = self._df.iloc[row_slice, col_slice]
        return res_df

    def __repr__(self):
        cls_name = self.__class__.__name__
        return f"{cls_name}(df)"


class NeighborCell:
    def __init__(self, df: pd.DataFrame, cell_value: CellValue, cell_offset: CellOffset):
        self._df = df
        self._cell_value = cell_value
        self._cell_offset = cell_offset

    def is_neighbor(self, cell: [CellPosition, ExcelCell]):
        if not isinstance(cell, (CellPosition, ExcelCell)):
            raise Exception('The "cell" must be instance of CellPosition or ExcelCell')

        new_cell_position = cell + self._cell_offset
        if new_cell_position.in_scope(df=self._df):
            new_raw_value = self._df.iloc[new_cell_position.row, new_cell_position.col]
            new_cell_value = CellValue(value=new_raw_value)
            res = self._cell_value == new_cell_value
        else:
            res = False
        return res

    def is_not_neighbor(self, cell: [CellPosition, ExcelCell]):
        return not self.is_neighbor(cell=cell)

    def __repr__(self):
        return f'NeighborCell(df, {self._cell_value.__repr__()}, {self._cell_offset.__repr__()})'
