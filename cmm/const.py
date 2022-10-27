from django.conf.global_settings import LANGUAGES as ORIGINAL_LANGUAGES


UTF8 = 'UTF-8'
SJIS = 'SHIFT-JIS'

# Code Category
SEX = 'sex'
ORG_RANK = 'org_rank'

# Export&Import
EXPORT_CSV = 'export_csv'
IMPORT_CSV = 'import_csv'
CSV_FILE_EXT = '.csv'

EXPORT_EXCEL = 'export_excel'
IMPORT_EXCEL = 'import_excel'
EXCEL_FILE_EXT = '.xlsx'

# Languages
LANGUAGES = [lang for lang in ORIGINAL_LANGUAGES if lang[0] in ('en', 'ja', 'zh-hans')]
