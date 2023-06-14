import os
import tempfile
import unittest
from maintenance import get_filenames

class TestGetFilenames(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def create_temp_files(self, file_names):
        for file_name in file_names:
            with open(os.path.join(self.temp_dir.name, file_name), 'w') as temp_file:
                temp_file.write("Dummy content")

    def test_get_filenames_with_pdf_files(self):
        # Создаем тестовые файлы с расширением .pdf и другие файлы
        files = ["file1.pdf", "file2.pdf", "file3.txt", "file4.docx"]
        self.create_temp_files(files)

        result = get_filenames(self.temp_dir.name)

        # Проверяем, что функция возвращает только файлы с расширением .pdf
        self.assertEqual(len(result), 2)
        self.assertIn("file1", result)
        self.assertIn("file2", result)

    def test_get_filenames_with_no_pdf_files(self):
        # Создаем тестовые файлы без расширения .pdf
        files = ["file1.txt", "file2.docx", "file3.jpeg", "file4.png"]
        self.create_temp_files(files)

        result = get_filenames(self.temp_dir.name)

        # Проверяем, что функция возвращает пустой список
        self.assertEqual(len(result), 0)
        self.assertEqual(result, [])

if __name__ == "__main__":
    unittest.main()
