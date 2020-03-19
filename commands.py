from abc import abstractmethod

import pandas as pd


class CellValue:
    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value


class Command:
    def __init__(self, df: pd.DataFrame):
        self._df = df
        self._cell_value = None

    @abstractmethod
    def res(self): raise NotImplementedError

    @property
    def cell_value(self):
        if self._cell_value is None:
            raise Exception('Value is None')
        return self._cell_value

    @property
    def raw_cell_value(self):
        if self._cell_value is None:
            raise Exception('Value is None')
        return self._cell_value.value

    @cell_value.setter
    def cell_value(self, cell_value: CellValue):
        self._cell_value = cell_value


class CellPosition:
    def __init__(self, row: int, col: int):
        self._row = row
        self._col = col

    @property
    def row(self):
        return self._row

    @property
    def col(self):
        return self.col

    def __lt__(self, other):
        return (self._row > other.row and self._col >= other.col) or \
               (self._row >= other.row and self._col > other.col)

    def __le__(self, other):
        return self._row >= other.row and self._col >= other.col

    def __eq__(self, other):
        return self._row == other.row and self._col == other.col


class RowNumFinder(Command):
    @property
    def res(self) -> int:
        # return self._df[self._df.eq(self._cell_value.value).any(axis=1)].index[0]
        return self._df[self._df.eq(self.raw_cell_value)].any(axis=1).idxmax()


class ColNumFinder(Command):
    @property
    def res(self) -> int:
        return self._df[self._df.eq(self.raw_cell_value)].any(axis=0).idxmax()


class CellPositionFinder(Command):
    @property
    def res(self) -> CellPosition:
        row_num = RowNumFinder(df=self._df)
        row_num.cell_value = self.cell_value
        col_num = ColNumFinder(df=self._df)
        col_num.value = self.cell_value
        return CellPosition(row=row_num.res, col=col_num.res)


class StartEndCellsByValueFilterDF(Command):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._start_cell_value = None
        self._end_cell_value = None
        self._start_position = None
        self._end_position = None

    @property
    def start_cell_value(self):
        return self._start_cell_value

    @start_cell_value.setter
    def start_cell_value(self, cell_value: CellValue):
        self._start_cell_value = cell_value
        finder = CellPositionFinder(df=self._df)
        finder.cell_value = self._start_cell_value
        self._start_position = finder.res

    @property
    def end_cell_value(self):
        return self._end_cell_value

    @end_cell_value.setter
    def end_cell_value(self, cell_value: CellValue):
        self._end_cell_value = cell_value
        finder = CellPositionFinder(df=self._df)
        finder.cell_value = self._end_cell_value
        self._end_position = finder.res

    @property
    def res(self):
        res_df = pd.DataFrame()
        if self._start_position <= self._end_position:
            row_slice = slice(self._start_position.row, self._end_position.row)
            col_slice = slice(self._start_position.col, self._end_position.col)
            res_df = self._df.iloc[row_slice, col_slice]
        return res_df
