import json
from django.db import models
from django.utils.translation import gettext_lazy as _


class CsvLog(models.Model):
    """Csv import&export log"""
    INFO = 'info'           # 正常インポート
    WARN = 'warn'           # 読み飛ばし
    ERROR = 'error'         # 読み込みエラー

    LEVEL_CHOICES = [
        (INFO, _('Information')),
        (WARN, _('Warning')),
        (ERROR, _('Error')),
    ]

    IMPORT = 'import'
    EXPORT = 'export'

    TYPE_CHOICES = [
        (IMPORT, _('Csv Import')),
        (EXPORT, _('Csv Export')),
    ]

    INSERT = 'insert'
    UPDATE = 'update'
    
    EDIT_CHOICES = [
        (INSERT, _('insert')),
        (UPDATE, _('update')),
    ]
    
    """CSV import, exportのログ情報"""
    log_level = models.CharField(max_length = 5, choices=LEVEL_CHOICES, blank = False,
                                 default=INFO, verbose_name = _('csv log level'))
    log_type = models.CharField(max_length=12, choices=TYPE_CHOICES, blank=False, default=IMPORT,
                                verbose_name=_('csv log type'))
    edit_type = models.CharField(max_length=12, choices=EDIT_CHOICES, blank=False, default=INSERT,
                                verbose_name=_('csv edit type'))
    file_name = models.CharField(max_length = 120, blank = True, null=True, verbose_name = _('file name'))
    row_no = models.IntegerField(verbose_name = _('row no'), blank=True, null=True)
    row_content = models.TextField(blank = True, null=True, verbose_name = _('row content'))
    message = models.CharField(max_length = 2048, blank = True, null=True, verbose_name = _('message'))
    creator = models.CharField(max_length = 120, blank = True, null=True, verbose_name = _('creator'))
    create_time = models.DateTimeField(blank = True, null=True, verbose_name = _('create time'))
    lot_number = models.CharField(max_length = 64, blank=True, null=True, verbose_name=_('lot number'))

    class Meta:
        db_table = 'cmm_csv_log'
        verbose_name = _('csv log')
        verbose_name_plural = _('csv logs')
        default_permissions = []

        ordering = ['-create_time']
    
    def convert_content2json(self):
        """json型に変換する"""
        self.row_content = json.dumps(self.row_content)
        return self
    
    def convert_content2dict(self):
        """dict型に変換する"""
        self.row_content = json.loads(self.row_content)
        return self
    
    def convert_content2values(self):
        """dict型に変換する"""
        self.row_content = list(json.loads(self.row_content).values())
        return self
