from abc import ABC, abstractmethod
from typing import List

import numpy as np
import pandas as pd

from base_types import CellValue, CellPosition, CellOffset, NeighborCell


class FinderConditionAbstract(ABC):
    condition_type = ''

    def __init__(self, **kwargs):
        df = kwargs.get('df')
        sr = kwargs.get('sr')
        if (df is None and sr is None) or (df is not None and sr is not None):
            raise Exception('Either the "df" or "sr" must be specified')
        self._df = df
        self._sr = sr

    @abstractmethod
    def get_all_indexes(self, axis: int): raise NotImplementedError


class ExactCellValueCondition(FinderConditionAbstract):
    condition_type = 'exact_cell_value'

    def __init__(self, cell_value: CellValue, **kwargs):
        self._cell_value = cell_value
        super().__init__(**kwargs)

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


class ExactCellValuesCondition(FinderConditionAbstract):
    condition_type = 'exact_cell_values'

    def __init__(self, cell_values: List[CellValue], **kwargs):
        self._cell_values = cell_values
        super().__init__(**kwargs)

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


class RegexCondition(FinderConditionAbstract):
    condition_type = 'regex'

    def __init__(self, cell_value: CellValue, **kwargs):
        self._cell_value = cell_value
        super().__init__(**kwargs)

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


class FinderConditionContainer:
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
        Добавляет смещение и/или соседа
        :param action: действие (смещение или сосед)
        """
        if len(self._actions) >= self.MAX_ACTIONS_COUNT:
            raise Exception(f'The action limit has reached {self.MAX_ACTIONS_COUNT}')
        self._actions.append(action)

