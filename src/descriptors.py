from src.exceptions import InvalidAttributeError, TaskInvalidStateError

class IdDescriptor:
    """Data descriptor для валидации Id"""

    def __set_name__(self, owner, name):
        self.private_name = f"_{name}"

    def __get__(self, instance, owner) -> int:
        if instance is None:
            raise InvalidAttributeError
        return getattr(instance, self.private_name)

    def __set__(self, instance, value):
        if not isinstance(value, int):
            raise InvalidAttributeError("Должно быть число")
        if value < 0:
            raise InvalidAttributeError("ID должно быть >= 0")
        if hasattr(instance, self.private_name):
            raise TaskInvalidStateError(
                f"Атрибут {self.private_name} нельзя изменить после создания"
            )
        setattr(instance, self.private_name, value)

class ValidatedString:
    """Data descriptor для валидации строк"""

    def __init__(self, min_length: int = 1, max_length: int = None):
        self.min_length = min_length
        self.max_length = max_length

    def __set_name__(self, owner, name):
        self.private_name = f"_{name}"

    def __get__(self, instance, owner) -> str:
        if instance is None:
            raise InvalidAttributeError
        return getattr(instance, self.private_name)

    def __set__(self, instance, value):
        if not isinstance(value, str):
            raise InvalidAttributeError(f"Должна быть строка")
        if len(value) < self.min_length:
            raise InvalidAttributeError(f"Минимальная длина: {self.min_length}")
        if self.max_length and len(value) > self.max_length:
            raise InvalidAttributeError(f"Максимальная длина: {self.max_length}")
        setattr(instance, self.private_name, value)


class PriorityDescriptor:
    """Data descriptor для приоритета (1-10)"""

    def __set_name__(self, owner, name):
        self.private_name = f"_{name}"

    def __get__(self, instance, owner) -> int:
        if instance is None:
            raise InvalidAttributeError
        return getattr(instance, self.private_name)

    def __set__(self, instance, value):
        if not isinstance(value, int):
            raise InvalidAttributeError("Приоритет должен быть целым числом")
        if value < 1 or value > 10:
            raise InvalidAttributeError("Приоритет должен быть от 1 до 10")
        setattr(instance, self.private_name, value)


class LazyComputedProperty:
    """Non-Data Descriptor"""

    def __init__(self, func):
        self.func = func

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return self.func(instance)
