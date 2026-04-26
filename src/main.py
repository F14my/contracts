import asyncio
import logging
from src.async_executor import AsyncTaskExecutor, BaseTaskHandler
from src.models import Task, TaskStatus
from src.queue import TaskQueue


class ReadyTaskHandler(BaseTaskHandler):
    """Обработчик задач, готовых к выполнению (PENDING + priority >= 5)."""

    def can_handle(self, task: Task) -> bool:
        return task.is_ready

    async def handle(self, task: Task) -> None:
        await asyncio.sleep(0)
        task.status = TaskStatus.IN_PROGRESS


class FallbackTaskHandler(BaseTaskHandler):
    """Обработчик для остальных задач."""

    def can_handle(self, task: Task) -> bool:
        return True

    async def handle(self, task: Task) -> None:
        await asyncio.sleep(0)


async def demo_async_executor() -> None:
    """
    Демонстрация

    Использует:
        - Task из models.py;
        - TaskQueue;
        - AsyncTaskExecutor.
    """
    logging.basicConfig(level=logging.INFO)

    task_queue = TaskQueue([
        Task(task_id=1, description="Deploy", priority=9, status=TaskStatus.PENDING),
        Task(task_id=2, description="Docs", priority=2, status=TaskStatus.PENDING),
        Task(task_id=3, description="Fix bug", priority=10, status=TaskStatus.PENDING),
    ])

    executor = AsyncTaskExecutor(workers=2)
    executor.register_handler(ReadyTaskHandler())
    executor.register_handler(FallbackTaskHandler())
    await executor.process_queue(task_queue)


if __name__ == "__main__":
    asyncio.run(demo_async_executor())
