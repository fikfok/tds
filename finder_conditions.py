

class FinderConditions:
    def __init__(self):
        self._exact_cell_value = None
        self._neighbors_cells = []
        self._cell_offset = None
        self._regex_cell_value_pattern = ''
        self._exact_cell_values = []
        self._is_condition_set = False

    @property
    def exact_cell_value(self):
        return self._exact_cell_value

    @exact_cell_value.setter
    def exact_cell_value(self, value):
        self._exact_cell_value = value
        self._is_condition_set = True

    @property
    def exact_cell_values(self):
        return self._exact_cell_values

    @exact_cell_values.setter
    def exact_cell_values(self, values):
        self._exact_cell_values = values
        self._is_condition_set = True

    @property
    def neighbors_cells(self):
        return self._neighbors_cells

    @neighbors_cells.setter
    def neighbors_cells(self, value):
        self._neighbors_cells = value
        self._is_condition_set = True

    @property
    def cell_offset(self):
        return self._cell_offset

    @cell_offset.setter
    def cell_offset(self, value):
        self._cell_offset = value
        self._is_condition_set = True

    @property
    def regex_cell_value_pattern(self):
        return self._regex_cell_value_pattern

    @regex_cell_value_pattern.setter
    def regex_cell_value_pattern(self, value):
        self._regex_cell_value_pattern = value
        self._is_condition_set = True

    # def get_conditions(self):
    #     """
    #     Здесь необходимо проверить не противоречат ли заданные выражения друг другу
    #     :return:
    #     """
    #     if not self._is_condition_set:
    #         raise Exception('Conditions not set')
    #
    #     if self._exact_cell_value and self._exact_cell_values:
    #         raise Exception('Either the "exact_cell_value" or "exact_cell_values" must be specified')
    #
    #     if self._regex_cell_value_pattern and self._exact_cell_value:
    #         raise Exception('Either the "regex_cell_value_pattern" or "exact_cell_value" must be specified')
    #
    #     if self._regex_cell_value_pattern and self._exact_cell_values:
    #         raise Exception('Either the "regex_cell_value_pattern" or "exact_cell_values" must be specified')
    #
    #     return self
