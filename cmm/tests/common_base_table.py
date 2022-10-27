from .versioned_table import VersionedTableTestMixin


class CommonBaseTableTestMixin(VersionedTableTestMixin):
    """
    Base class to test tables which inherit CommonBaseTable
    """

    def change_value4test(self, obj):
        """ we should override this method to test HistoryTable and VersionedTable"""
