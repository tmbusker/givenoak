from datetime import date
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from cmm.utils.date import format_date

def validate_period(valid_from: date, valid_through: date):
    """ 開始日 <= 終了日のチェック """
    if valid_from and valid_through and valid_from > valid_through:
        raise ValidationError(
            _('The period start date %(valid_from)s must be older then end date %(valid_through)s.'),
            code='invalid_period',
            params = {"valid_from": format_date(valid_from), "valid_through": format_date(valid_through)}
        )
