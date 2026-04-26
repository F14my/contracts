from datetime import datetime
from enum import Enum
from src.exceptions import TaskInvalidStateError
from src.descriptors import ValidatedString, PriorityDescriptor, LazyComputedProperty, IdDescriptor


class TaskStatus(Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"
    CANCELLED = "CANCELLED"


class Task:
    """
    Модель задачи с валидацией и защитой инвариантов.

    Attributes:
        id: Уникальный идентификатор задачи
        description: Описание задачи
        priority: Приоритет (1-10)
        status: Текущий статус
        created_at: Время создания
    """
    __slots__ = ('_id', '_description', '_priority', '_status', '_created_at')
    id = IdDescriptor()
    description = ValidatedString(min_length=1, max_length=500)
    priority = PriorityDescriptor()

    def __init__(
            self,
            task_id: int,
            description: str,
            priority: int,
            status: TaskStatus = TaskStatus.PENDING,
    ):
        self.id = task_id
        self.description = description
        self.priority = priority
        self._status = status
        self._created_at = datetime.now()

    @property
    def status(self) -> TaskStatus:
        """Чтение статуса"""
        return self._status

    @status.setter
    def status(self, value: TaskStatus):
        """
        Контролируемое изменение статуса.

        Инвариант:
        Проверяет допустимые переходы между состояниями.
        """
        if not isinstance(value, TaskStatus):
            raise TaskInvalidStateError(f"Недопустимый статус: {value}")

        valid_transitions = {
            TaskStatus.PENDING: [TaskStatus.IN_PROGRESS, TaskStatus.CANCELLED],
            TaskStatus.IN_PROGRESS: [TaskStatus.DONE, TaskStatus.CANCELLED],
            TaskStatus.DONE: [],
            TaskStatus.CANCELLED: []
        }

        if value not in valid_transitions.get(self._status, []):
            raise TaskInvalidStateError(
                f"Недопустимый переход из {self._status.value} в {value.value}"
            )

        self._status = value

    @property
    def created_at(self) -> datetime:
        """Время создания (только для чтения)"""
        return self._created_at

    @LazyComputedProperty
    def is_ready(self) -> bool:
        """
        Вычисляемое свойство: Готова ли задача к выполнению.

        Инвариант:
        Задача готова, если она в статусе PENDING и приоритет >= 5
        """
        return self._status == TaskStatus.PENDING and self.priority >= 5

    @property
    def is_high_priority(self) -> bool:
        """Вычисляемое свойство: высокий ли приоритет"""
        return self.priority >= 8

    @LazyComputedProperty
    def is_critical(self) -> bool:
        """Задача критическая, если приоритет 10"""
        return self.priority == 10


    def __repr__(self) -> str:
        return (
            f"Task(id={self.id}, description={self.description}, priority={self.priority}, status={self.status})")
