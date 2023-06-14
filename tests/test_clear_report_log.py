import unittest
import os
from unittest.mock import patch
from maintenance import clear_report_log


class TestClearReportLog(unittest.TestCase):

    def setUp(self):
        self.test_report_log = 'test_report.log'

    def tearDown(self):
        # Удаление тестового файла report.log после каждого теста
        if os.path.exists(self.test_report_log):
            os.remove(self.test_report_log)

    @patch('maintenance.report_log', new='test_report.log')
    def test_create_report_log_if_not_exists(self):
        # Убеждаемся, что тестовый файл report.log не существует
        self.assertFalse(os.path.exists(self.test_report_log))

        # Вызываем функцию clear_report_log
        clear_report_log()

        # Проверяем, что тестовый файл report.log был создан
        self.assertTrue(os.path.exists(self.test_report_log))

    @patch('maintenance.report_log', new='test_report.log')
    def test_clear_existing_report_log(self):
        # Создаем тестовый файл report.log с некоторым содержимым
        with open(self.test_report_log, 'w') as f:
            f.write("Test content")

        # Вызываем функцию clear_report_log
        clear_report_log()

        # Проверяем, что содержимое файла report.log было очищено
        with open(self.test_report_log, 'r') as f:
            content = f.read()
        self.assertEqual(content, "")
