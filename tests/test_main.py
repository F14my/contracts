import io
import json
import os
import unittest
from contextlib import redirect_stdout

from src.main import create_dummy_json, delete_dummy_json, main


class TestMain(unittest.TestCase):
    def test_create_dummy_json(self):
        """Проверяет, что create_dummy_json создает test.json с ожидаемой структурой."""
        create_dummy_json()
        self.assertTrue(os.path.exists("test.json"))
        with open("test.json", "r", encoding="utf-8") as file:
            data = json.load(file)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["id"], "file_1")

    def test_delete_dummy_json(self):
        """Проверяет, что delete_dummy_json удаляет ранее созданный test.json."""
        with open("test.json", "w", encoding="utf-8") as file:
            file.write("[]")
        self.assertTrue(os.path.exists("test.json"))
        delete_dummy_json()
        self.assertFalse(os.path.exists("test.json"))

    def test_main_prints_tasks_and_deletes_file(self):
        """Проверяет полный сценарий main: вывод задач и очистку временного файла."""
        output = io.StringIO()
        with redirect_stdout(output):
            main()
        stdout = output.getvalue()
        self.assertIn("Регистрация источников", stdout)
        self.assertIn("Все источники успешно прошли проверку контракта!", stdout)
        self.assertIn("ID: file_1", stdout)
        self.assertIn("ID: id_0", stdout)
        self.assertIn("ID: 1", stdout)
        self.assertFalse(os.path.exists("test.json"))


if __name__ == "__main__":
    unittest.main()
