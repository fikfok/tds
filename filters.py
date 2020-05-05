from typing import List

from base_types import CellValue, CellPosition, CellOffset, ExcelCell, FilterDfAbstract, NeighborCell
from position_finders import FirstCellPositionFinder, FirstCellPositionFinderOffset, AllCellPositionsFinder


class ByValueLTRBFilterDF(FilterDfAbstract):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cell_pos_finder = FirstCellPositionFinder(df=self._df)

    def _filter(self, start_cell_value: CellValue, end_cell_value: CellValue):
        start_position = self.cell_pos_finder.get_position(start_cell_value)
        end_position = self.cell_pos_finder.get_position(end_cell_value)
        res_df = self._filter_df_ltrb(start_position, end_position)
        return res_df


class ByValueOffsetLTRBFilterDF(FilterDfAbstract):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cell_pos_finder_offset = FirstCellPositionFinderOffset(df=self._df)

    def _filter(self, start_cell_value: CellValue, end_cell_value: CellValue, start_pos_offset: CellOffset,
                end_pos_offset: CellOffset):
        start_position = self.cell_pos_finder_offset.get_position(start_cell_value, start_pos_offset)
        end_position = self.cell_pos_finder_offset.get_position(end_cell_value, end_pos_offset)
        res_df = self._filter_df_ltrb(start_position, end_position)
        return res_df


class ByPositionLTRBFilterDF(FilterDfAbstract):
    def _filter(self, start_position: CellPosition, end_position: CellPosition):
        if not isinstance(start_position, CellPosition) or not isinstance(end_position, CellPosition):
            raise Exception('The start and the end positions must be instance of CellPosition')
        res_df = self._filter_df_ltrb(start_position, end_position)
        return res_df


class ByExcelCellLTRBFilterDF(FilterDfAbstract):
    def _filter(self, start_position: ExcelCell, end_position: ExcelCell):
        if not isinstance(start_position, ExcelCell) or not isinstance(end_position, ExcelCell):
            raise Exception('The start and the end positions must be instance of ExcelCell')
        res_df = self._filter_df_ltrb(start_position.cell_position, end_position.cell_position)
        return res_df


class ByValueNeighborhoodsLTRBFilterDF(FilterDfAbstract):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cell_pos_finder = AllCellPositionsFinder(df=self._df)

    def _filter(self, start_cell_value: CellValue, start_cell_neighbors: List[NeighborCell],
                end_cell_value: CellValue, end_cell_neighbors: List[NeighborCell]):

        _start_position = CellPosition()
        for start_position in self.cell_pos_finder.get_position(start_cell_value):
            neighbors_on_places = all([neighbor.is_neighbor(start_position) for neighbor in start_cell_neighbors])
            if neighbors_on_places:
                _start_position = start_position
                break

        _end_position = CellPosition()
        for end_position in self.cell_pos_finder.get_position(end_cell_value):
            neighbors_on_places = all([neighbor.is_neighbor(end_position) for neighbor in start_cell_neighbors])
            if neighbors_on_places:
                _end_position = end_position
                break

        res_df = self._filter_df_ltrb(_start_position, _end_position)
        return res_df
