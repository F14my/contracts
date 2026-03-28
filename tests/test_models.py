"""
Тесты для модели Task.
Проверяют инварианты, валидацию, переходы состояний.
"""
import pytest
from datetime import datetime
from src.models import Task, TaskStatus
from src.exceptions import InvalidAttributeError, TaskInvalidStateError


class TestTaskCreation:
    """Тесты создания задачи"""

    def test_valid_creation(self):
        task = Task(task_id=1, description="Test task", priority=5)
        assert task.id == 1
        assert task.description == "Test task"
        assert task.priority == 5
        assert task.status == TaskStatus.PENDING
        assert isinstance(task.created_at, datetime)

    def test_custom_status_on_creation(self):
        task = Task(1, "Test", 5, status=TaskStatus.IN_PROGRESS)
        assert task.status == TaskStatus.IN_PROGRESS

    def test_repr(self):
        task = Task(1, "Test", 5)
        repr_str = repr(task)
        assert "Task" in repr_str
        assert "1" in repr_str
        assert "Test" in repr_str


class TaskInvariants:
    """Тесты инвариантов задачи"""

    def test_id_can_change(self):
        task = Task(1, "Test", 5)
        with pytest.raises(TaskInvalidStateError):
            task.id = 2

    def test_description_validated(self):
        task = Task(1, "Test", 5)

        with pytest.raises(InvalidAttributeError):
            task.description = ""

        with pytest.raises(InvalidAttributeError):
            task.description = "A" * 501

        with pytest.raises(InvalidAttributeError):
            task.description = 123

    def test_priority_range(self):
        task = Task(1, "Test", 5)

        with pytest.raises(InvalidAttributeError):
            task.priority = 0
        with pytest.raises(InvalidAttributeError):
            task.priority = 11

    def test_created_at_immutable(self):
        task = Task(1, "Test", 5)
        original = task.created_at

        with pytest.raises(AttributeError):
            task.created_at = datetime(2000, 1, 1)

        assert task.created_at == original


class TestStatusTransitions:
    """Тесты status"""

    @pytest.mark.parametrize("from_status,to_status,should_allow", [
        (TaskStatus.PENDING, TaskStatus.IN_PROGRESS, True),
        (TaskStatus.PENDING, TaskStatus.CANCELLED, True),
        (TaskStatus.PENDING, TaskStatus.DONE, False),

        (TaskStatus.IN_PROGRESS, TaskStatus.DONE, True),
        (TaskStatus.IN_PROGRESS, TaskStatus.CANCELLED, True),
        (TaskStatus.IN_PROGRESS, TaskStatus.PENDING, False),

        (TaskStatus.DONE, TaskStatus.PENDING, False),
        (TaskStatus.DONE, TaskStatus.IN_PROGRESS, False),

        (TaskStatus.CANCELLED, TaskStatus.PENDING, False),
        (TaskStatus.CANCELLED, TaskStatus.DONE, False),
    ])
    def test_status_transitions(self, from_status, to_status, should_allow):
        task = Task(1, "Test", 5, status=from_status)

        if should_allow:
            task.status = to_status
            assert task.status == to_status
        else:
            with pytest.raises(TaskInvalidStateError):
                task.status = to_status

    def test_invalid_status_type(self):
        task = Task(1, "Test", 5)
        with pytest.raises(TaskInvalidStateError):
            task.status = "INVALID"


class TestComputedProperties:
    """Тесты вычисляемых свойств"""

    def test_is_ready_pending_high_priority(self):
        task = Task(1, "Test", priority=8, status=TaskStatus.PENDING)
        assert task.is_ready is True

    def test_is_ready_pending_low_priority(self):
        task = Task(1, "Test", priority=3, status=TaskStatus.PENDING)
        assert task.is_ready is False

    def test_is_ready_not_pending(self):
        task = Task(1, "Test", priority=10, status=TaskStatus.IN_PROGRESS)
        assert task.is_ready is False

    def test_is_high_priority(self):
        task = Task(1, "Test", priority=8)
        assert task.is_high_priority is True

        task.priority = 7
        assert task.is_high_priority is False

    def test_is_critical(self):
        task = Task(1, "Test", priority=10)
        assert task.is_critical is True

        task.priority = 9
        assert task.is_critical is False


class TestPublicApiVsPrivateState:
    """Тесты разделения публичного API и внутреннего состояния"""

    def test_public_properties_exist(self):
        task = Task(1, "Test", 5)

        assert hasattr(task, 'id')
        assert hasattr(task, 'description')
        assert hasattr(task, 'priority')
        assert hasattr(task, 'status')
        assert hasattr(task, 'created_at')
        assert hasattr(task, 'is_ready')

    def test_private_attributes_prefixed(self):
        task = Task(1, "Test", 5)

        assert hasattr(task, '_status')
        assert hasattr(task, '_created_at')

    def test_cannot_set_readonly_via_property(self):
        task = Task(1, "Test", 5)

        with pytest.raises(AttributeError):
            task.created_at = datetime.now()

        with pytest.raises(TaskInvalidStateError):
            task.id = 999