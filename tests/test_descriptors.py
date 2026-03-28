"""
Тесты для дескрипторов.
Проверяют валидацию, защиту инвариантов и различия Data/Non-Data.
"""
import pytest
from src.descriptors import (
    IdDescriptor,
    ValidatedString,
    PriorityDescriptor,
    LazyComputedProperty,
)
from src.exceptions import InvalidAttributeError, TaskInvalidStateError


class DummyClass:
    """Вспомогательный класс для тестов дескрипторов"""
    id = IdDescriptor()
    name = ValidatedString(min_length=2, max_length=20)
    priority = PriorityDescriptor()

    @LazyComputedProperty
    def is_important(self):
        return self.priority >= 8


class TestIdDescriptor:
    """Тесты для IdDescriptor"""

    def test_valid_id(self):
        obj = DummyClass()
        obj.id = 42
        assert obj.id == 42

    def test_id_must_be_int(self):
        obj = DummyClass()
        with pytest.raises(InvalidAttributeError, match="Должно быть число"):
            obj.id = "not_an_int"

    def test_id_must_be_non_negative(self):
        obj = DummyClass()
        with pytest.raises(InvalidAttributeError, match=">= 0"):
            obj.id = -1

    def test_id_immutable_after_set(self):
        obj = DummyClass()
        obj.id = 1
        with pytest.raises(TaskInvalidStateError, match="нельзя изменить"):
            obj.id = 2

    def test_id_access_via_class(self):
        with pytest.raises(InvalidAttributeError):
            _ = DummyClass.id


class TestValidatedString:
    """Тесты для ValidatedString"""

    def test_valid_string(self):
        obj = DummyClass()
        obj.name = "Hello"
        assert obj.name == "Hello"

    def test_min_length_violation(self):
        obj = DummyClass()
        with pytest.raises(InvalidAttributeError, match="Минимальная длина"):
            obj.name = "A"

    def test_max_length_violation(self):
        obj = DummyClass()
        with pytest.raises(InvalidAttributeError, match="Максимальная длина"):
            obj.name = "A" * 21

    def test_must_be_string(self):
        obj = DummyClass()
        with pytest.raises(InvalidAttributeError, match="Должна быть строка"):
            obj.name = 123

    def test_empty_string(self):
        obj = DummyClass()
        with pytest.raises(InvalidAttributeError):
            obj.name = ""

    def test__min_length(self):
        obj = DummyClass()
        obj.name = "AB"
        assert obj.name == "AB"

    def test_max_length(self):
        obj = DummyClass()
        obj.name = "A" * 20
        assert obj.name == "A" * 20


class TestPriorityDescriptor:
    """Тесты для PriorityDescriptor"""

    def test_valid_priority(self):
        obj = DummyClass()
        for val in [1, 5, 10]:
            obj.priority = val
            assert obj.priority == val

    def test_priority_below_range(self):
        obj = DummyClass()
        with pytest.raises(InvalidAttributeError, match="от 1 до 10"):
            obj.priority = 0

    def test_priority_above_range(self):
        obj = DummyClass()
        with pytest.raises(InvalidAttributeError, match="от 1 до 10"):
            obj.priority = 11

    def test_priority_must_be_int(self):
        obj = DummyClass()
        with pytest.raises(InvalidAttributeError, match="целым числом"):
            obj.priority = 5.5


class TestLazyComputedProperty:
    """Тесты для Non-Data Descriptor"""

    def test_computed_value(self):
        obj = DummyClass()
        obj.priority = 7
        assert obj.is_important is False

        obj.priority = 9
        assert obj.is_important is True


    def test_can_override_via_instance_dict(self):
        """Non-data descriptor можно перекрыть через __dict__"""
        obj = DummyClass()
        obj.priority = 5

        obj.__dict__["is_important"] = True
        assert obj.__dict__["is_important"] is True
        assert obj.is_important is True


class TestDataNonDataDemonstration:
    """Интеграционный тест: демонстрация различий"""

    def test_data_descriptor_ignores_dict(self):
        """Data descriptor игнорирует прямую запись в __dict__"""
        obj = DummyClass()
        obj.priority = 5
        obj.__dict__["priority"] = 100
        assert obj.priority != 5

    def test_non_data_allows_dict_override(self):
        """Non-data descriptor позволяет записать в __dict__"""
        obj = DummyClass()
        obj.__dict__["is_important"] = "OVERRIDDEN"
        assert obj.__dict__["is_important"] == "OVERRIDDEN"
