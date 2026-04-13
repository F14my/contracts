from typing import Callable, Generator, Iterable, Optional, Any
from src.models import Task, TaskStatus
from src.iterators import TaskQueueIterator


class TaskQueue:
    """
    Очередь задач с поддержкой:
    Протокола итерации (for, list(), sum())
    Повторной итерации
    Ленивой фильтрации
    """

    def __init__(self, tasks: Optional[Iterable[Task]] = None):
        """
        Инициализация очереди.

        Args:
            tasks: Опционально - начальная коллекция задач
        """
        self._tasks: list[Task] = []
        if tasks is not None:
            self._tasks = list(tasks)

    def add(self, task: Task) -> None:
        """Добавить задачу в очередь."""
        self._tasks.append(task)

    def add_many(self, tasks: Iterable[Task]) -> None:
        """Добавить несколько задач."""
        for task in tasks:
            self.add(task)

    def __iter__(self) -> TaskQueueIterator:
        """
        Возвращает новый итератор для обхода очереди.

        Returns:
            TaskQueueIterator: Новый экземпляр итератора
        """
        return TaskQueueIterator(self._tasks)

    def __len__(self) -> int:
        """Количество задач в очереди."""
        return len(self._tasks)

    def __getitem__(self, index: int) -> Task:
        """Доступ к задаче по индексу."""
        return self._tasks[index]

    def __bool__(self) -> bool:
        """Проверка на пустоту."""
        return bool(self._tasks)

    def __repr__(self) -> str:
        return f"TaskQueue(tasks={len(self._tasks)})"

    def filter_by_status(self, status: TaskStatus) -> Generator[Task, None, None]:
        """
        Ленивый фильтр по статусу задачи.

        Args:
            status: Целевой статус для фильтрации

        Yields:
            Task: Задачи с указанным статусом
        """
        for task in self._tasks:
            if task.status == status:
                yield task

    def filter_by_priority(self, min_priority: Optional[int] = None,
                           max_priority: Optional[int] = None) -> Generator[Task, None, None]:
        """
        Ленивый фильтр по приоритету.

        Args:
            min_priority: Минимальный приоритет (включительно)
            max_priority: Максимальный приоритет (включительно)

        Yields:
            Task: Задачи в диапазоне приоритетов
        """
        for task in self._tasks:
            if min_priority is not None and task.priority < min_priority:
                continue
            if max_priority is not None and task.priority > max_priority:
                continue
            yield task

    def filter(self, predicate: Callable[[Task], bool]) -> Generator[Task, None, None]:
        """
        Универсальный ленивый фильтр.

        Args:
            predicate: Функция, возвращающая True для подходящих задач

        Yields:
            Task: Задачи, удовлетворяющие условию
        """
        for task in self._tasks:
            if predicate(task):
                yield task

    def map(self, func: Callable[[Task], Any]) -> Generator[Any, None, None]:
        """
        Ленивое преобразование задач.

        Args:
            func: Функция для применения к каждой задаче

        Yields:
            Результаты применения функции
        """
        for task in self._tasks:
            yield func(task)

    def clear(self) -> None:
        """Очистить очередь."""
        self._tasks.clear()

    def is_empty(self) -> bool:
        """Проверить пустоту очереди."""
        return len(self._tasks) == 0