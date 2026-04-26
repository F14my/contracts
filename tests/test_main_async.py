import asyncio
import logging

import pytest

import src.main as main_async
from src.async_executor import AsyncTaskExecutor, BaseTaskHandler, TaskProcessingError
from src.contracts import AsyncTaskHandlerContract
from src.models import Task, TaskStatus
from src.queue import TaskQueue


def run(coro):
    """Запускает coroutine в синхронном тесте."""
    return asyncio.run(coro)


class SpyLogHandler(logging.Handler):
    """Сохраняет сообщения логгера в список для проверок."""

    def __init__(self):
        super().__init__()
        self.messages: list[str] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.messages.append(record.getMessage())


class SpyHandler(BaseTaskHandler):
    """Тестовый обработчик задач с опциональным падением по ID."""

    def __init__(self, min_priority: int = 1, fail_ids: set[int] | None = None):
        super().__init__()
        self.min_priority = min_priority
        self.fail_ids = fail_ids or set()
        self.handled: list[int] = []
        self.enter_calls = 0
        self.exit_calls = 0

    async def __aenter__(self):
        self.enter_calls += 1
        return await super().__aenter__()

    async def __aexit__(self, exc_type, exc, tb):
        self.exit_calls += 1
        await super().__aexit__(exc_type, exc, tb)

    def can_handle(self, task: Task) -> bool:
        return task.priority >= self.min_priority

    async def handle(self, task: Task) -> None:
        await asyncio.sleep(0)
        if task.id in self.fail_ids:
            raise ValueError(f"boom-{task.id}")
        self.handled.append(task.id)


class InvalidHandler:
    """Объект без AsyncTaskHandlerContract."""

    pass


def test_base_handler_initial():
    """BaseTaskHandler по умолчанию закрыт."""
    assert BaseTaskHandler().is_open is False


def test_base_handler():
    """Контекст-менеджер открывает и закрывает handler."""
    handler = BaseTaskHandler()

    async def check():
        assert handler.is_open is False
        async with handler:
            assert handler.is_open is True
        assert handler.is_open is False

    run(check())


def test_base_handler_raises():
    """Базовый can_handle обязан выбрасывать NotImplementedError."""
    with pytest.raises(NotImplementedError):
        BaseTaskHandler().can_handle(Task(1, "a", 1))


@pytest.mark.parametrize("workers", [0, -1])
def test_executor_invalid_workers(workers):
    """Executor запрещает workers < 1."""
    with pytest.raises(ValueError):
        AsyncTaskExecutor(workers=workers)


def test_executor_errors_property():
    """Коллекция ошибок изначально пустая."""
    assert AsyncTaskExecutor().errors == ()


def test_executor_registers_valid_handler():
    """Executor принимает валидный обработчик."""
    executor = AsyncTaskExecutor()
    executor.register_handler(SpyHandler())
    assert executor.errors == ()


def test_executor_rejects_invalid_handler():
    """Executor отклоняет объект без нужного контракта."""
    with pytest.raises(TypeError):
        AsyncTaskExecutor().register_handler(InvalidHandler())


def test_handler_matches_runtime_protocol():
    """SpyHandler проходит runtime-проверки протокола."""
    handler = SpyHandler()
    assert issubclass(SpyHandler, AsyncTaskHandlerContract)
    assert isinstance(handler, AsyncTaskHandlerContract)


def test_task_processing_error():
    """Строка TaskProcessingError содержит ID задачи."""
    err = TaskProcessingError(task=Task(67, "x", 1), original_error=ValueError("Six Seven Error"))
    assert "67" in str(err)


def test_dispatch_without_handlers():
    """Dispatch без обработчиков накапливает LookupError."""
    executor = AsyncTaskExecutor()
    task = Task(1, "x", 1)
    run(executor._dispatch(task, []))
    assert len(executor.errors) == 1
    assert isinstance(executor.errors[0].original_error, LookupError)


def test_dispatch_exception():
    """Ошибка в handler попадает в errors и лог."""
    logger = logging.getLogger("tests.main_async.dispatch.fail")
    logger.setLevel(logging.INFO)
    log_sink = SpyLogHandler()
    logger.handlers[:] = [log_sink]

    executor = AsyncTaskExecutor(logger=logger)
    handler = SpyHandler(min_priority=1, fail_ids={4})
    run(executor._dispatch(Task(4, "bad", 4), [handler]))

    assert len(executor.errors) == 1
    assert isinstance(executor.errors[0].original_error, ValueError)
    assert any("Ошибка обработки задачи 4" in msg for msg in log_sink.messages)


