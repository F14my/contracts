import pytest
from src.models import Task, TaskStatus
from src.queue import TaskQueue

class TestTaskQueueCreation:
    """Тесты создания очереди."""

    def test_create_empty_queue(self):
        """Создание пустой очереди."""
        queue = TaskQueue()
        assert len(queue) == 0
        assert queue.is_empty() is True
        assert bool(queue) is False
        assert repr(queue) == "TaskQueue(tasks=0)"

    def test_create_queue_from_list(self):
        """Создание очереди из списка задач."""
        tasks = [
            Task(1, "Task 1", priority=5),
            Task(2, "Task 2", priority=3),
        ]
        queue = TaskQueue(tasks)
        assert len(queue) == 2
        assert queue.is_empty() is False
        assert bool(queue) is True

    def test_create_queue_from_generator(self):
        """Создание очереди из генератора."""
        def task_gen():
            for i in range(3):
                yield Task(i + 1, f"Task {i + 1}", priority=i + 1)

        queue = TaskQueue(task_gen())
        assert len(queue) == 3
        assert queue[0].id == 1
        assert queue[2].id == 3


class TestAddOperations:
    """Тесты добавления задач."""

    def test_add_single_task(self):
        """Добавление одной задачи."""
        queue = TaskQueue()
        task = Task(1, "New Task", priority=7)
        queue.add(task)

        assert len(queue) == 1
        assert queue[0] is task
        assert queue[0].description == "New Task"

    def test_add_multiple_tasks_sequentially(self):
        """Последовательное добавление задач."""
        queue = TaskQueue()
        queue.add(Task(1, "T1", priority=7))
        queue.add(Task(2, "T2", priority=6))
        queue.add(Task(3, "T3", priority=5))

        assert len(queue) == 3
        assert queue[0].id == 1
        assert queue[1].id == 2
        assert queue[2].id == 3

    def test_add_many_from_list(self):
        """Добавление нескольких задач из списка."""
        queue = TaskQueue()
        tasks = [Task(i, f"T{i}", priority=i) for i in range(1, 6)]
        queue.add_many(tasks)

        assert len(queue) == 5
        assert queue[4].id == 5

    def test_add_many_from_generator(self):
        """Добавление задач из генератора."""
        queue = TaskQueue()

        def gen():
            for i in range(3):
                yield Task(i + 1, f"GenTask {i + 1}", priority=i+1)

        queue.add_many(gen())
        assert len(queue) == 3
        assert queue[0].description == "GenTask 1"


class TestGetItemAndIndexing:
    """Тесты доступа по индексу."""

    def test_getitem_positive_index(self):
        """Доступ по положительному индексу."""
        queue = TaskQueue([Task(i, f"T{i}", priority=i+1) for i in range(3)])
        assert queue[0].id == 0
        assert queue[1].id == 1
        assert queue[2].id == 2

    def test_getitem_negative_index(self):
        """Доступ по отрицательному индексу."""
        queue = TaskQueue([Task(i, f"T{i}", priority=i+1) for i in range(3)])
        assert queue[-1].id == 2
        assert queue[-2].id == 1
        assert queue[-3].id == 0

    def test_getitem_out_of_range(self):
        """Доступ за пределами диапазона."""
        queue = TaskQueue([Task(1, "T1", priority=1)])
        with pytest.raises(IndexError):
            _ = queue[5]
        with pytest.raises(IndexError):
            _ = queue[-5]

    def test_getitem_on_empty_queue(self):
        """Доступ к пустой очереди."""
        queue = TaskQueue()
        with pytest.raises(IndexError):
            _ = queue[0]


