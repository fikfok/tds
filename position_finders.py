from base_types import PositionFinderAbstract, CellValue, CellPosition, CellOffset


class AllRowNumsFinder(PositionFinderAbstract):
    def res(self, cell_value: CellValue) -> CellPosition:
        for row in self._get_all_indexes_by_axis(cell_value=cell_value, axis=1):
            yield CellPosition(row=row)


class AllColNumsFinder(PositionFinderAbstract):
    def res(self, cell_value: CellValue) -> CellPosition:
        for col in self._get_all_indexes_by_axis(cell_value=cell_value, axis=0):
            yield CellPosition(col=col)


class FirstRowNumFinder(PositionFinderAbstract):
    def res(self, cell_value: CellValue) -> CellPosition:
        row = self._get_first_index_by_axis(cell_value=cell_value, axis=1)
        return CellPosition(row=row)


class FirstColNumFinder(PositionFinderAbstract):
    def res(self, cell_value: CellValue) -> CellPosition:
        col = self._get_first_index_by_axis(cell_value=cell_value, axis=0)
        return CellPosition(col=col)


class FirstCellPositionFinder(PositionFinderAbstract):
    def res(self, cell_value: CellValue) -> CellPosition:
        row_num_finder = FirstRowNumFinder(df=self._df)
        row_position = row_num_finder.res(cell_value)
        col_num_finder = FirstColNumFinder(sr=self._df.iloc[row_position.row, :])
        return row_position + col_num_finder.res(cell_value)


class FirstCellPositionFinderOffset(FirstCellPositionFinder):
    def res(self, cell_value: CellValue, cell_offset: CellOffset) -> CellPosition:
        return super().res(cell_value) + cell_offset
