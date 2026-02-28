from src.models import Task
import json
import time


class FileSource:
    """Источник, загружающий задачи из локального JSON файла"""

    def __init__(self, file_name: str):
        self.file_name = file_name

    def get_tasks(self) -> list[Task]:
        with open(self.file_name, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [Task(id=str(item["id"]), payload=item["payload"]) for item in data]


class GeneratorSource:
    """Источник, генерирующий заданное количество задач"""

    def __init__(self, count: int):
        self.count = count

    def get_tasks(self) -> list[Task]:
        return [Task(id=f"id_{i}", payload={"q": f"generated_question_{i}", "a": f"generated_answer_{i}"}) for i in
                range(self.count)]


class ApiSource:
    """API-заглушка, имитирующая получение задач через API"""

    def __init__(self, endpoint_url: str):
        self.endpoint_url = endpoint_url
        self._mock_json_response = '''
            [
              {
                "id": "1",
                "payload": {
                  "question": "1 + 1 = ?",
                  "answer": "2"
                }
              },
              {
                "id": "2",
                "payload": {
                  "question": "2 + 2 = ?",
                  "answer": "4"
                }
              }
            ]
        '''

    def get_tasks(self) -> list[Task]:
        print(f"Подключение к {self.endpoint_url}...")
        time.sleep(1.5)
        raw_data = json.loads(self._mock_json_response)
        tasks = []
        for item in raw_data:
            task_id = item.pop("id")
            task = Task(id=task_id, payload=item["payload"])
            tasks.append(task)
        return tasks
