import asyncio
import logging
from contextlib import AsyncExitStack
from dataclasses import dataclass
from typing import Iterable

from src.contracts import AsyncTaskHandlerContract
from src.models import Task
from src.queue import TaskQueue


@dataclass(slots=True, frozen=True)
class TaskProcessingError:
    """
    Ошибка обработки конкретной задачи.

    Attributes:
        task: Задача, на которой произошла ошибка.
        original_error: Исходное исключение обработчика.
    """

    task: Task
    original_error: Exception

    def __str__(self) -> str:
        return f"Ошибка обработки задачи {self.task.id}: {self.original_error}"


class BaseTaskHandler:
    """
    Базовый асинхронный обработчик задач.
    """

    def __init__(self) -> None:
        self._is_open = False

    @property
    def is_open(self) -> bool:
        """Флаг открытого ресурса обработчика."""
        return self._is_open

    async def __aenter__(self) -> BaseTaskHandler:
        self._is_open = True
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        self._is_open = False

    def can_handle(self, task: Task) -> bool:
        """
        Проверяет, может ли обработчик обработать задачу.

        Args:
            task: Кандидат на обработку.

        Returns:
            bool: True, если обработчик поддерживает задачу.
        """
        raise NotImplementedError

    async def handle(self, task: Task) -> None:
        """
        Асинхронная обработка задачи.

        Args:
            task: Задача для обработки.
        """
        raise NotImplementedError


class AsyncTaskExecutor:
    """
    Асинхронный исполнитель задач.

    Поддерживает:
        - регистрацию обработчиков по контракту
        - конкурентную обработку задач из TaskQueue
        - логирование и централизованный сбор ошибок
    """

    def __init__(self, workers: int = 1, logger: logging.Logger | None = None):
        """
        Инициализация исполнителя.

        Args:
            workers: Количество воркеров.
            logger: Опциональный logger.
        """
        if workers < 1:
            raise ValueError("Количество воркеров должно быть >= 1")
        self._workers = workers
        self._handlers: list[AsyncTaskHandlerContract] = []
        self._errors: list[TaskProcessingError] = []
        self._logger = logger or logging.getLogger(__name__)

    @property
    def errors(self) -> tuple[TaskProcessingError, ...]:
        """Список ошибок обработки."""
        return tuple(self._errors)

    def register_handler(self, handler: AsyncTaskHandlerContract) -> None:
        """
        Регистрирует обработчик задач.

        Args:
            handler: Экземпляр обработчика.

        Raises:
            TypeError: Если объект не реализует контракт обработчика.
        """
        handler_type = type(handler)
        if not isinstance(handler, AsyncTaskHandlerContract) or not issubclass(handler_type, AsyncTaskHandlerContract):
            raise TypeError(f"{handler_type.__name__} не реализует контракт AsyncTaskHandlerContract")
        self._handlers.append(handler)

    async def process_queue(self, task_queue: TaskQueue) -> None:
        """
        Асинхронно обрабатывает все задачи из TaskQueue.

        Args:
            task_queue: Очередь задач.
        """
        tasks = task_queue.drain()
        await self.process_tasks(tasks)

    async def process_tasks(self, tasks: Iterable[Task]) -> None:
        """
        Асинхронно обрабатывает переданный набор задач.

        Args:
            tasks: Последовательность задач.
        """
        queue: asyncio.Queue[Task | None] = asyncio.Queue()
        for task in tasks:
            await queue.put(task)

        async with AsyncExitStack() as stack:
            active_handlers = [await stack.enter_async_context(handler) for handler in self._handlers]
            workers = [
                asyncio.create_task(self._worker(queue, active_handlers), name=f"task-worker-{idx}")
                for idx in range(self._workers)
            ]
            await queue.join()
            for _ in workers:
                await queue.put(None)
            await asyncio.gather(*workers)

    async def _worker(
            self,
            queue: asyncio.Queue[Task | None],
            handlers: list[AsyncTaskHandlerContract],
    ) -> None:
        """Воркер обработки задач."""
        while True:
            task = await queue.get()
            try:
                if task is None:
                    return
                await self._dispatch(task, handlers)
            finally:
                queue.task_done()

    async def _dispatch(self, task: Task, handlers: list[AsyncTaskHandlerContract]) -> None:
        """Маршрутизация задачи на подходящий обработчик."""
        handler = next((item for item in handlers if item.can_handle(task)), None)
        if handler is None:
            error = TaskProcessingError(task=task, original_error=LookupError("Нет обработчика для задачи"))
            self._errors.append(error)
            self._logger.error(str(error))
            return

        try:
            await handler.handle(task)
            self._logger.info(f"Задача {task.id} обработана")
        except Exception as exc:
            error = TaskProcessingError(task=task, original_error=exc)
            self._errors.append(error)
            self._logger.error(str(error))
