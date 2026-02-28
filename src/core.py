from typing import Any
from src.contracts import TaskContract
from src.models import Task


class TaskSystem:
    """
    Подсистема приёма задач.
    Управляет источниками и собирает из них данные через единый контракт.
    """

    def __init__(self):
        self._sources: list[TaskContract] = []

    def register_source(self, source: Any) -> None:
        """Регистрирует новый источник после runtime-проверки контракта"""
        if not isinstance(source, TaskContract):
            raise TypeError(f"Источник {type(source).__name__} не поддерживает контракт!")
        self._sources.append(source)

    def collect_tasks(self) -> list[Task]:
        """Опрашивает все зарегистрированные источники и собирает задачи в список"""
        all_task = []
        for source in self._sources:
            all_task.extend(source.get_tasks())
        return all_task
