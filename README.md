# Лабораторная работа №4

---
Асинхронный исполнитель задач.

### Основные возможности

- Обработка задач из `TaskQueue` (реализованной на `asyncio.Queue`)
- Асинхронная обработка через `AsyncTaskExecutor`
- Контракт обработчика через `Protocol` + `runtime_checkable`
- Поддержка `isinstance`/`issubclass` при регистрации обработчиков
- Использование `async context manager` для lifecycle обработчиков
- Централизованное логирование и сбор ошибок обработки
- Расширяемая архитектура: новые типы задач/обработчиков без изменения исполнителя


## Структура проекта

```
src/
├── models.py            # Task
├── descriptors.py       # Дескрипторы
├── exceptions.py        # Исключения
├── iterators.py         # TaskQueueIterator
├── queue.py             # TaskQueue на базе asyncio.Queue
├── async_executor.py    # AsyncTaskExecutor и BaseTaskHandler
└── main.py              # Демо

tests/
├── test_main_async.py   # Тесты ЛР4
└── ...                  # Тесты предыдущих лаб
```

## Установка и запуск

```bash
# Клонирование репозитория
git clone https://github.com/F14my/contracts.git
cd contracts
git checkout main_async

pip install -r requirements.txt

# Запуск тестов
pytest tests/ -v

# Точка входа
python -m src.main_async
```

### Реализованные компоненты

#### AsyncTaskHandlerContract (Protocol)
```python
@runtime_checkable
class AsyncTaskHandlerContract(Protocol):
    async def __aenter__(self): ...
    async def __aexit__(self, exc_type, exc, tb): ...
    def can_handle(self, task: Task) -> bool: ...
    async def handle(self, task: Task) -> None: ...
```

#### AsyncTaskExecutor
```python
class AsyncTaskExecutor:
    # - register_handler(handler)      # Регистрация обработчика по контракту
    # - process_queue(task_queue)      # Обработка задач из TaskQueue
    # - process_tasks(tasks)           # Обработка произвольной коллекции Task
    # - errors                         # Централизованный список ошибок
```

## Тестирование
### Покрытие тестами
- Контракт обработчика через Protocol/runtime_checkable
- Регистрация и маршрутизация задач по типам
- Работа async context manager у обработчиков
- Централизованный сбор ошибок и продолжение обработки
- Логирование ошибок исполнения


### Запуск тестов

```bash
pytest tests/test_main_async.py -v
```
