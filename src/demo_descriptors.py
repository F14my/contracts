from models import Task

def demo_descriptors():
    """Демонстрация различий Data и Non-Data дескрипторов"""


    task = Task(1, "Test", priority=5)

    # Data Descriptor
    print(task.priority)
    task.__dict__["priority"] = 100
    print(task.priority)

    # Non-Data Descriptor
    print(task.is_critical)
    task.__dict__["is_critical"] = True
    print(task.is_critical)


if __name__ == "__main__":
    demo_descriptors()