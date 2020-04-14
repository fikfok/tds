from abc import ABC, abstractmethod

import pandas as pd


class CellValue:
    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value

    def __str__(self):
        return self._value

    def __repr__(self):
        return f'CellValue({self._value})'


class Command:
    def __init__(self, df: pd.DataFrame):
        self._df = df
        self._cell_value = None
        self._fillna_res = True

    @abstractmethod
    def res(self): raise NotImplementedError

    @property
    def fillna_res(self):
        return self._fillna_res

    @fillna_res.setter
    def fillna_res(self, value: bool):
        self._fillna_res = value

    @property
    def cell_value(self):
        if self._cell_value is None:
            raise Exception('Value is None')
        return self._cell_value

    @cell_value.setter
    def cell_value(self, cell_value: CellValue):
        self._cell_value = cell_value

    @property
    def raw_cell_value(self):
        """
        Возвращает изначальное искомое значение
        """
        if self._cell_value is None:
            raise Exception('Value is None')
        return self._cell_value.value

    def __repr__(self):
        cls_name = self.__class__.__name__
        return f"{cls_name}(df, '{self.raw_cell_value}')"


class CellPosition:
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
        _col = None
        _row = None
        if self._col and other.col:
            _col = self._col + other.col
        elif self._col is None and other.col:
            _col = other.col
        elif self._col and other.col is None:
            _col = self._col

        if self._row and other.row:
            _row = self._row + other.row
        elif self._row is None and other.row:
            _row = other.row
        elif self._row and other.row is None:
            _row = self._row

        return CellPosition(col=_col, row=_row)

    def __repr__(self):
        return f'CellPosition(col={self._col}, row={self._row})'


class RowNumFinder(Command):
    @property
    def res(self) -> CellPosition:
        # return self._df[self._df.eq(self._cell_value.value).any(axis=1)].index[0]
        row = self._df[self._df.eq(self.raw_cell_value)].any(axis=1).idxmax()
        return CellPosition(row=row)


class ColNumFinder(Command):
    @property
    def res(self) -> CellPosition:
        col = self._df[self._df.eq(self.raw_cell_value)].any(axis=0).idxmax()
        return CellPosition(col=col)


class CellPositionFinder(Command):
    @property
    def res(self) -> CellPosition:
        row_num_finder = RowNumFinder(df=self._df)
        row_num_finder.cell_value = self._cell_value
        col_num_finder = ColNumFinder(df=self._df)
        col_num_finder.cell_value = self._cell_value
        return row_num_finder.res + col_num_finder.res


class StartEndCellsByValueFilterDF(Command):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._start_cell_value = None
        self._end_cell_value = None
        self._start_position = None
        self._end_position = None
        self.cell_pos_finder = CellPositionFinder(df=self._df)

    @property
    def start_cell_value(self):
        return self._start_cell_value

    @start_cell_value.setter
    def start_cell_value(self, cell_value: CellValue):
        self._start_cell_value = cell_value

    @property
    def end_cell_value(self):
        return self._end_cell_value

    @end_cell_value.setter
    def end_cell_value(self, cell_value: CellValue):
        self._end_cell_value = cell_value

    @property
    def res(self):
        res_df = pd.DataFrame()
        self.cell_pos_finder.cell_value = self._start_cell_value
        self._start_position = self.cell_pos_finder.res

        self.cell_pos_finder.cell_value = self._end_cell_value
        self._end_position = self.cell_pos_finder.res

        if self._start_position <= self._end_position:
            row_slice = slice(self._start_position.row, self._end_position.row + 1)
            col_slice = slice(self._start_position.col, self._end_position.col + 1)
            res_df: pd.DataFrame = self._df.iloc[row_slice, col_slice]
            if self._fillna_res:
                res_df.fillna(0, inplace=True)
        return res_df
