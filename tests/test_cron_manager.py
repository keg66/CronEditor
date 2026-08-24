import unittest

from src.cron_manager import CronManager


class CronValidationTests(unittest.TestCase):
    def setUp(self):
        self.manager = CronManager()

    def test_standard_builder_expressions_are_accepted(self):
        self.assertEqual({}, self.manager.validate_time_fields('*/5', '9-17/2', '1,15', '1-12', '1-5'))

    def test_named_weekday_range_is_accepted(self):
        self.assertEqual({}, self.manager.validate_time_fields('30', '9', '*', '*', 'mon-fri'))

    def test_invalid_values_are_returned_by_field(self):
        errors = self.manager.validate_time_fields('60', '24', '0', '13', 'mon-funday')
        self.assertEqual(set(errors), {'minute', 'hour', 'day', 'month', 'weekday'})

    def test_invalid_interval_and_reverse_range_are_rejected(self):
        errors = self.manager.validate_time_fields('*/0', '17-9', '*', '*', '*')
        self.assertIn('minute', errors)
        self.assertIn('hour', errors)

    def test_unsupported_interval_and_list_combination_is_rejected(self):
        errors = self.manager.validate_time_fields('*/5,30', '*', '*', '*', '*')
        self.assertIn('minute', errors)

    def test_prose_comment_is_not_a_disabled_cron_job(self):
        self.assertFalse(self.manager._looks_like_disabled_cron(
            '# Edit this file to introduce tasks to be run by cron.'
        ))

    def test_disabled_cron_job_is_still_detected(self):
        self.assertTrue(self.manager._looks_like_disabled_cron(
            '# 0 9 * * mon-fri /usr/local/bin/report'
        ))


if __name__ == '__main__':
    unittest.main()
