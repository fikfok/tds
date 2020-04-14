import pandas as pd

from commands import StartEndCellsByValueFilterDF, CellValue

with open('/home/fikfok/Downloads/Результат на 4ое задание.xlsx', 'rb') as xls:
    df = pd.read_excel(xls, sheet_name='ПП', header=None)

    filter = StartEndCellsByValueFilterDF(df=df)
    filter.start_cell_value = CellValue('SKU')
    filter.end_cell_value = CellValue(105153489.25)
    res_df = filter.res
