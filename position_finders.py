from base_types import PositionFinderAbstract, CellValue, CellPosition, CellOffset


class AllRowNumsFinder(PositionFinderAbstract):
    def res(self, cell_value: CellValue) -> CellPosition:
        for row in self._get_all_indexes_by_axis(cell_value=cell_value, axis=1):
            yield CellPosition(row=row)


class AllColNumsFinder(PositionFinderAbstract):
    def res(self, cell_value: CellValue) -> CellPosition:
        for col in self._get_all_indexes_by_axis(cell_value=cell_value, axis=0):
            yield CellPosition(col=col)


class AllCellPositionsFinder(PositionFinderAbstract):
    def res(self, cell_value: CellValue) -> CellPosition:
        row_num_finder = AllRowNumsFinder(df=self._df)
        for row_position in row_num_finder.res(cell_value=cell_value):
            col_num_finder = AllColNumsFinder(sr=self._df.iloc[row_position.row, :])
            for col_position in col_num_finder.res(cell_value=cell_value):
                yield row_position + col_position


class FirstRowNumFinder(PositionFinderAbstract):
    def res(self, cell_value: CellValue) -> CellPosition:
        if self._df is not None:
            row_num_finder = AllRowNumsFinder(df=self._df)
        else:
            row_num_finder = AllRowNumsFinder(sr=self._sr)
        for row_position in row_num_finder.res(cell_value=cell_value):
            # Была найдена первая строка
            result = row_position
            break
        else:
            # Ничего не найдено, т.е. генератор пуст
            result = CellPosition()
        return result


class FirstColNumFinder(PositionFinderAbstract):
    def res(self, cell_value: CellValue) -> CellPosition:
        if self._df is not None:
            col_num_finder = AllColNumsFinder(df=self._df)
        else:
            col_num_finder = AllColNumsFinder(sr=self._sr)
        for col_position in col_num_finder.res(cell_value=cell_value):
            # Был найден первый столбец
            result = col_position
            break
        else:
            # Ничего не найдено, т.е. генератор пуст
            result = CellPosition()
        return result


class FirstCellPositionFinder(PositionFinderAbstract):
    def res(self, cell_value: CellValue) -> CellPosition:
        row_num_finder = FirstRowNumFinder(df=self._df)
        row_position = row_num_finder.res(cell_value)
        col_num_finder = FirstColNumFinder(sr=self._df.iloc[row_position.row, :])
        return row_position + col_num_finder.res(cell_value)


class FirstCellPositionFinderOffset(FirstCellPositionFinder):
    def res(self, cell_value: CellValue, cell_offset: CellOffset) -> CellPosition:
        return super().res(cell_value) + cell_offset
