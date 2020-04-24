from base_types import CellValue, CellPosition, CellOffset, ExcelCell, FilterDfAbstract
from position_finders import FirstCellPositionFinder, FirstCellPositionFinderOffset


class StartEndCellsByValueFilterDF(FilterDfAbstract):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cell_pos_finder = FirstCellPositionFinder(df=self._df)

    def _filter(self, start_cell_value: CellValue, end_cell_value: CellValue):
        start_position = self.cell_pos_finder.res(start_cell_value)
        end_position = self.cell_pos_finder.res(end_cell_value)
        res_df = self._filter_df_by_positions(start_position, end_position)
        return res_df


class StartEndCellsByValueOffsetFilterDF(FilterDfAbstract):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cell_pos_finder_offset = FirstCellPositionFinderOffset(df=self._df)

    def _filter(self, start_cell_value: CellValue, end_cell_value: CellValue, start_pos_offset: CellOffset,
                end_pos_offset: CellOffset):
        start_position = self.cell_pos_finder_offset.res(start_cell_value, start_pos_offset)
        end_position = self.cell_pos_finder_offset.res(end_cell_value, end_pos_offset)
        res_df = self._filter_df_by_positions(start_position, end_position)
        return res_df


class ByPositionLeftTopRightBottomFilterDF(FilterDfAbstract):
    def _filter(self, start_position: CellPosition, end_position: CellPosition):
        if not isinstance(start_position, CellPosition) or not isinstance(end_position, CellPosition):
            raise Exception('The start and the end positions must be instance of CellPosition')
        res_df = self._filter_df_by_positions(start_position, end_position)
        return res_df


class ByExcelCellLeftTopRightBottomFilterDF(FilterDfAbstract):
    def _filter(self, start_position: ExcelCell, end_position: ExcelCell):
        if not isinstance(start_position, ExcelCell) or not isinstance(end_position, ExcelCell):
            raise Exception('The start and the end positions must be instance of ExcelCell')
        res_df = self._filter_df_by_positions(start_position.cell_position, end_position.cell_position)
        return res_df
