from dataclasses import dataclass


@dataclass
class Task:
    """
    Структура данных для хранения минимальной информации о задаче
    """
    id: str
    payload: dict
