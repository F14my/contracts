from src.models import Task


class TaskQueueIterator:
    """
    Итератор для обхода очереди задач.

    Реализует протокол итератора Python:
    __iter__() возвращает self
    __next__() возвращает следующую задачу или StopIteration
    """

    def __init__(self, tasks: list[Task]):
        """
        Инициализация итератора.

        Args:
            tasks: Копия списка задач для безопасной итерации
        """
        self._tasks = tasks
        self._index = 0

    def __iter__(self) -> TaskQueueIterator:
        """Возвращает сам итератор (протокол итерации)."""
        return self

    def __next__(self) -> Task:
        """
        Возвращает следующую задачу.

        Returns:
            Task: Следующая задача в очереди

        Raises:
            StopIteration: Когда все задачи пройдены
        """
        if self._index >= len(self._tasks):
            raise StopIteration

        task = self._tasks[self._index]
        self._index += 1
        return task

    def __repr__(self) -> str:
        return f"TaskQueueIterator(index={self._index}, total={len(self._tasks)})"