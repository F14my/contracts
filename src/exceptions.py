class TaskError(Exception):
    """Базовое исключение задачи"""
    pass

class TaskInvalidStateError(TaskError):
    """Нарушение инварианта состояния"""
    pass

class InvalidAttributeError(TaskError):
    """Некорректный атрибут"""
    pass
