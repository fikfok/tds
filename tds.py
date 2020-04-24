from base_types import CellValue, CellOffset, ExcelCell, ExcelDataProvider
from filters import ByExcelCellLeftTopRightBottomFilterDF

file_path = '/home/fikfok/Downloads/Результат на 4ое задание.xlsx'
sheet_name = 'ПП'
provider = ExcelDataProvider(file_path=file_path)
df = provider.get_df(sheet_name=sheet_name)
#
# filter = StartEndCellsByValueFilterDF(df=df)
# res_df = filter.res(CellValue('SKU'), CellValue(105153489.25))
#
# filter1 = StartEndCellsByValueOffsetFilterDF(df=df)
# res1_df = filter1.res(CellValue('SKU'), CellValue(6141), CellOffset(row=1, col=1), CellOffset(row=2, col=-1))

filter2 = ByExcelCellLeftTopRightBottomFilterDF(df=df)
res2_df = filter2.res(ExcelCell(cell_name='B5'), ExcelCell(cell_name='H209'))
res2_df[2] = res2_df[2].astype(int)
res2_df[3] = res2_df[3].astype(int)
res2_df[4] = res2_df[4].astype(int)
res2_df[5] = res2_df[5].astype(int)
a=1