class TestClearAndEmpty:
    """Тесты очистки и проверки на пустоту."""

    def test_clear_non_empty_queue(self):
        """Очистка непустой очереди."""
        queue = TaskQueue([Task(i, f"T{i}", priority=i+1) for i in range(5)])
        assert len(queue) == 5
        queue.clear()
        assert len(queue) == 0
        assert queue.is_empty() is True
        assert bool(queue) is False


    def test_is_empty_after_add_and_remove(self):
        """Проверка is_empty после добавления и очистки."""
        queue = TaskQueue()
        assert queue.is_empty() is True

        queue.add(Task(1, "T1", priority=1))
        assert queue.is_empty() is False

        queue.clear()
        assert queue.is_empty() is True


class TestIteration:
    """Тесты итерации."""

    def test_iter_returns_iterator(self):
        """__iter__ возвращает итератор."""
        queue = TaskQueue([Task(1, "T1", priority=1)])
        iterator = iter(queue)
        assert iterator is not None
        assert hasattr(iterator, '__next__')
        assert hasattr(iterator, '__iter__')

    def test_iteration_with_for_loop(self):
        """Итерация через for"""
        queue = TaskQueue([Task(i, f"T{i}", priority=1) for i in range(3)])
        result = []

        for task in queue:
            result.append(task.id)

        assert result == [0, 1, 2]

    def test_iteration_with_next(self):
        """Итерация через next()."""
        queue = TaskQueue([Task(1, "T1", priority=1), Task(2, "T2", priority=2)])
        iterator = iter(queue)

        assert next(iterator).id == 1
        assert next(iterator).id == 2

        with pytest.raises(StopIteration):
            next(iterator)

    def test_iteration_empty_queue(self):
        """Итерация по пустой очереди."""
        queue = TaskQueue()
        count = sum(1 for _ in queue)
        assert count == 0


class TestRepeatedIteration:
    """Тесты повторной итерации"""

    def test_repeated_iteration_same_results(self):
        """Повторная итерация даёт те же результаты."""
        queue = TaskQueue([Task(i, f"T{i}", priority=i+1) for i in range(3)])

        first_pass = [t.id for t in queue]
        second_pass = [t.id for t in queue]
        third_pass = [t.id for t in queue]

        assert first_pass == second_pass == third_pass == [0, 1, 2]

    def test_multiple_iterators_independent(self):
        """Независимость итераторов"""
        queue = TaskQueue([Task(1, "T1", priority=1), Task(2, "T2", priority=2)])

        iter1 = iter(queue)
        iter2 = iter(queue)

        next(iter1)

        assert next(iter2).id == 1
        assert next(iter1).id == 2


class TestIterationWithPythonConstructs:
    """Тесты совместимости с конструкциями Python"""

    def test_sum_with_generator(self):
        """sum() с генератором."""
        queue = TaskQueue([Task(i, f"T{i}", priority=i+1) for i in range(5)])

        total_priority = sum(t.priority for t in queue)
        assert total_priority == 15

    def test_max_min_with_key(self):
        """max() и min() с key функцией."""
        queue = TaskQueue([
            Task(1, "Low", priority=1),
            Task(2, "High", priority=10),
            Task(3, "Mid", priority=5),
        ])

        max_task = max(queue, key=lambda t: t.priority)
        min_task = min(queue, key=lambda t: t.priority)

        assert max_task.id == 2
        assert min_task.id == 1

    def test_any_and_all(self):
        """any() и all() с генераторами."""
        queue = TaskQueue([
            Task(1, "T1", priority=5),
            Task(2, "T2", priority=10),
            Task(3, "T3", priority=3),
        ])

        assert any(t.priority > 8 for t in queue) is True
        assert all(t.priority > 0 for t in queue) is True
        assert all(t.priority > 5 for t in queue) is False

    def test_enumerate(self):
        """enumerate()"""
        queue = TaskQueue([Task(i, f"T{i}", priority=i+1) for i in range(3)])

        result = list(enumerate(queue))

        assert len(result) == 3
        assert result[0] == (0, queue[0])
        assert result[2] == (2, queue[2])