def test_worker_stops():
    """Worker завершает цикл на значении None."""
    executor = AsyncTaskExecutor()
    queue: asyncio.Queue[Task | None] = asyncio.Queue()
    run(queue.put(None))
    run(executor._worker(queue, []))
    assert queue.empty() is True


def test_process_tasks_uses_handler():
    """process_tasks открывает и закрывает handler ровно один раз."""
    executor = AsyncTaskExecutor()
    handler = SpyHandler()
    executor.register_handler(handler)
    run(executor.process_tasks([Task(1, "a", 2)]))
    assert handler.enter_calls == 1
    assert handler.exit_calls == 1
    assert handler.is_open is False


def test_process_tasks_continues():
    """Ошибочная задача не останавливает обработку остальных."""
    executor = AsyncTaskExecutor()
    handler = SpyHandler(fail_ids={2})
    executor.register_handler(handler)
    run(executor.process_tasks([Task(1, "ok1", 2), Task(2, "bad", 2), Task(3, "ok2", 2)]))
    assert handler.handled == [1, 3]
    assert len(executor.errors) == 1


def test_process_queue():
    """process_queue полностью опустошает TaskQueue."""
    queue = TaskQueue([Task(1, "a", 1), Task(2, "b", 1)])
    executor = AsyncTaskExecutor()
    executor.register_handler(SpyHandler())
    run(executor.process_queue(queue))
    assert queue.is_empty() is True


def test_process_tasks_with_multiple_workers():
    """Несколько workers обрабатывают все задачи."""
    tasks = [Task(i, f"t{i}", 5) for i in range(1, 21)]
    executor = AsyncTaskExecutor(workers=4)
    handler = SpyHandler()
    executor.register_handler(handler)
    run(executor.process_tasks(tasks))
    assert sorted(handler.handled) == list(range(1, 21))


def test_process_tasks_with_no_handlers():
    """Без обработчиков каждая задача дает ошибку маршрутизации."""
    executor = AsyncTaskExecutor()
    run(executor.process_tasks([Task(1, "a", 1), Task(2, "b", 1)]))
    assert len(executor.errors) == 2
    assert all(isinstance(e.original_error, LookupError) for e in executor.errors)


def test_process_tasks_with_empty():
    """Пустой вход не создает ошибок."""
    executor = AsyncTaskExecutor()
    run(executor.process_tasks([]))
    assert executor.errors == ()


@pytest.mark.parametrize(
    ("status", "priority", "expected"),
    [
        (TaskStatus.PENDING, 5, True),
        (TaskStatus.PENDING, 10, True),
        (TaskStatus.PENDING, 4, False),
        (TaskStatus.IN_PROGRESS, 10, False),
    ],
)
def test_ready_handler_can_handle(status, priority, expected):
    """ReadyTaskHandler принимает только готовые задачи."""
    handler = main_async.ReadyTaskHandler()
    assert handler.can_handle(Task(1, "x", priority=priority, status=status)) is expected


def test_ready_handler_in_progress():
    """ReadyTaskHandler переводит задачу в IN_PROGRESS."""
    handler = main_async.ReadyTaskHandler()
    task = Task(1, "x", priority=9, status=TaskStatus.PENDING)
    run(handler.handle(task))
    assert task.status == TaskStatus.IN_PROGRESS


@pytest.mark.parametrize(
    ("status", "priority"),
    [
        (TaskStatus.PENDING, 1),
        (TaskStatus.DONE, 10),
        (TaskStatus.CANCELLED, 3),
    ],
)
def test_fallback_handler(status, priority):
    """FallbackTaskHandler принимает любую задачу."""
    handler = main_async.FallbackTaskHandler()
    assert handler.can_handle(Task(7, "x", priority=priority, status=status)) is True


def test_fallback_handler_status():
    """FallbackTaskHandler не меняет статус задачи."""
    handler = main_async.FallbackTaskHandler()
    task = Task(1, "x", priority=2, status=TaskStatus.PENDING)
    run(handler.handle(task))
    assert task.status == TaskStatus.PENDING


