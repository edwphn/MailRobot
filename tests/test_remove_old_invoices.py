import os
import unittest
from datetime import datetime, timedelta
from tempfile import TemporaryDirectory
from maintenance import remove_old_invoices

class TestRemoveOldInvoices(unittest.TestCase):

    def setUp(self):
        # Создание временной директории для тестов
        self.temp_dir = TemporaryDirectory()
        self.test_dir = self.temp_dir.name

        # Создание файлов PDF с разной датой создания
        self.files = {
            'old.pdf': (datetime.now() - timedelta(days=10)),
            'new.pdf': (datetime.now() - timedelta(days=5))
        }

        for file, mtime in self.files.items():
            path = os.path.join(self.test_dir, file)
            with open(path, 'w') as f:
                f.write('test content')
            os.utime(path, (mtime.timestamp(), mtime.timestamp()))

    def test_remove_old_invoices(self):
        # Запуск функции remove_old_invoices с порогом 7 дней
        remove_old_invoices(self.test_dir, 7)

        # Проверка, что старый файл удален, а новый файл остался
        remaining_files = os.listdir(self.test_dir)
        self.assertNotIn('old.pdf', remaining_files)
        self.assertIn('new.pdf', remaining_files)

    def test_permission_error(self):
        # Изменение прав доступа к файлу, если это возможно
        try:
            os.chmod(os.path.join(self.test_dir, 'old.pdf'), 0o444)
            remove_old_invoices(self.test_dir, 7)
            remaining_files = os.listdir(self.test_dir)

            # Если файл old.pdf остался после выполнения функции, это означает, что ошибка прав доступа была обработана
            self.assertIn('old.pdf', remaining_files)
        except PermissionError:
            self.skipTest("Unable to set file permission")

    def tearDown(self):
        # Удаление временной директории после завершения тестов
        self.temp_dir.cleanup()

if __name__ == '__main__':
    unittest.main()
