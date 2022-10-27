from django.core.exceptions import ValidationError


class VersionedTableTestMixin():
    """Base class to test tables which inherit VersionedTable"""
    # pylint: disable = missing-function-docstring, invalid-name
    def setUp(self) -> None:
        ...

    def test_default_version(self):
        self.test_class(**self.test_dict).save()
        test_record = self.test_class.objects.get(**self.test_dict)
        self.assertEqual(test_record.version, 1)

    def test_version_up(self):
        self.test_class(**self.test_dict).save()
        test_record = self.test_class.objects.get(**self.test_dict)
        self.change_value4test(test_record)
        test_record.save()
        self.assertEqual(test_record.version, 2)

    def test_race_condition(self):
        self.test_class(**self.test_dict).save()
        test_record_a = self.test_class.objects.get(**self.test_dict)
        test_record_b = self.test_class.objects.get(**self.test_dict)

        self.change_value4test(test_record_a)
        self.change_value4test(test_record_b)
        test_record_a.save()

        self.change_value4test(test_record_b)
        self.assertRaises(ValidationError, test_record_b.save)
