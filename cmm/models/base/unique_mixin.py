import logging
from django.db import models


_logger = logging.getLogger(__name__)

class UniqueConstraintMixin():
    """
    This mixin should be mixed with models.Model, 
    which defined a models.UniqueConstraint named as (meta.db_table)_unique.
    """
    def get_unique_key(self) -> tuple[str]:
        """
        return columns of the unique constraint.
        """
        meta = self._meta
        if meta.total_unique_constraints:

            unique_constraint_name = f'{meta.db_table}_unique'
            unique_constraints = [c for c in meta.total_unique_constraints if c.name == unique_constraint_name]
            if unique_constraints:
                unique_constraint_fields = unique_constraints[0].fields
            else:
                unique_constraint_fields = meta.total_unique_constraints[0].fields

            _logger.debug("Unique constraint of %(table)s is %(fields)s.", \
                            {'table': meta.db_table, 'fields': unique_constraint_fields})
            return unique_constraint_fields
        return ()

    def retrieve_by_unique_key(self) -> models.Model:
        """Uniqueキーで検索した結果"""
        return self.__class__.objects.filter(**{k: getattr(self, k) for k in self.get_unique_key()}).first()
