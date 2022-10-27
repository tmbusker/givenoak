from datetime import date, timedelta
from django.core.exceptions import ValidationError
from cmm.models.base import DEFAULT_valid_from


class HistoryTableTestMixin():
    """
    Base class to test tables which inherit HistoryTable
    """
    def setUp(self) -> None:
        """test set up, called by each test."""
        # pylint: disable = invalid-name
        self.reference_date = date.today()
        self.past_date = self.reference_date + timedelta(days=-1)
        self.older_past_date = self.reference_date + timedelta(days=-10)
        self.future_date = self.reference_date + timedelta(days=1)
        self.newer_future_date = self.reference_date + timedelta(days=10)

        self.test_dict["valid_from"] = DEFAULT_valid_from

    def test_invalid_period(self):
        """
        create date:  valid_from > valid_through
        result:          ValidationError
        """

        # test condition
        self.test_dict['valid_through'] = self.test_dict['valid_from'] + timedelta(days=-1)
        with self.assertRaises(ValidationError):
            self.test_class(**self.test_dict).full_clean()

    def test_create_by_reference_date(self):
        """
        original record: none
        create date:     none                    (reference_date)
        result:                                 |+--------------------------------------|
        """

        self.test_dict["valid_from"] = self.reference_date
        self.test_class(**self.test_dict).save()
        test_record = self.test_class.objects.get(**self.test_dict)
        self.assertEqual(test_record.valid_from, self.reference_date)
        self.assertEqual(test_record.valid_through, test_record.get_default_valid_through())

    def test_create_by_past_date(self):
        """
        original record: none
        update date:     past          (reference_date)
        result:         |past---------+-------------------------------------------------|
        """

        self.test_dict["valid_from"] = self.past_date
        self.test_class(**self.test_dict).save()
        test_record = self.test_class.objects.get(**self.test_dict)
        self.assertEqual(test_record.valid_from, self.past_date)
        self.assertEqual(test_record.valid_through, test_record.get_default_valid_through())

    def test_create_by_future_date(self):
        """
        original record: none
        update date:              (reference_date)         future
        result:                                           |future-----------------------|
        """

        self.test_dict["valid_from"] = self.future_date
        self.test_class(**self.test_dict).save()
        test_record = self.test_class.objects.get(**self.test_dict)
        self.assertEqual(test_record.valid_from, self.future_date)
        self.assertEqual(test_record.valid_through, test_record.get_default_valid_through())

    def test_create_by_reference_date_has_next_record(self):
        """
        original record:                                  |future-----------------------|
        create date:                             reference_date
        result:                                 |+--------|future-----------------------|
        """

        # test condition
        self.test_dict["valid_from"] = self.future_date
        self.test_class(**self.test_dict).save()

        # test
        self.test_dict["valid_from"] = self.reference_date
        self.test_class(**self.test_dict).save()
        test_record = self.test_class.objects.get(**self.test_dict)
        self.assertEqual(test_record.valid_from, self.reference_date)
        self.assertEqual(test_record.valid_through, test_record.get_next_record().valid_from + timedelta(days=-1))

    def test_create_by_past_date_has_next_record(self):
        """
        original record:                                  |future-----------------------|
        update date:     past         (reference_date)
        result:         |past---------+-------------------|-----------------------------|
        """

        # test condition
        self.test_dict["valid_from"] = self.future_date
        self.test_class(**self.test_dict).save()

        # test
        self.test_dict["valid_from"] = self.past_date
        self.test_class(**self.test_dict).save()
        test_record = self.test_class.objects.get(**self.test_dict)
        self.assertEqual(test_record.valid_from, self.past_date)
        self.assertEqual(test_record.valid_through, test_record.get_next_record().valid_from + timedelta(days=-1))

    def test_create_future_date_has_next_record(self):
        """
        original record:                                    |newer future---------------|
        update date:              (reference_date)  future
        result:                                    |--------|newer future---------------|
        """

        # test condition
        self.test_dict["valid_from"] = self.newer_future_date
        self.test_class(**self.test_dict).save()

        # test
        self.test_dict["valid_from"] = self.future_date
        self.test_class(**self.test_dict).save()
        test_record = self.test_class.objects.get(**self.test_dict)
        self.assertEqual(test_record.valid_from, self.future_date)
        self.assertEqual(test_record.valid_through, test_record.get_next_record().valid_from + timedelta(days=-1))

    def test_create_by_reference_date_has_previous_record(self):
        """
        original record:|-----------------------+---------------------------------------|
        create date:                             reference_date
        result:         ValidationError
        """

        # test condition
        self.test_dict["valid_from"] = DEFAULT_valid_from
        self.test_class(**self.test_dict).save()

        # test
        self.test_dict["valid_from"] = self.reference_date
        with self.assertRaises(ValidationError):
            self.test_class(**self.test_dict).full_clean()
        # self.assertRaises(ValidationError, self.test_class.objects.create, **self.test_dict)

    def test_create_by_past_date_has_previous_record(self):
        """
        original record:|------------------------+--------------------------------------|
        create date:              past           (reference_date)
        result:         ValidationError
        """
        # pylint: disable = protected-access

        # test condition
        self.test_dict["valid_from"] = DEFAULT_valid_from
        self.test_class(**self.test_dict).save()

        # test
        self.test_dict["valid_from"] = self.past_date
        with self.assertRaises(ValidationError):
            self.test_class(**self.test_dict).full_clean()
            self.test_class(**self.test_dict).save()

    def test_create_by_future_date_has_previous_record(self):
        """
        original record:|------------------------+--------------------------------------|
        create date:                             (reference_date)     future
        result:         |------------------------+-------------------|------------------|
        """

        # test condition
        self.test_dict["valid_from"] = DEFAULT_valid_from
        self.test_class(**self.test_dict).save()

        # test
        self.test_dict["valid_from"] = self.future_date
        self.test_class(**self.test_dict).save()
        test_record = self.test_class.objects.get(**self.test_dict)
        self.assertEqual(test_record.valid_from, self.future_date)
        self.assertEqual(test_record.get_previous_record().valid_through, test_record.valid_from + timedelta(days=-1))

    def test_create_by_future_date_has_invalid_previous_record(self):
        """
        original record:|---------+|
        create date:     past     (reference_date)      future
        result:         |---------+--------------------|--------------------------------|
        """

        # test condition
        self.test_class(**self.test_dict).save()
        self.test_class.objects.filter(**self.test_dict).update(valid_through = self.reference_date)

        # test
        self.test_dict["valid_from"] = self.future_date
        self.test_class(**self.test_dict).save()
        test_record = self.test_class.objects.get(**self.test_dict)
        self.assertEqual(test_record.valid_from, self.future_date)
        self.assertEqual(test_record.get_previous_record().valid_through, test_record.valid_from + timedelta(days=-1))

    def test_create_by_future_date_has_previous_and_next_record(self):
        """
        original record:|-------------+-------------------------------|-----------------|
        create date:                  (reference_date)     future      newer_future
        result:         |-------------+-------------------|-----------|-----------------|
        """

        # test condition
        self.test_dict["valid_from"] = DEFAULT_valid_from
        self.test_class(**self.test_dict).save()
        self.test_dict["valid_from"] = self.newer_future_date
        self.test_class(**self.test_dict).save()

        # test
        self.test_dict["valid_from"] = self.future_date
        self.test_class(**self.test_dict).save()
        test_record = self.test_class.objects.get(**self.test_dict)
        self.assertEqual(test_record.valid_from, self.future_date)
        self.assertEqual(test_record.valid_from, test_record.get_previous_record().valid_through + timedelta(days=1))
        self.assertEqual(test_record.valid_through, test_record.get_next_record().valid_from + timedelta(days=-1))

    def test_update_record_valid_from_future(self):
        """
        original record:                                  |future-----------------------|
        update date:              (reference_date)         future
        result:                                           |future-----------------------|
        """

        # test condition
        self.test_dict["valid_from"] = self.future_date
        self.test_class(**self.test_dict).save()

        # test
        test_record = self.test_class.objects.get(**self.test_dict)
        test_record.save()
        self.assertEqual(test_record.valid_from, self.future_date)

    def test_update_record_valid_through_reference_date(self):
        """
        original record:|---------+|
        update date:     past     (reference_date)
        result:          ValidationError
        """

        # test condition
        self.test_class(**self.test_dict).save()
        self.test_class.objects.filter(**self.test_dict).update(valid_through = self.reference_date)

        # test
        test_record = self.test_class.objects.get(**self.test_dict)
        self.change_value4test(test_record)
        with self.assertRaises(ValidationError):
            self.test_class(**self.test_dict).full_clean()
            self.test_class(**self.test_dict).save()

    def test_update_record_currently_valid(self):
        """
        original record:|-------------+-------------------------------------------------|
        create date:                  (reference_date)
        result:         |-------------+|-------------------------------------------------|
        """

        # test condition
        self.test_dict["valid_from"] = DEFAULT_valid_from
        self.test_class(**self.test_dict).save()

        # test
        test_record = self.test_class.objects.get(**self.test_dict)
        self.change_value4test(test_record)
        test_record.save()
        self.assertEqual(test_record.valid_from, self.reference_date + timedelta(days=1))
        self.assertEqual(test_record.valid_through, test_record.get_default_valid_through())
        self.assertEqual(test_record.get_previous_record().valid_from, DEFAULT_valid_from)
        self.assertEqual(test_record.get_previous_record().valid_through, test_record.valid_from + timedelta(days=-1))

    def test_delete_record_valid_from_future(self):
        """
        original record:                                  |future-----------------------|
        delete date:             (reference_date)         future
        result:         no record
        """

        # test condition
        self.test_dict["valid_from"] = self.future_date
        self.test_class(**self.test_dict).save()

        # test
        test_record = self.test_class.objects.get(**self.test_dict)
        test_record.delete()
        self.assertRaises(self.test_class.DoesNotExist, self.test_class.objects.get, **self.test_dict)

    def test_delete_record_valid_from_future_has_previous_record(self):
        """
        original record: |--------------------------------|future-----------------------|
        delete date:                                       future
        result:          |--------------------------------------------------------------|
        """

        # test condition
        self.test_class(**self.test_dict).save()
        self.test_dict["valid_from"] = self.future_date
        self.test_class(**self.test_dict).save()
        test_record = self.test_class.objects.get(**self.test_dict)
        valid_through = test_record.valid_through
        self.assertEqual(test_record.get_previous_record().valid_through, test_record.valid_from + timedelta(days=-1))

        # test
        test_record.delete()
        self.assertRaises(self.test_class.DoesNotExist, self.test_class.objects.get, **self.test_dict)
        self.test_dict["valid_from"] = DEFAULT_valid_from
        prev_record = self.test_class.objects.get(**self.test_dict)
        self.assertEqual(prev_record.valid_through, valid_through)

    def test_delete_currently_valid_record_has_no_next_record(self):
        """
        original record: |----------------+---------------------------------------------|
        delete date:                      (reference_date)
        result:          |----------------+|
        """

        # test condition
        self.test_class(**self.test_dict).save()

        # test
        test_record = self.test_class.objects.get(**self.test_dict)
        test_record.delete()
        self.test_dict["valid_from"] = self.future_date
        self.assertRaises(self.test_class.DoesNotExist, self.test_class.objects.get, **self.test_dict)
        self.test_dict["valid_from"] = DEFAULT_valid_from
        current = self.test_class.objects.get(**self.test_dict)
        self.assertEqual(current.valid_through, self.reference_date)

    def test_delete_currently_valid_record_has_next_record(self):
        """
        original record: |----------------+--------------------|------------------------|
        delete date:                      (reference_date)      future
        result:          |----------------+|--------------------------------------------|
        """

        # test condition
        self.test_class(**self.test_dict).save()
        self.test_dict["valid_from"] = self.newer_future_date
        self.test_class(**self.test_dict).save()

        # test
        self.test_dict["valid_from"] = DEFAULT_valid_from
        test_record = self.test_class.objects.get(**self.test_dict)
        test_record.delete()
        test_record.refresh_from_db()
        self.assertEqual(test_record.valid_through, test_record.get_next_record().valid_from + timedelta(days=-1))

    def test_delete_record_valid_through_reference_date(self):
        """
        original record:|---------+|
        delete date:              reference_date
        result:          ValidationError
        """

        # test condition
        self.test_class(**self.test_dict).save()
        self.test_class.objects.filter(**self.test_dict).update(valid_through = self.reference_date)

        # test
        test_record = self.test_class.objects.get(**self.test_dict)
        self.assertRaises(ValidationError, test_record.delete)

    def test_delete_nonexisting_record(self):
        """
        original record:|-------------+-------------------------------------------------|
        delete date:                  reference_date
        result:          DoesNotExist
        """

        # test condition
        self.test_class(**self.test_dict).save()

        # test
        test_record = self.test_class.objects.get(**self.test_dict)
        test_record.valid_from = self.reference_date
        self.assertRaises(self.test_class.DoesNotExist, test_record.delete)
