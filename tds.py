import pandas as pd

from commands import StartEndCellsByValueFilterDF, CellValue, StartEndCellsByValueOffsetFilterDF, CellOffset

with open('/home/fikfok/Downloads/Результат на 4ое задание.xlsx', 'rb') as xls:
    df = pd.read_excel(xls, sheet_name='ПП', header=None)

    filter = StartEndCellsByValueFilterDF(df=df)
    res_df = filter.res(CellValue('SKU'), CellValue(105153489.25))

    filter1 = StartEndCellsByValueOffsetFilterDF(df=df)
    res1_df = filter1.res(CellValue('SKU'), CellValue(6141), CellOffset(row=1, col=1), CellOffset(row=2, col=-1))
    a=1
