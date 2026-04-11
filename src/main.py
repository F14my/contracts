from src.models import Task, TaskStatus
from src.queue import TaskQueue


def generate_sample_tasks(count: int = 10):
    """Генератор задач"""
    for i in range(count):
        yield Task(
            task_id=i + 1,
            description=f"Task {i + 1}",
            priority=(i % 10) + 1,
            status=list(TaskStatus)[i % 4]
        )


def demo_basic_iteration():
    """Демонстрация базовой итерации"""
    print("Базовая итерация")

    queue = TaskQueue()
    queue.add(Task(1, "Deploy prod", priority=10))
    queue.add(Task(2, "Fix bug", priority=5))
    queue.add(Task(3, "Update docs", priority=2))

    print("Все задачи:")
    for task in queue:
        print(f"{task.id}: {task.description} (prio={task.priority})")

    print("Повторная итерация")
    count = sum(1 for _ in queue)
    print(f"Всего задач: {count}")


def demo_lazy_filtering():
    """Демонстрация ленивой фильтрации."""
    print("\nЛенивая фильтрация")

    queue = TaskQueue(generate_sample_tasks(20))

    print("Задачи со статусом PENDING:")
    for task in queue.filter_by_status(TaskStatus.PENDING):
        print(f"{task.id}: {task.description}")

    print("Высокий приоритет (>= 8):")
    for task in queue.filter_by_priority(min_priority=8):
        print(f"{task.id}: {task.description} (prio={task.priority})")

    print("Сложный фильтр (PENDING + high priority):")
    filtered = queue.filter(
        lambda t: t.status == TaskStatus.PENDING and t.priority >= 7
    )
    for task in filtered:
        print(f"{task.id}: {task.description}")


def demo_python_constructs():
    """Совместимость с конструкциями Python."""
    print("\nСовместимость с Python")

    queue = TaskQueue([
        Task(1, "A", priority=5),
        Task(2, "B", priority=3),
        Task(3, "C", priority=7),
    ])

    print(f"len(queue) = {len(queue)}")
    print(f"bool(queue) = {bool(queue)}")
    print(f"queue[0] = {queue[0].description}")

    print(f"сумма приоритетов: {sum(t.priority for t in queue)}")
    print(f"list: {[t.id for t in queue]}")
    print(f"максимальный по приоритету: {max(queue, key=lambda t: t.priority).description}")


def main():
    """Запуск всех демо."""
    demo_basic_iteration()
    demo_lazy_filtering()
    demo_python_constructs()


if __name__ == "__main__":
    main()