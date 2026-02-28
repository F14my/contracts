from typing import Protocol, runtime_checkable, Any, Generator


@runtime_checkable
class TaskContract(Protocol):
    """
    Единый контракт для всех источников задач.
    Каждый источник обязан реализовать метод get_tasks.
    """
    def get_tasks(self) -> list[Any] | Generator[Any, None, None]:
        ...