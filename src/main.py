import json
from src.core import TaskSystem
from src.sources import FileSource, GeneratorSource, ApiSource
import os


def create_dummy_json():
    """Создает тестовый JSON файл для FileSource"""
    data = [
        {"task_id": 1, "description": "some_description", "priority": 1, "status": "PENDING"},
        {"task_id": 2, "description": "some_description2", "priority": 2, "status": "DONE"},
        {"task_id": 3, "description": "some_description3", "priority": 3, "status": "CANCELED"},
        {"task_id": 4, "description": "some_description4", "priority": 4, "status": "IN_PROGRESS"},
    ]
    with open("test.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def delete_dummy_json():
    """Удаляет тестовый JSON файл"""
    os.remove("test.json")


def main():
    create_dummy_json()

    system = TaskSystem()

    file_source = FileSource("test.json")
    gen_source = GeneratorSource(count=2)
    api_source = ApiSource("https://api.example.com/tasks")

    print("Регистрация источников")
    system.register_source(file_source)
    system.register_source(gen_source)
    system.register_source(api_source)
    print("Все источники успешно прошли проверку контракта!\n")

    tasks = system.collect_tasks()

    for task in tasks:
        print(task)

    delete_dummy_json()


if __name__ == "__main__":
    main()