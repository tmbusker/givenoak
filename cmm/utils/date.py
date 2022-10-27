import fractions
from functools import total_ordering
from datetime import date, timedelta
from django.utils.formats import date_format


def format_date(date_obj):
    """format date to localized SHORT_DATE_FORMAT"""
    return date_format(date_obj, format='SHORT_DATE_FORMAT', use_l10n=True)

# @total_ordering
class Period:
    """Period class, valid_from and valid_through are inclusive."""
    def __init__(self, valid_from: date, valid_through: date):
        self.valid_from = valid_from
        self.valid_through = valid_through
        if self.valid_from > self.valid_through:
            self.valid_from, self.valid_through = self.valid_through, self.valid_from
        
    def __str__(self) -> str:
        return f'[{date_format(self.valid_from)}: {date_format(self.valid_through)}]'

    def __eq__(self, obj) -> bool:
        return isinstance(obj, self.__class__) and \
            self.valid_from == obj.valid_from and self.valid_through == obj.valid_through

    def __ne__(self, obj) -> bool:
        return not isinstance(obj, self.__class__) and \
            self.valid_from != obj.valid_from or self.valid_through != obj.valid_through

    def __lt__(self, obj) -> bool:
        return self.valid_from < obj.valid_from or \
            self.valid_from == obj.valid_from and self.valid_through < obj.valid_through

    def __le__(self, obj) -> bool:
        return self.valid_from <= obj.valid_from or \
            self.valid_from == obj.valid_from and self.valid_through <= obj.valid_through

    def __gt__(self, obj) -> bool:
        return self.valid_from > obj.valid_from or \
            self.valid_from == obj.valid_from and self.valid_through > obj.valid_through

    def __ge__(self, obj) -> bool:
        return self.valid_from >= obj.valid_from or \
            self.valid_from == obj.valid_from and self.valid_through >= obj.valid_through
    
    def __hash__(self) -> int:
        return hash((self.valid_from, self.valid_through))
    
    def __repr__(self):
        return f'[{self.valid_from}:{self.valid_through}]'
    
    def is_contains(self, obj):
        """ほかの期間を含んでいるのか"""
        if obj is None or not isinstance(obj, self.__class__):
            return False
        return self.valid_from <= obj.valid_from and self.valid_through >= obj.valid_through
    
    def is_contained(self, obj):
        """ほかの期間に含まれているか"""
        if obj is None or not isinstance(obj, self.__class__):
            return False
        return self.valid_from >= obj.valid_from and self.valid_through <= obj.valid_through

    def is_joined(self, obj):
        """ほかの期間と重なっているか"""
        if obj is None or not isinstance(obj, self.__class__):
            return False
        return self.valid_from <= obj.valid_through and self.valid_through >= obj.valid_from
    
    def to_dict(self):
        """Convert period to dict"""
        return({'valid_from': self.valid_from, 'valid_through': self.valid_through})
    
    def get_ends(self):
        """両端をsort可能なdictに変換する"""
        return [{'date': self.valid_from, 'type': 'start', 'sort_key': self.valid_from.strftime('%Y%m%d') + '0'},
                {'date': self.valid_through, 'type': 'end', 'sort_key': self.valid_through.strftime('%Y%m%d') + '1'}]
        
def flat_overlap(periods: list[Period]) -> list[Period]:
    """Break down overlapped periods to separated ones."""
    converted = []
    for period in periods:
        converted.extend(period.get_ends())
    converted.sort(key=lambda x: x.get('sort_key'))
    
    fragments = []
    start_cnt = 0
    valid_from = None
    for item in converted:
        current_type = item.get('type')
        current_date = item.get('date')
        if current_type == 'start':
            start_cnt += 1
            if valid_from is None:
                valid_from = current_date
            elif current_date > valid_from:
                fragments.append(Period(valid_from, current_date - timedelta(days=1)))
                valid_from = current_date
        else:
            start_cnt -= 1
            if current_date >= valid_from:
                fragments.append(Period(valid_from, current_date))
                if start_cnt > 0:
                    valid_from = current_date + timedelta(days=1)
                else:
                    valid_from = None
    return fragments
