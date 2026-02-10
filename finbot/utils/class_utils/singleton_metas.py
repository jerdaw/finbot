from threading import Lock
from typing import Any


class Reinitializable:
    """
    Base class for reinitializable singleton instances.
    Classes that inherit from this base class must implement the reinitialize method,
    allowing them to update their state upon subsequent instantiations with new arguments.

    Subclasses should ensure that the reinitialize method safely updates instance attributes as needed.
    """

    def reinitialize(self, *args: Any, **kwargs: Any) -> None:
        """
        Reinitialize the singleton instance with new arguments.

        Args:
            *args: Positional arguments for reinitialization.
            **kwargs: Keyword arguments for reinitialization.
        """
        raise NotImplementedError("Subclasses must implement this method.")


class SingletonMetaReinit(type):
    """
    A thread-safe implementation of Singleton that allows controlled re-initialization through the reinitialize method.
    This metaclass ensures that only one instance of a class is created, and provides the mechanism to safely update the
    instance's state on subsequent instantiations.

    Usage:
        class MyClass(Reinitializable, metaclass=SingletonMetaReinit):
            def __init__(self, data):
                self.data = data

            def reinitialize(self, data):
                self.data = data
    """

    _instances: dict[type, Reinitializable] = {}
    _lock: Lock = Lock()

    def __call__(cls, *args: Any, **kwargs: Any) -> Reinitializable:
        with cls._lock:
            if cls not in cls._instances:
                cls._instances[cls] = super().__call__(*args, **kwargs)
            else:
                instance = cls._instances[cls]
                try:
                    instance.reinitialize(*args, **kwargs)
                except Exception as e:
                    raise RuntimeError(f"Failed to reinitialize {cls.__name__} instance: {e}") from e
        return cls._instances[cls]


class SingletonMetaNoReinitNoError(type):
    """
    A thread-safe implementation of Singleton that disallows re-initialization.
    This metaclass ensures that only one instance of a class is created, without allowing state updates on subsequent instantiations.

    Usage:
        class MyClass(metaclass=SingletonMetaNoReinit):
            def __init__(self, data):
                self.data = data
    """

    _instances: dict[type, "SingletonMetaNoReinitNoError"] = {}
    _lock: Lock = Lock()

    def __call__(cls, *args: Any, **kwargs: Any) -> "SingletonMetaNoReinitNoError":
        with cls._lock:
            if cls not in cls._instances:
                cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class SingletonMetaNoReinitError(type):
    """
    A thread-safe implementation of Singleton that disallows re-initialization.
    This metaclass ensures that only one instance of a class is created. Attempts to
    re-instantiate an existing class with new parameters will result in a RuntimeError.

    Usage:
        class MyClass(metaclass=SingletonMetaNoReinitError):
            def __init__(self, data):
                self.data = data
    """

    _instances: dict[type, "SingletonMetaNoReinitError"] = {}
    _lock: Lock = Lock()

    def __call__(cls, *args: Any, **kwargs: Any) -> "SingletonMetaNoReinitError":
        with cls._lock:
            if cls not in cls._instances:
                cls._instances[cls] = super().__call__(*args, **kwargs)
            else:
                raise RuntimeError(f"An instance of {cls.__name__} already exists and cannot be re-initialized.")
        return cls._instances[cls]


if __name__ == "__main__":
    # Example of a reinit class
    class MySingletonReinit(Reinitializable, metaclass=SingletonMetaReinit):
        def __init__(self, data: Any):
            self.data = data

        def reinitialize(self, data: Any) -> None:
            # Implementation of reinitialization logic
            self.data = data

    reinit_a = MySingletonReinit(data=1)
    print(reinit_a.data)  # 1
    reinit_b = MySingletonReinit(data=2)  # Does change the value
    print(reinit_a.data)  # 2
    print(reinit_b.data)  # 2

    # Example of a non-reinit class with no error
    class MySingletonNoReinitNoError(metaclass=SingletonMetaNoReinitNoError):
        def __init__(self, data: Any):
            self.data = data

    reinit_c = MySingletonNoReinitNoError(data=1)
    print(reinit_c.data)  # 1
    reinit_d = MySingletonNoReinitNoError(data=2)  # Doesn't change the value
    print(reinit_c.data)  # 1
    print(reinit_d.data)  # 1

    # Example of a non-reinit class with error
    class MySingletonNoReinitError(metaclass=SingletonMetaNoReinitError):
        def __init__(self, data: Any):
            self.data = data

    reinit_e = MySingletonNoReinitError(data=1)
    print(reinit_e.data)  # 1
    reinit_f = MySingletonNoReinitError(data=2)  # Raises error
