import itertools
from abc import ABC, abstractmethod
from typing import List

import numpy as np
import pandas as pd


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


class ValueFinderAbstract(ABC):
    condition_type = ''

    def __init__(self):
        self._df = None
        self._sr = None

    @property
    def df(self):
        return self._df

    @df.setter
    def df(self, other_df: pd.DataFrame):
        self._df = other_df

    @property
    def sr(self):
        return self._sr

    @sr.setter
    def sr(self, other_sr: pd.Series):
        self._sr = other_sr

    @abstractmethod
    def get_all_indexes(self, axis: int): raise NotImplementedError


class PositionFinderAbstract(ABC):
    def __init__(self, df: pd.DataFrame = None, sr: pd.Series = None):
        if (df is None and sr is None) or (df is not None and sr is not None):
            raise Exception('Either the "df" or "sr" must be specified')
        self._df = df
        self._sr = sr
        self._value_finder = None

    @property
    def value_finder(self):
        return self._value_finder

    @value_finder.setter
    def value_finder(self, other_value_finder: ValueFinderAbstract):
        self._value_finder = other_value_finder
        self._value_finder.df = self._df
        self._value_finder.sr = self._sr

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


class ExactValueFinder(ValueFinderAbstract):
    condition_type = 'exact_cell_value'

    def __init__(self, cell_value: CellValue):
        self._cell_value = cell_value
        super().__init__()

    def get_all_indexes(self, axis: int) -> np.array:
        if self._cell_value:
            # cell_value не пустое значение
            if self._df is not None:
                seria = self._df[self._df.eq(self._cell_value.value)].notna().any(axis=axis)
            else:
                seria = self._sr.eq(self._cell_value.value)
        else:
            # exact_cell_value пустое значение.
            # Пустым значением могут быть варианты: '', None, np.NaN.
            # С None и np.NaN функция .isnull() справится, т.е. поставит True в нужную позицию.
            # А вот с '' не справится и поставит False. Потому предварительно '' необходимо заменить на None.
            if self._df is not None:
                seria = self._df.replace(to_replace={'': None}).isnull().any(axis=axis)
            else:
                seria = self._sr.replace(to_replace={'': None}).isnull()

        res = seria[seria].index.values
        return res


class ExactValuesFinder(ValueFinderAbstract):
    condition_type = 'exact_cell_values'

    def __init__(self, cell_values: List[CellValue]):
        self._cell_values = cell_values
        super().__init__()

    def get_all_indexes(self, axis: int) -> np.array:
        values = list(set([cell_value.value for cell_value in self._cell_values]))
        values_wo_nulls = [value for value in values if not pd.isnull(value)]
        empty_value_exists = any(pd.isnull(values))
        seria_nulls = None
        seria_wo_nulls = None
        if empty_value_exists:
            # В списке есть пустое значение, значит предстоит проверка на пустое значение. Значит необходимо
            # '' заменить на None в df
            if self._df is not None:
                seria_nulls = self._df.replace(to_replace={'': None}).isnull().any(axis=axis)
            else:
                seria_nulls = self._sr.replace(to_replace={'': None}).isnull()

        if len(values_wo_nulls):
            # В списке есть реальные значения
            if self._df is not None:
                seria_wo_nulls = self._df[self._df.isin(values_wo_nulls)].notna().any(axis=axis)
            else:
                seria_wo_nulls = self._sr.isin(values_wo_nulls)

        if seria_nulls is not None and seria_wo_nulls is not None:
            seria = seria_nulls + seria_wo_nulls
        elif seria_nulls is not None and seria_wo_nulls is None:
            seria = seria_nulls
        else:
            seria = seria_wo_nulls
        res = seria[seria].index.values
        return res


class RegexFinder(ValueFinderAbstract):
    condition_type = 'regex'

    def __init__(self, cell_value: CellValue):
        self._cell_value = cell_value
        super().__init__()

    def get_all_indexes(self, axis: int) -> np.array:
        pattern = self._cell_value.value
        if self._df is not None:
            seria = self._df.apply(lambda seria: seria.astype(str).str.match(pattern)).any(axis=axis)
        else:
            seria = self._sr.astype(str).str.match(pattern)
        res = seria[seria].index.values
        return res


class ActionAbstract(ABC):
    """
    Выполняет действие над ячейкой
    """
    @abstractmethod
    def __init__(self, **kwargs): raise NotImplementedError

    @abstractmethod
    def execute(self, **kwargs): raise NotImplementedError


class CellOffsetAction(ActionAbstract):
    def __init__(self, df: pd.DataFrame, cell_offset: CellOffset):
        self._df = df
        self._cell_offset = cell_offset

    def execute(self, position: CellPosition):
        if position:
            res = position + self._cell_offset
            if not res.in_scope(df=self._df):
                res = CellPosition()
        else:
            res = CellPosition()
        return res


class NeighborsAction(ActionAbstract):
    def __init__(self, df: pd.DataFrame, neighbors: [List[NeighborCell], NeighborCell]):
        self._df = df
        if isinstance(neighbors, list):
            self._neighbors = neighbors
        else:
            self._neighbors = [neighbors]

    def execute(self, position: CellPosition):
        if position:
            is_neighbor = all([neighbor.is_neighbor(position) for neighbor in self._neighbors])
            if is_neighbor:
                res = position
            else:
                res = CellPosition()
        else:
            res = CellPosition()
        return res


class ConditionContainer:
    """
    Содержит искателя ячейки и разный набор действий (смещения или поиск соседа).
    """
    MAX_ACTIONS_COUNT = 10

    def __init__(self):
        self._actions = []
        self._cell_finder = None

    @property
    def cell_finder(self):
        if self._cell_finder is None:
            raise Exception('Cell finder is empty')
        return self._cell_finder

    @cell_finder.setter
    def cell_finder(self, cell_finder):
        self._cell_finder = cell_finder

    @property
    def actions(self):
        return self._actions

    def add_action(self, action):
        """
        Добавляет действие
        :param action: действие (смещение или сосед)
        """
        if len(self._actions) >= self.MAX_ACTIONS_COUNT:
            raise Exception(f'The action limit has reached {self.MAX_ACTIONS_COUNT}')
        self._actions.append(action)

