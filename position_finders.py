from base_types import PositionFinderAbstract, CellValue, CellPosition, CellOffset


class AllRowNumsFinder(PositionFinderAbstract):
    def get_position(self) -> CellPosition:
        for row in self._get_all_indexes(axis=1):
            yield CellPosition(row=row)


class AllColNumsFinder(PositionFinderAbstract):
    def get_position(self) -> CellPosition:
        for col in self._get_all_indexes(axis=0):
            yield CellPosition(col=col)


class AllCellPositionsFinder(PositionFinderAbstract):
    def get_position(self) -> CellPosition:
        row_num_finder = AllRowNumsFinder(df=self._df)
        row_num_finder.conditions = self.conditions
        for row_position in row_num_finder.get_position():
            col_num_finder = AllColNumsFinder(sr=self._df.iloc[row_position.row, :])
            col_num_finder.conditions = self.conditions
            for col_position in col_num_finder.get_position():
                position = row_position + col_position

                # Здесь очень важен порядок. Сначала надо сместить положение, а только потом проверять соседа новой
                # ячейки
                if self.conditions.cell_offset:
                    position += self.conditions.cell_offset
                    if not position.in_scope(df=self._df):
                        continue

                if self.conditions.neighbors_cells:
                    is_neighbor = all([neighbor.is_neighbor(position) for neighbor in self.conditions.neighbors_cells])
                    if is_neighbor:
                        yield position
                else:
                    yield position


class FirstRowNumFinder(PositionFinderAbstract):
    def get_position(self) -> CellPosition:
        if self._df is not None:
            row_num_finder = AllRowNumsFinder(df=self._df)
        else:
            row_num_finder = AllRowNumsFinder(sr=self._sr)

        row_num_finder.conditions = self.conditions
        for row_position in row_num_finder.get_position():
            # Была найдена первая строка
            result = row_position
            break
        else:
            # Ничего не найдено, т.е. генератор пуст
            result = CellPosition()
        return result


class FirstColNumFinder(PositionFinderAbstract):
    def get_position(self) -> CellPosition:
        if self._df is not None:
            col_num_finder = AllColNumsFinder(df=self._df)
        else:
            col_num_finder = AllColNumsFinder(sr=self._sr)

        col_num_finder.conditions = self.conditions
        for col_position in col_num_finder.get_position():
            # Был найден первый столбец
            result = col_position
            break
        else:
            # Ничего не найдено, т.е. генератор пуст
            result = CellPosition()
        return result


class FirstCellPositionFinder(PositionFinderAbstract):
    def get_position(self) -> CellPosition:
        row_num_finder = FirstRowNumFinder(df=self._df)
        row_num_finder.conditions = self.conditions
        row_position = row_num_finder.get_position()
        col_num_finder = FirstColNumFinder(sr=self._df.iloc[row_position.row, :])
        col_num_finder.conditions = self.conditions
        return row_position + col_num_finder.get_position()



# НЕАКТУАЛЬНО УДАЛИТЬ!!!
class FirstCellPositionFinderOffset(FirstCellPositionFinder):
    def get_position(self) -> CellPosition:
        if self._cell_offset is None:
            raise Exception('The "cell_offset" is not set')

        return super().get_position() + self._cell_offset
