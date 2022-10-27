from django.test import TestCase
from django.db import models

from cmm.tests.history_table import HistoryTableTestMixin
from cmm.models.city import City

from ..models import Organization, Employee
from ..exception import RecursiveParenthoodError
from .common_base_table import CommonBaseTableTestMixin


class ShikuchosonTableTestCase(HistoryTableTestMixin, TestCase):
    """test class"""
    def setUp(self) -> None:
        self.test_class = City
        self.test_dict = {"code": "010006", "pref_name": "北海道", "pref_name_kana": "ホッカイドウ"}
        super().setUp()

    def change_value4test(self, obj: models.Model):
        obj.name += "test"

class OrganizationTestCase(CommonBaseTableTestMixin, TestCase):
    """test class"""
    def change_value4test(self, obj: models.Model):
        obj.name += "test"

    def setUp(self) -> None:
        self.test_class = Organization
        self.test_dict = {"name": "name", "code": "code"}
        self.parent_test_dict = {"name": "parent_org_name", "code": "parent_org_code"}

        super().setUp()

    def test_default_value(self):
        """デフォルト値確認"""
        self.test_class(**self.test_dict).save()
        test_record = self.test_class.objects.get(**self.test_dict)
        self.assertEqual(test_record.name, self.test_dict["name"])
        self.assertEqual(test_record.code, self.test_dict["code"])

    def test_parent_org(self):
        """parent organization"""
        self.test_class(**self.parent_test_dict).save()
        parent_org = self.test_class.objects.get(**self.parent_test_dict)
        self.test_dict["parent_org"] = parent_org
        self.test_class(**self.test_dict).save()

        child_test_org = self.test_class.objects.get(**self.test_dict)
        self.assertEqual(child_test_org.parent_org.code, self.parent_test_dict["code"])

    def test_self_as_parent_org(self):
        """can not specify self as parent"""
        self.test_class(**self.test_dict).save()
        parent_org = self.test_class.objects.get(**self.test_dict)
        parent_org.parent_org = parent_org
        self.assertRaises(RecursiveParenthoodError, self.test_class.save, parent_org)

class EmployeeTestCase(CommonBaseTableTestMixin, TestCase):
    """ test class"""
    def change_value4test(self, obj: models.Model):
        obj.name += "test"

    def setUp(self) -> None:
        self.test_class = Employee
        self.test_dict = {"name": "name", "code": "name", "email": 'tester@test.org'}

        super().setUp()

    def test_default_value(self):
        """default values"""
        self.test_class(**self.test_dict).save()
        test_record = self.test_class.objects.get(**self.test_dict)
        self.assertEqual(test_record.name, self.test_dict["name"])
        self.assertEqual(test_record.code, self.test_dict["code"])
        self.assertEqual(test_record.email, self.test_dict["email"])
