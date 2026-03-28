from src.models import Task
import json
import time
import random


class FileSource:
    """Источник, загружающий задачи из локального JSON файла"""

    def __init__(self, file_name: str):
        self.file_name = file_name

    def get_tasks(self) -> list[Task]:
        with open(self.file_name, "r", encoding="utf-8") as f:
            data = json.load(f)

        return [
            Task(task_id=int(item["task_id"]),
                 description=item["description"],
                 priority=item["priority"],
                 status=item["status"]) for item in data]


class GeneratorSource:
    """Источник, генерирующий заданное количество задач"""

    def __init__(self, count: int):
        self.count = count

    def get_tasks(self) -> list[Task]:
        return [Task(
            task_id=i,
            description=f"some_good_description_{i}",
            priority=random.randint(1, 10),
            status=random.choice(["PENDING", "IN_PROGRESS", "DONE", "CANCELED"])) for i in range(self.count)]
#
#
class ApiSource:
    """API-заглушка, имитирующая получение задач через API"""

    def __init__(self, endpoint_url: str):
        self.endpoint_url = endpoint_url
        self._mock_json_response = '''
            [
              {
                "task_id": 1,
                "description": "some_good_description_1",
                "priority": 1,
                "status": "PENDING"
              },
              {
                "task_id": 2,
                "description": "some_good_description_2",
                "priority": 2,
                "status": "DONE"
              }
            ]
        '''

    def get_tasks(self) -> list[Task]:
        print(f"Подключение к {self.endpoint_url}...")
        time.sleep(1)
        raw_data = json.loads(self._mock_json_response)
        tasks = []
        for item in raw_data:
            task = Task(
                task_id=item["task_id"],
                description=item["description"],
                priority=item["priority"],
                status=item["status"]
            )
            tasks.append(task)
        return tasks
