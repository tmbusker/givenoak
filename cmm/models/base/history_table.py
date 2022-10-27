import logging
from typing import Any
from datetime import date, timedelta
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.db.models import Q, Min, Max

from cmm.models.base import SimpleTable
from cmm.utils.validation import validate_period
from cmm.utils.date import format_date


_logger = logging.getLogger(__name__)

DEFAULT_valid_from = date(2000, 1, 1)
DEFAULT_valid_through = date(2222, 12, 31)

class HistoryTable(SimpleTable, models.Model):
    """
    履歴テーブル
    - 履歴データのデフォルト有効期間は本テーブル指定のデフォルト開始日とデフォルト終了日とする
    - 履歴データの有効終了日は自動設定される。
        - 後続レコードがある場合は、後続レコードの前日を設定する
        - 後続レコードがない場合は、デフォルト終了日を設定する
    - 履歴データへの変更分は必ず基準日の翌日以後へ反映される（更新時画面から入力可能な日付は基準日より新しいもののみ）
    - 有効終了日が基準日以前となるレコードは編集不可、未来日付となるレコードのみ編集可能
    - 基準日までの履歴データはほかの処理から参照されトランザクション・データが作成された可能性があるので、変更不可とする
    - 基準日時点より有効開始日が未来となるレコードは複数件作成可能
    - 新規作成時のみ有効開始日は任意の日付を指定することができる
    """
    valid_from = models.DateField(blank=False, default=date.today, verbose_name=_("valid from"))
    valid_through = models.DateField(blank=True, null=True, verbose_name=_("valid through"))

    class Meta:
        abstract = True

    def get_reference_date(self) -> date:
        """基準日"""
        return date.today()

    def get_default_valid_from(self) -> date:
        """デフォルトの有効開始日"""
        return self.get_reference_date() + timedelta(days=1)

    def get_default_valid_through(self) -> date:
        """デフォルトの有効終了日"""
        return DEFAULT_valid_through

    def get_broadly_unique_key(self) -> tuple[str]:
        """
        ユニーク・キーから有効開始日を外した広義的（業務的）ユニーク・キー
        """
        return tuple(f for f in self.get_unique_key() if f != "valid_from")

    def retrieve_by_broadly_unique_key(self) -> models.QuerySet:
        """Instance作成時にUnique keyとなる項目が不十分の場合は想定したより多い件数が取得されることがある"""
        return self.__class__.objects.filter(**{f: getattr(self, f) for f in self.get_broadly_unique_key()
                                                                        if getattr(self, f, None) is not None})

    def get_next_record(self):
        """有効開始日が直後となるレコード"""
        return self.retrieve_by_broadly_unique_key().filter(valid_from__gt=self.valid_from)\
                        .order_by("valid_from").first()

    def get_previous_record(self):
        """有効開始日が直前となるレコード"""
        return self.retrieve_by_broadly_unique_key().filter(valid_from__lt=self.valid_from)\
                        .order_by('-valid_from').first()

    def has_same_contents(self, obj) -> bool:
        """同一レコードであるかどうかの判断ロジックを実装、比較対象となるカラムをカスタマイズできる"""
        raise Exception('Must be implemented.')

    def save(self, *args, **kwargs) -> None:
        # pylint: disable = attribute-defined-outside-init

        if not self.valid_through:
            self.valid_through = self.get_default_valid_through()

        same_record = self.retrieve_by_unique_key()

        # 変更がない場合は保存処理をスキップする
        if same_record is not None and self.has_same_contents(same_record):
            _logger.debug("Skip to save the contents because no change was detected on %s.", self)
            return

        prev_record = self.get_previous_record()
        next_record = self.get_next_record()

        if not same_record:
            # 新規作成処理
            if next_record:
                self.valid_through = next_record.valid_from + timedelta(days = -1)

            if prev_record is None:
                super().save(*args, **kwargs)
            else:
                prev_record.valid_through = self.valid_from + timedelta(days = -1)
                super(HistoryTable, prev_record).save(*args, **kwargs)
                # pylint: disable = invalid-name
                self.id = None
                self._state.adding = True
                super().save(*args, **kwargs)
        else:
            # 更新処理
            self.creator = same_record.creator
            self.create_time = same_record.create_time

            if same_record.valid_from > self.get_reference_date():         # 未来発効レコード
                if self.id is None:             # CSV import時に発生することがある
                    self.id = same_record.id
                super().save(*args, **kwargs)
            else:
                same_record.valid_through = self.get_reference_date()
                super(HistoryTable, same_record).save(*args, **kwargs)
                self.valid_from = self.get_reference_date() + timedelta(days = 1)
                self.id = None
                self._state.adding = True
                super().save(*args, **kwargs)

    def delete(self, *args, **kwargs) -> None:
        same_record = self.retrieve_by_unique_key()

        if same_record:
            prev_record = self.get_previous_record()
            next_record = self.get_next_record()
            if same_record.valid_from > self.get_reference_date():
                if prev_record:
                    prev_record.valid_through = self.valid_through
                    super(HistoryTable, prev_record).save()

                super().delete(*args, **kwargs)
            elif same_record.valid_through > self.get_reference_date():
                same_record.valid_through = self.get_reference_date()
                super(HistoryTable, same_record).save(*args, **kwargs)
                if next_record:
                    next_record.valid_from = self.get_reference_date() + timedelta(days = 1)
                    super(HistoryTable, next_record).save(*args, **kwargs)
            else:
                raise ValidationError(
                    _('You cannot edit a record with expired date %(valid_through)s.'),
                    code='validate_valid_through',
                    params = {"valid_through": format_date(same_record.valid_through)}
                )
        else:
            raise self.DoesNotExist

    def clean(self) -> None:
        # 変更がない場合は処理をスキップする
        same_record = self.retrieve_by_unique_key()
        if same_record is not None and self.has_same_contents(same_record):
            return

        # 開始日 <= 終了日のチェック
        validate_period(self.valid_from, self.valid_through)

        # 終了日 <= 基準日のチェック（失効レコードは変更不可）
        self.validate_valid_through()

        # 自身の開始日より新しいレコードが存在する場合、開始日 <= 基準日のレコードを新規作成することはできない
        self.validate_valid_from()

        super().clean()
   
    def get_at(self, ref_date: date) -> Any:
        """指定日付時点に有効なレコードを取得する"""
        obj = self.retrieve_by_broadly_unique_key().filter(valid_from__lte=ref_date, valid_through__gte=ref_date).first()
        return obj

    def validate_valid_from(self):
        """自身の開始日より新しいレコードが存在する場合、開始日 <= 基準日のレコードを新規作成することはできない"""
        query_set = self.retrieve_by_broadly_unique_key().filter(~Q(valid_from = self.valid_from))
        result = query_set.aggregate(Min('valid_from'), Max('valid_from'), Min('valid_through'), Max('valid_through'))
        max_valid_through = result.get('valid_through__max')
        if self.valid_from <= self.get_reference_date() and max_valid_through is not None \
            and self.valid_from <= max_valid_through:
            raise ValidationError(
                # memo: gettext or gettext_lazy is not localized.
                _('You cannot specify a staled date %(valid_from)s as a start date.'),
                code='staled_valid_from',
                params = {"valid_from": format_date(self.valid_from)}
            )

    def validate_valid_through(self):
        """ 終了日 <= 基準日のチェック（失効レコードは変更不可） """
        ref_date = self.get_reference_date()
        if self.valid_through and self.valid_through <= ref_date:
            raise ValidationError(
                _('You cannot edit a record that expired at %(valid_through)s.'),
                code='validate_valid_through',
                params = {"valid_through": format_date(self.valid_through)}
            )
