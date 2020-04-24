from base_types import PositionFinderAbstract, CellValue, CellPosition, CellOffset


class RowNumFinder(PositionFinderAbstract):
    def res(self, cell_value: CellValue) -> CellPosition:
        # return self._df[self._df.eq(self._cell_value.value).any(axis=1)].index[0]
        if self._df is not None:
            row = self._df[self._df.eq(cell_value.value)].any(axis=1).idxmax()
        else:
            row = self._sr.eq(cell_value.value).idxmax()
        return CellPosition(row=row)


class ColNumFinder(PositionFinderAbstract):
    def res(self, cell_value: CellValue) -> CellPosition:
        if self._df is not None:
            col = self._df[self._df.eq(cell_value.value)].any(axis=0).idxmax()
        else:
            col = self._sr.eq(cell_value.value).idxmax()
        return CellPosition(col=col)


class FirstCellPositionFinder(PositionFinderAbstract):
    def res(self, cell_value: CellValue) -> CellPosition:
        row_num_finder = RowNumFinder(df=self._df)
        row_position = row_num_finder.res(cell_value)
        col_num_finder = ColNumFinder(sr=self._df.iloc[row_position.row, :])
        return row_position + col_num_finder.res(cell_value)


class FirstCellPositionFinderOffset(FirstCellPositionFinder):
    def res(self, cell_value: CellValue, cell_offset: CellOffset) -> CellPosition:
        return super().res(cell_value) + cell_offset
