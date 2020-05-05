from abc import ABC, abstractmethod

import pandas as pd


class DataProviderAbstract(ABC):
    """
    Читает данные из файла и возвращает df
    """
    @abstractmethod
    def __init__(self):
        raise NotImplementedError

    @abstractmethod
    def get_df(self) -> pd.DataFrame:
        raise NotImplementedError


class ExcelDataProvider(DataProviderAbstract):
    def __init__(self, file_path: str):
        self._file_path = file_path

    def get_df(self, sheet_name: str) -> pd.DataFrame:
        with open(self._file_path, 'rb') as xls:
            self._df = pd.read_excel(xls, sheet_name=sheet_name, header=None)
        return self._df