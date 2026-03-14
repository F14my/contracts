import unittest
import json
import os

from src.core import TaskSystem
from src.models import Task
from src.sources import GeneratorSource, FileSource, ApiSource


class BadSource:
    """'Плохой' источник без метода get_tasks"""

    def wrong_method(self):
        pass


class TestModels(unittest.TestCase):

    def test_task_creation(self):
        """Тестируем корректное создание структуры Task"""
        task = Task(id="test_1", payload={"key": "value"})
        self.assertEqual(task.id, "test_1")
        self.assertEqual(task.payload, {"key": "value"})


class TestSources(unittest.TestCase):
    test_file_name = "test_source_data.json"

    def setUp(self):
        """Создаем реальный тестовый файл перед каждым тестом"""
        data = [{"id": "file_1", "payload": {"task": "real_file_task"}}]
        with open(self.test_file_name, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def tearDown(self):
        """Удаляем тестовый файл после завершения теста"""
        if os.path.exists(self.test_file_name):
            os.remove(self.test_file_name)

    def test_generator_source(self):
        """Тестируем, что генератор создает правильное количество задач"""
        count = 2
        source = GeneratorSource(count=count)
        tasks = source.get_tasks()

        self.assertEqual(len(tasks), count)
        self.assertIsInstance(tasks[0], Task)
        self.assertTrue(tasks[0].id.startswith("id_"))
        self.assertIn("q", tasks[0].payload)

    def test_file_source(self):
        """Тестируем чтение из созданного файла"""
        source = FileSource(self.test_file_name)
        tasks = source.get_tasks()

        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].id, "file_1")
        self.assertEqual(tasks[0].payload["task"], "real_file_task")

    def test_api_source(self):
        """Тестируем ApiSource на корректный парсинг встроенного ответа"""
        source = ApiSource("http://fake.api")
        tasks = source.get_tasks()

        self.assertTrue(len(tasks) > 0)
        self.assertEqual(tasks[0].id, "1")
        self.assertIn("question", tasks[0].payload)

    def test_file_source_empty_list(self):
        """Тестируем чтение из файла с пустым списком []"""
        with open(self.test_file_name, "w", encoding="utf-8") as f:
            json.dump([], f)

        source = FileSource(self.test_file_name)
        tasks = source.get_tasks()
        self.assertEqual(tasks, [])

    def test_generator_zero_count(self):
        """Тестируем генератор с нулевым количеством задач"""
        source = GeneratorSource(count=0)
        self.assertEqual(len(source.get_tasks()), 0)


class TestTaskSystem(unittest.TestCase):

    def setUp(self):
        """Создаем чистую систему задач перед каждым тестом"""
        self.system = TaskSystem()

    def test_register_valid_source(self):
        """Тестируем, что правильный источник успешно регистрируется"""
        valid_source = GeneratorSource(count=1)
        self.system.register_source(valid_source)
        self.assertEqual(len(self.system._sources), 1)

    def test_register_invalid_source_raises_error(self):
        """Тестируем, что источник без метода get_tasks вызывает TypeError"""
        invalid_source = BadSource()
        with self.assertRaises(TypeError):
            self.system.register_source(invalid_source)

    def test_collect_tasks_single_source(self):
        """Тестируем сбор задач из одного источника"""
        source = GeneratorSource(count=3)
        self.system.register_source(source)

        tasks = self.system.collect_tasks()
        self.assertEqual(len(tasks), 3)

    def test_collect_tasks_multiple_sources(self):
        """Тестируем объединение задач из разных источников"""
        gen_source = GeneratorSource(count=2)
        api_source = ApiSource("http://fake.api")

        self.system.register_source(gen_source)
        self.system.register_source(api_source)

        tasks = self.system.collect_tasks()

        self.assertEqual(len(tasks), 4)

    def test_collect_tasks_no_sources(self):
        """Тестируем сбор задач, когда источники еще не добавлены"""
        tasks = self.system.collect_tasks()
        self.assertEqual(tasks, [])
        self.assertIsInstance(tasks, list)


if __name__ == '__main__':
    unittest.main()