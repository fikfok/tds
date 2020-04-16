import pandas as pd

from commands import StartEndCellsByValueFilterDF, CellValue, StartEndCellsByValueOffsetFilterDF, CellOffset

with open('/home/fikfok/Downloads/Результат на 4ое задание.xlsx', 'rb') as xls:
    df = pd.read_excel(xls, sheet_name='ПП', header=None)

    filter = StartEndCellsByValueFilterDF(df=df)
    filter.start_cell_value = CellValue('SKU')
    filter.end_cell_value = CellValue(105153489.25)
    res_df = filter.res

    filter1 = StartEndCellsByValueOffsetFilterDF(df=df)
    filter1.start_cell_value = CellValue('SKU')
    filter1.end_cell_value = CellValue(105153489.25)
    filter1.start_position_offset = CellOffset(row=1, col=1)
    filter1.end_position_offset = CellOffset(row=2, col=-1)
    res1_df = filter1.res
    a=1
