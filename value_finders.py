from typing import List

import numpy as np
import pandas as pd
from pandas.core.dtypes.common import is_string_dtype

from base_types import ValueFinderAbstract, CellValue


class ExactValueFinder(ValueFinderAbstract):
    condition_type = 'exact_cell_value'

    def __init__(self, cell_value: CellValue):
        self._cell_value = cell_value
        super().__init__()

    def get_all_indexes(self, axis: int) -> np.array:
        if self._cell_value:
            # cell_value не пустое значение
            if self.df is not None:
                seria = self.df[self.df.eq(self._cell_value.value)].notna().any(axis=axis)
            else:
                seria = self.sr.eq(self._cell_value.value)
        else:
            # exact_cell_value пустое значение.
            # Пустым значением могут быть варианты: '', None, np.NaN.
            # С None и np.NaN функция .isnull() справится, т.е. поставит True в нужную позицию.
            # А вот с '' не справится и поставит False. Потому предварительно '' необходимо заменить на None.
            if self.df is not None:
                seria = self.df.replace(to_replace={'': None}).isnull().any(axis=axis)
            else:
                seria = self.sr.replace(to_replace={'': None}).isnull()

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
            if self.df is not None:
                seria_nulls = self.df.replace(to_replace={'': None}).isnull().any(axis=axis)
            else:
                seria_nulls = self.sr.replace(to_replace={'': None}).isnull()

        if len(values_wo_nulls):
            # В списке есть реальные значения
            if self.df is not None:
                seria_wo_nulls = self.df[self.df.isin(values_wo_nulls)].notna().any(axis=axis)
            else:
                seria_wo_nulls = self.sr.isin(values_wo_nulls)

        if seria_nulls is not None and seria_wo_nulls is not None:
            seria = seria_nulls + seria_wo_nulls
        elif seria_nulls is not None and seria_wo_nulls is None:
            seria = seria_nulls
        else:
            seria = seria_wo_nulls
        res = seria[seria].index.values
        return res


class RegexFinder(ValueFinderAbstract):
    """
    Only for string columns
    """
    condition_type = 'regex'

    def __init__(self, cell_value: CellValue):
        self._cell_value = cell_value
        super().__init__()

    def get_all_indexes(self, axis: int) -> np.array:
        pattern = self._cell_value.value
        if self.df is not None:
            seria = self.df. \
                apply(lambda s: s.astype(str).str.match(pattern, na=False) if is_string_dtype(s) else False). \
                any(axis=axis)
        else:
            # Т.к. это regex, то необходимо обязательно конвертировать в строку
            seria = self.sr.astype(str).str.match(pattern, na=False)
        res = seria[seria].index.values
        return res


class StartWithFinder(ValueFinderAbstract):
    condition_type = 'start_with'

    def __init__(self, cell_value: CellValue):
        self._cell_value = cell_value
        super().__init__()

    def get_all_indexes(self, axis: int) -> np.array:
        value = self._cell_value.value
        if self.df is not None:
            seria = self.df. \
                apply(lambda s: s.astype(str).str.startswith(value, na=False) if is_string_dtype(s) else False). \
                any(axis=axis)
        else:
            seria = self.sr.str.startswith(value, na=False)
        res = seria[seria].index.values
        return res


class EndWithFinder(ValueFinderAbstract):
    condition_type = 'end_with'

    def __init__(self, cell_value: CellValue):
        self._cell_value = cell_value
        super().__init__()

    def get_all_indexes(self, axis: int) -> np.array:
        value = self._cell_value.value
        if self.df is not None:
            seria = self.df. \
                apply(lambda s: s.astype(str).str.endswith(value, na=False) if is_string_dtype(s) else False). \
                any(axis=axis)
        else:
            seria = self.sr.str.endswith(value, na=False)
        res = seria[seria].index.values
        return res