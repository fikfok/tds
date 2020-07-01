import itertools
from abc import ABC, abstractmethod
from enum import Enum
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


class IndexesMask(Enum):
    Wrong = -1
    OnlyChar = 1
    OnlyDigit = 2
    CharDigit = 3
    DigitChar = 4


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
        # return bool(self._col) or bool(self._row)
        return self._col is not None or self._row is not None

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
        for char in self._cell_name:
            if char.isalpha():
                col_alias += char
            elif char.isdigit():
                row_alias += char
            else:
                raise Exception(f'Wrong char in ExcelCellPosition: "{char}"')

        aliases_mask = self.get_aliases_mask(some_text=self._cell_name)
        if aliases_mask != IndexesMask.CharDigit:
            raise Exception(f'Wrong excel cell name format: "{cell_name}"')

        try:
            col = ExcelConstants.ALL_COLUMNS_LABELS.index(col_alias)
        except Exception:
            raise Exception(f'Wrong column name in ExcelCellPosition: "{col_alias}"')

        try:
            # Мало ли, лучше на всякий случай int() обернуть в try
            row = int(row_alias)
        except Exception:
            raise Exception(f'Wrong row number in ExcelCellPosition: "{row_alias}"')
        else:
            if row > ExcelConstants.MAX_EXCEL_ROWS_COUNT:
                raise Exception(f'Wrong row number in ExcelCellPosition: "{row_alias}"')

        row -= 1
        self._cell_position = CellPosition(col=col, row=row)

    @property
    def excel_cell(self) -> str:
        return self._cell_name

    @property
    def cell_position(self) -> CellPosition:
        return self._cell_position

    @staticmethod
    def get_aliases_mask(some_text: str) -> IndexesMask:
        """
        Возвращает краткое без дубликатов представление текстового аргумента
        :param some_text: или адрес одной ячейки или диапазон индексов (номера строк или названйи колонок)
        :return: маска индексов
        """
        aliases_mask = ''
        char_type = ''
        for char in some_text:
            if not char.isalpha() and not char.isdigit():
                aliases_mask = 'w'
                break

            if char.isalpha():
                char_type = 'c'
            elif char.isdigit():
                char_type = 'd'

            if aliases_mask:
                if aliases_mask[-1] != char_type:
                    aliases_mask += char_type
            else:
                aliases_mask += char_type

        if aliases_mask == 'c':
            res = IndexesMask.OnlyChar
        elif aliases_mask == 'd':
            res = IndexesMask.OnlyDigit
        elif aliases_mask == 'cd':
            res = IndexesMask.CharDigit
        elif aliases_mask == 'dc':
            res = IndexesMask.DigitChar
        else:
            res = IndexesMask.Wrong
        return res

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
        self.df = None
        self.sr = None

    @abstractmethod
    def get_all_indexes(self, axis: int): raise NotImplementedError


class CellOffsetAction:
    def __init__(self, cell_offset: CellOffset):
        self._df = None
        self._cell_offset = cell_offset

    def get_position(self, position: CellPosition) -> CellPosition:
        if self._df is None:
            raise Exception('_df must not be None')

        if position:
            res = position + self._cell_offset
            if not res.in_scope(df=self._df):
                res = CellPosition()
        else:
            res = CellPosition()
        return res


class PositionFinderAbstract(ABC):
    def __init__(self, df: pd.DataFrame = None, sr: pd.Series = None):
        if (df is None and sr is None) or (df is not None and sr is not None):
            raise Exception('Either the "df" or "sr" must be specified')
        self._df = df
        self._sr = sr
        self._value_finder = None
        self.neighbors_container = None
        self._cell_offset_action = None

    @property
    def value_finder(self):
        return self._value_finder

    @value_finder.setter
    def value_finder(self, other_value_finder: ValueFinderAbstract):
        self._value_finder = other_value_finder
        self._value_finder.df = self._df
        self._value_finder.sr = self._sr

    @property
    def cell_offset_action(self):
        return self._cell_offset_action

    @cell_offset_action.setter
    def cell_offset_action(self, other_cell_offset_action: CellOffsetAction):
        self._cell_offset_action = other_cell_offset_action
        self._cell_offset_action._df = self._df

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


class NeighborsContainer:
    def __init__(self, neighbors: [List[NeighborCell], NeighborCell]):
        if isinstance(neighbors, list):
            self._neighbors = neighbors
        else:
            self._neighbors = [neighbors]

    def is_neighbors_for(self, position: CellPosition) -> bool:
        res = False
        if position:
            is_neighbor = all([neighbor.is_neighbor(position) for neighbor in self._neighbors])
            if is_neighbor:
                res = True
            else:
                res = False
        return res


