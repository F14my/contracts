from typing import Protocol, runtime_checkable, Any, Generator

from src.models import Task


@runtime_checkable
class TaskContract(Protocol):
    """
    Единый контракт для всех источников задач.
    Каждый источник обязан реализовать метод get_tasks.
    """
    def get_tasks(self) -> list[Any] | Generator[Any, None, None]:
        ...


@runtime_checkable
class AsyncTaskHandlerContract(Protocol):
    """
    Контракт асинхронного обработчика задач.

    Требует:
        - lifecycle через async context manager;
        - can_handle;
        - асинхронный метод handle для обработки задачи.
    """

    async def __aenter__(self) -> AsyncTaskHandlerContract:
        """Подготовка ресурсов обработчика."""

    async def __aexit__(self, exc_type, exc, tb) -> None:
        """Освобождение ресурсов обработчика."""

    def can_handle(self, task: Task) -> bool:
        """Проверяет, может ли обработчик обработать задачу."""

    async def handle(self, task: Task) -> None:
        """Обрабатывает задачу."""