class TestFilterByStatus:
    """Тесты фильтрации по статусу."""

    @pytest.fixture
    def mixed_status_queue(self) -> TaskQueue:
        """Очередь с задачами разных статусов."""
        return TaskQueue([
            Task(1, "Pending 1", status=TaskStatus.PENDING, priority=1),
            Task(2, "InProgress", status=TaskStatus.IN_PROGRESS, priority=2),
            Task(3, "Pending 2", status=TaskStatus.PENDING, priority=3),
            Task(4, "Done", status=TaskStatus.DONE, priority=4),
            Task(5, "Failed", status=TaskStatus.CANCELLED, priority=5),
            Task(6, "Pending 3", status=TaskStatus.PENDING, priority=6),
        ])

    def test_filter_pending(self, mixed_status_queue):
        """Фильтрация PENDING задач."""
        pending = list(mixed_status_queue.filter_by_status(TaskStatus.PENDING))

        assert len(pending) == 3
        assert all(t.status == TaskStatus.PENDING for t in pending)
        assert {t.id for t in pending} == {1, 3, 6}

    def test_filter_in_progress(self, mixed_status_queue):
        """Фильтрация IN_PROGRESS задач."""
        in_progress = list(mixed_status_queue.filter_by_status(TaskStatus.IN_PROGRESS))

        assert len(in_progress) == 1
        assert in_progress[0].id == 2

    def test_filter_completed(self, mixed_status_queue):
        """Фильтрация DONE задач."""
        completed = list(mixed_status_queue.filter_by_status(TaskStatus.DONE))

        assert len(completed) == 1
        assert completed[0].id == 4

    def test_filter_no_matches(self, mixed_status_queue):
        """Фильтрация без совпадений."""
        queue = TaskQueue([
            Task(i, f"T{i}", status=TaskStatus.PENDING, priority=i+1) for i in range(3)
        ])

        failed = list(queue.filter_by_status(TaskStatus.CANCELLED))
        assert len(failed) == 0

    def test_filter_all_match(self, mixed_status_queue):
        """Фильтрация когда все задачи подходят."""
        queue = TaskQueue([
            Task(i, f"T{i}", status=TaskStatus.PENDING, priority=i+1) for i in range(3)
        ])

        pending = list(queue.filter_by_status(TaskStatus.PENDING))
        assert len(pending) == 3



class TestFilterByPriority:
    """Тесты фильтрации по приоритету."""

    @pytest.fixture
    def priority_queue(self) -> TaskQueue:
        """Очередь с задачами разных приоритетов."""
        return TaskQueue([
            Task(1, "Low", priority=1),
            Task(2, "Mid-Low", priority=3),
            Task(3, "Mid", priority=5),
            Task(4, "Mid-High", priority=7),
            Task(5, "High", priority=9),
            Task(6, "Critical", priority=10),
        ])

    def test_filter_min_priority(self, priority_queue):
        """Фильрация по минимальному приоритету."""
        high = list(priority_queue.filter_by_priority(min_priority=7))

        assert len(high) == 3
        assert all(t.priority >= 7 for t in high)
        assert {t.id for t in high} == {4, 5, 6}

    def test_filter_max_priority(self, priority_queue):
        """Фильтрация по максимальному приоритету."""
        low = list(priority_queue.filter_by_priority(max_priority=3))

        assert len(low) == 2
        assert all(t.priority <= 3 for t in low)
        assert {t.id for t in low} == {1, 2}

    def test_filter_priority_range(self, priority_queue):
        """Фильтрация по диапазону приоритетов."""
        mid = list(priority_queue.filter_by_priority(min_priority=3, max_priority=7))

        assert len(mid) == 3
        assert all(3 <= t.priority <= 7 for t in mid)
        assert {t.id for t in mid} == {2, 3, 4}


    def test_filter_no_matches(self, priority_queue):
        """Фильтрация без совпадений."""
        result = list(priority_queue.filter_by_priority(min_priority=100))
        assert len(result) == 0


