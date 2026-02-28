import unittest
from src.core import TaskSystem
from src.models import Task
from src.sources import GeneratorSource


class BadSource:
    """'Плохой' источник без метода get_tasks"""

    def wrong_method(self):
        pass


class TestTaskSystem(unittest.TestCase):

    def setUp(self):
        """Этот метод запускается перед каждым тестом"""
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

    def test_collect_tasks(self):
        """Тестируем сбор задач из зарегистрированного источника"""
        source = GeneratorSource(count=3)
        self.system.register_source(source)

        tasks = self.system.collect_tasks()

        self.assertEqual(len(tasks), 3)


if __name__ == '__main__':
    unittest.main()