class Indexes:
    """
    Принимает на вход строку, в которой будут разного рода перечисления: и одиночные и диапазонные.
    Проверяет, приводит к отсортированному виду и раворачивает диапазоны.
    Обрабатывает как диапазоны строк так и столбцов.
    Может принимать или числа (для строк) или буквенные коды столбцов (для столбцов)
    """
    MAX_LENGTH = 100
    SIMPLE_DELIMITERS = [',', ' ']
    DIAPASON_DELIMITERS = ['-', ':']

    def __init__(self, indexes: str):
        self._indexes = indexes
        reason = self._is_correct()
        if reason:
            raise Exception(reason)

    def _is_correct(self) -> str:
        """
        Проверка на корректность всех перечисленных индексов
        """
        msg = ''
        checkers = [
            self._check_length,
            self._check_homogeneous,
            self._check_open_range,
            self._check_range_borders,
            self._check_in_scope,
        ]
        for checker in checkers:
            msg = checker()
            if msg:
                break
        return msg

    def _get_indexes_with_space_delimeters(self) -> str:
        """
        Заменить все разделители на пробелы, все пробелы заменить на одиночные, убрать пробелы сбоков
        """
        # Сначала необходимо сбоков убрать пробелы и символы разделителей
        indexes = self._indexes.strip()
        for delimiter in self.SIMPLE_DELIMITERS:
            indexes = indexes.strip(delimiter)
            # Заменить все разделители внутри на пробелы
            indexes = indexes.replace(delimiter, ' ')
        # В итоге в строке разделители заменены на пробелы и с боков нет пробелов и разделителей
        # Теперь надо повторяющиеся пробелы заменить на одиночные
        indexes = ' '.join(indexes.split())
        return indexes

    def _get_aliases_mask(self) -> IndexesMask:
        """
        Вернуть маску алиасов
        """
        wo_delimiters = self._indexes.replace(' ', '')
        for delimiter in self.SIMPLE_DELIMITERS + self.DIAPASON_DELIMITERS:
            wo_delimiters = wo_delimiters.replace(delimiter, '')
        aliases_mask = ExcelCell.get_aliases_mask(some_text=wo_delimiters)
        return aliases_mask

    def _check_length(self) -> str:
        """
        Проверка на длину
        """
        msg = ''
        wo_spaces = self._indexes.replace(' ', '')
        if len(wo_spaces) > self.MAX_LENGTH:
            msg = f'The string is too long. Limit is {self.MAX_LENGTH} symbols without spaces'
        return msg

    def _check_homogeneous(self) -> str:
        """
        Проверка на однородность: или числа или строки
        """
        msg = ''
        aliases_mask = self._get_aliases_mask()
        if aliases_mask not in [IndexesMask.OnlyChar, IndexesMask.OnlyDigit]:
            msg = 'Indexes must be only number or symbol'
        return msg

    def _check_open_range(self) -> str:
        """
        Отлов открытого диапазона слева или справа
        """
        msg = ''
        ideal_indexes = self._get_indexes_with_space_delimeters()
        ideal_indexes = ideal_indexes.split()
        for index in ideal_indexes:
            if index[0] in self.DIAPASON_DELIMITERS or index[-1] in self.DIAPASON_DELIMITERS:
                msg = f'Wrong index {index}'
        return msg

    def _check_range_borders(self) -> str:
        """
        Правильность диапазона: левая граница меньше чем правая
        """
        msg = ''
        aliases_mask = self._get_aliases_mask()
        ideal_indexes = self._get_indexes_with_space_delimeters()
        ideal_indexes = ideal_indexes.split()
        for index in ideal_indexes:
            for delimiter in self.DIAPASON_DELIMITERS:
                if delimiter in index:
                    left_index, right_index = index.split(delimiter)
                    if aliases_mask == IndexesMask.OnlyChar:
                        left_col_num = ExcelConstants.ALL_COLUMNS_LABELS.index(left_index)
                        rigth_col_num = ExcelConstants.ALL_COLUMNS_LABELS.index(right_index)
                        if left_col_num > rigth_col_num:
                            return f'Wrong borders of range: {index}'
                    else:
                        if int(left_index) > int(right_index):
                            return f'Wrong borders of range: {index}'
        return msg

    def _check_in_scope(self) -> str:
        """
        Проверка а вхождение всех индексов в диапазон разрешённых индексов
        """
        msg = ''
        aliases_mask = self._get_aliases_mask()
        ideal_indexes = self._get_indexes_with_space_delimeters()
        ideal_indexes = ideal_indexes.split()
        for index in ideal_indexes:
            for delimiter in self.DIAPASON_DELIMITERS:
                if delimiter in index:
                    left_index, right_index = index.split(delimiter)
                    if aliases_mask == IndexesMask.OnlyChar:
                        if left_index not in ExcelConstants.ALL_COLUMNS_LABELS:
                            return f'{left_index} not in columns scope'
                        if right_index not in ExcelConstants.ALL_COLUMNS_LABELS:
                            return f'{right_index} not in columns scope'
                    else:
                        if not (0 <= int(left_index) <= ExcelConstants.MAX_EXCEL_ROWS_COUNT):
                            return f'{left_index} not in rows scope'
                        if not (0 <= int(right_index) <= ExcelConstants.MAX_EXCEL_ROWS_COUNT):
                            return f'{right_index} not in rows scope'
                else:
                    if aliases_mask == IndexesMask.OnlyChar:
                        if index not in ExcelConstants.ALL_COLUMNS_LABELS:
                            return f'{index} not in columns scope'
                    else:
                        if not (0 <= int(index) <= ExcelConstants.MAX_EXCEL_ROWS_COUNT):
                            return f'{index} not in rows scope'
        return msg

    def _unpack_diapasones(self) -> list:
        """
        Распаковывает диапазоны. Возвращает список, в котором все индексы: и одиночные и распакованные диапазоны.
        Без сортировок и удалений дубликатов.
        """
        aliases_mask = self._get_aliases_mask()
        ideal_indexes = self._get_indexes_with_space_delimeters()
        ideal_indexes = ideal_indexes.split()
        for index in ideal_indexes:
            for delimiter in self.DIAPASON_DELIMITERS:
                if delimiter in index: