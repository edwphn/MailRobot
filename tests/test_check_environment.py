import unittest
import os
import shutil
from unittest.mock import patch
from maintenance import _check_dirs, _check_templates

class TestCheckEnvironment(unittest.TestCase):

    def setUp(self):
        self.test_directory = 'test_directory'
        self.test_template_file = 'test_template.txt'
        self.test_missing_directory = 'test_missing_directory'
        self.test_missing_template_file = 'test_missing_template.txt'

    def tearDown(self):
        # Удаление тестовой директории и файлов после каждого теста
        if os.path.exists(self.test_directory):
            shutil.rmtree(self.test_directory)
        if os.path.exists(self.test_template_file):
            os.remove(self.test_template_file)

    def test_check_existing_dirs_and_files(self):
        os.makedirs(self.test_directory)
        with open(self.test_template_file, 'w') as f:
            f.write("Test content")

        with patch('maintenance.config_vars', {'directories': {'test_dir': self.test_directory},
                                               'files': {'test_file': self.test_template_file}}):
            self.assertTrue(_check_dirs(['test_dir']))
            self.assertTrue(_check_templates(['test_file']))

    def test_create_missing_dirs(self):
        with patch('maintenance.config_vars', {'directories': {'test_missing_dir': self.test_missing_directory}}):
            self.assertTrue(_check_dirs(['test_missing_dir']))
            self.assertTrue(os.path.exists(self.test_missing_directory))

    def test_missing_template_files(self):
        with patch('maintenance.config_vars', {'files': {'test_missing_file': self.test_missing_template_file}}):
            self.assertFalse(_check_templates(['test_missing_file']))

    @unittest.skipUnless(os.name == 'posix', "Test requires POSIX permissions.")
    def test_permission_error(self):
        os.makedirs(self.test_directory)
        os.chmod(self.test_directory, 0o500)  # Устанавливаем права доступа только на чтение

        with patch('maintenance.config_vars', {'directories': {'test_dir': self.test_directory}}):
            self.assertFalse(_check_dirs(['test_dir']))

        # Возвращаем права доступа к директории после теста
        os.chmod(self.test_directory, 0o700)
