# Лабораторная работа №3

---
Итераторы, генераторы и ленивая обработка данных в Python

### Основные возможности

- Протокол итерации: реализация __iter__/__next__ с корректной обработкой StopIteration
- Повторная итерация: возможность многократного обхода коллекции без ограничений
- Ленивые фильтры: методы filter_by_status, filter_by_priority, filter возвращают генераторы 
- Эффективность памяти: обработка больших объёмов данных без загрузки всех элементов в память 
- Совместимость с Python: поддержка for, list(), sum(), max(), any(), all() 


## Структура проекта

```
src/
├── models.py            # Task, TaskStatus из лабы 2
├── descriptors.py       # Дескрипторы из лабы 2
├── exceptions.py        # Исключения из лабы 2
├── iterators.py         # TaskQueueIterator
├── queue.py             # TaskQueue с итераторами и генераторами
└── main.py              # Демонстрация использования

tests/
├── test_queue.py        # Тесты с полным покрытием
└── ...                  # Тесты из лабы 2
```

## Установка и запуск

```bash
# Клонирование репозитория
git clone https://github.com/F14my/contracts.git
cd contracts
git checkout main_iterators_generators

pip install -r requirements.txt

# Запуск тестов
pytest tests/ -v

# Точка входа
python -m src.main
```

### Реализованные компоненты

#### TaskQueueIterator (Iterator)
```python
class TaskQueueIterator:
    """Итератор для обхода очереди задач"""
    # - Реализует протокол: __iter__() → self, __next__() → Task | StopIteration
    # - Хранит копию списка задач и текущий индекс
    # - Позволяет повторную итерацию
```

#### TaskQueue (Iterable)
```python
class TaskQueue:
    """Очередь задач с поддержкой итерации и ленивой фильтрации"""
    # Базовые методы
    - add(task: Task) → None                    # Добавление задачи
    - add_many(tasks: Iterable[Task]) → None    # Добавление нескольких задач
    - __iter__() → TaskQueueIterator            # Протокол итерации
    - __len__() → int                           # Количество задач
    - __getitem__(index: int) → Task            # Доступ по индексу
    - clear() → None                            # Очистка очереди
    - is_empty() → bool                         # Проверка на пустоту
    
    # Ленивые фильтры
    - filter_by_status(status: TaskStatus)      # Фильтр по статусу
    - filter_by_priority(min, max)              # Фильтр по диапазону приоритета
    - filter(predicate: Callable[[Task], bool]) # Универсальный фильтр
    
    - map(func: Callable[[Task], Any])          # Применение функции к задачам
```

## Тестирование
### Покрытие тестами
- Базовые операции
- Протокол итерации
- Повторная итерация
- Совместимость с Python
- Фильтрация по статусу
- Фильтрация по приоритету
- Универсальный фильтр
- Ленивые вычисления
- Преобразование данных
- Производительность


### Запуск тестов

```bash
pytest tests/test_queue.py
```