class TestFilterWithPredicate:
    """Тесты универсального фильтра"""

    @pytest.fixture
    def complex_queue(self) -> TaskQueue:
        """Очередь со сложными данными."""
        return TaskQueue([
            Task(1, "A", priority=10, status=TaskStatus.PENDING),
            Task(2, "B", priority=5, status=TaskStatus.IN_PROGRESS),
            Task(3, "C", priority=8, status=TaskStatus.PENDING),
            Task(4, "D", priority=3, status=TaskStatus.DONE),
            Task(5, "E", priority=10, status=TaskStatus.CANCELLED),
        ])

    def test_filter_complex_condition(self, complex_queue):
        """Сложное условие: высокий приоритет+pending."""
        result = list(complex_queue.filter(
            lambda t: t.priority >= 8 and t.status == TaskStatus.PENDING
        ))

        assert len(result) == 2
        assert {t.id for t in result} == {1, 3}

    def test_filter_or_condition(self, complex_queue):
        """Условие ИЛИ: priority=10 ИЛИ status=CANCELLED."""
        result = list(complex_queue.filter(
            lambda t: t.priority == 10 or t.status == TaskStatus.CANCELLED
        ))

        assert len(result) == 2
        assert {t.id for t in result} == {1, 5}

    def test_filter_always_true(self, complex_queue):
        """Предикат всегда True."""
        result = list(complex_queue.filter(lambda t: True))
        assert len(result) == len(complex_queue)

    def test_filter_always_false(self, complex_queue):
        """Предикат всегда False."""
        result = list(complex_queue.filter(lambda t: False))
        assert len(result) == 0



class TestLazyEvaluation:
    """Тесты ленивых вычислений."""

    def test_filter_not_evaluated_until_iterated(self):
        """Фильтр не вычисляется до итерации."""
        queue = TaskQueue([Task(i, f"T{i}", priority=9) for i in range(1000)])

        filtered = queue.filter_by_priority(min_priority=5)
        count = sum(1 for _ in filtered)
        assert count > 0

    def test_filter_short_circuit(self):
        """Фильтр останавливается при break."""
        queue = TaskQueue([Task(i, f"T{i}", priority=5) for i in range(100)])
        filtered = queue.filter_by_priority(min_priority=0)
        count = 0
        for task in filtered:
            count += 1
            if count == 5:
                break

        assert count == 5

class TestMap:
    """Тесты метода map"""

    def test_map_to_id(self):
        """Map для получения ID."""
        queue = TaskQueue([Task(i, f"T{i}", priority=i+1) for i in range(3)])
        ids = list(queue.map(lambda t: t.id))
        assert ids == [0, 1, 2]

    def test_map_to_priority_sum(self):
        """Map с последующим sum."""
        queue = TaskQueue([Task(i, f"T{i}", priority=i+1) for i in range(5)])
        priorities = queue.map(lambda t: t.priority)
        assert sum(priorities) == 15

    def test_map_returns_generator(self):
        """Map возвращает генератор."""
        queue = TaskQueue([Task(1, "T1", priority=1)])
        result = queue.map(lambda t: t.id)

        import types
        assert isinstance(result, types.GeneratorType)


class TestPerformance:
    """Тесты производительности (корректность работы с большими данными)"""

    def test_large_queue_iteration(self):
        """Итерация большой очереди."""
        queue = TaskQueue([Task(i, f"T{i}", priority=10) for i in range(10000)])
        count = sum(1 for _ in queue)
        assert count == 10000

    def test_filter_large_queue(self):
        """Фильтрация большой очереди."""
        queue = TaskQueue([
            Task(i, f"T{i}", priority=10)
            for i in range(10000)
        ])

        high_priority = queue.filter_by_priority(min_priority=8)
        count = sum(1 for _ in high_priority)
        assert count == 10000
