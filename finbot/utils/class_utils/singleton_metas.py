"""Thread-safe singleton metaclasses with flexible reinitialization strategies.

Provides three metaclass implementations for the Singleton pattern, each with
different reinitialization behavior. All implementations are thread-safe using
locks to prevent race conditions during instance creation.

Typical usage:
    ```python
    from finbot.utils.class_utils.singleton_metas import (
        Reinitializable,
        SingletonMetaReinit,
        SingletonMetaNoReinitNoError,
        SingletonMetaNoReinitError,
    )


    # 1. Reinitializable singleton (allows state updates)
    class ConfigManager(Reinitializable, metaclass=SingletonMetaReinit):
        def __init__(self, config_path):
            self.config_path = config_path
            self.config = self.load_config()

        def reinitialize(self, config_path):
            self.config_path = config_path
            self.config = self.load_config()


    manager1 = ConfigManager("config.yaml")  # Creates instance
    manager2 = ConfigManager("new_config.yaml")  # Calls reinitialize()
    assert manager1 is manager2  # Same instance


    # 2. Non-reinitializable (ignores new arguments)
    class DatabaseConnection(metaclass=SingletonMetaNoReinitNoError):
        def __init__(self, db_url):
            self.db_url = db_url


    conn1 = DatabaseConnection("db://server1")  # Creates instance
    conn2 = DatabaseConnection("db://server2")  # Same instance, ignores args
    assert conn1.db_url == "db://server1"  # Original value preserved


    # 3. Non-reinitializable (raises error on re-attempt)
    class LicenseManager(metaclass=SingletonMetaNoReinitError):
        def __init__(self, license_key):
            self.license_key = license_key


    lic1 = LicenseManager("KEY123")  # Creates instance
    lic2 = LicenseManager("KEY456")  # Raises RuntimeError
    ```

Three metaclass strategies:

1. **SingletonMetaReinit**: Allows controlled reinitialization
   - First call: Creates instance via __init__()
   - Subsequent calls: Calls reinitialize() with new arguments
   - Requires: Class must inherit from Reinitializable
   - Use when: State updates needed (config reloading, connection refresh)

2. **SingletonMetaNoReinitNoError**: Ignores reinitialization silently
   - First call: Creates instance
   - Subsequent calls: Returns existing instance, ignores arguments
   - Use when: State should never change after creation
   - Fails silently (no error on re-instantiation attempts)

3. **SingletonMetaNoReinitError**: Prevents reinitialization strictly
   - First call: Creates instance
   - Subsequent calls: Raises RuntimeError
   - Use when: Re-instantiation attempts indicate a bug
   - Fails loudly (explicit error on re-instantiation)

Thread safety:
    - All metaclasses use threading.Lock
    - Prevents race conditions during instance creation
    - Safe for multithreaded applications
    - Lock is shared across all instances of a class

Features:
    - Thread-safe instance creation
    - Per-class singleton (not global)
    - Clear error messages
    - Three reinitialization strategies
    - Standard metaclass protocol

Reinitializable base class:
    - Defines reinitialize() contract
    - Must be implemented by subclasses
    - Called on subsequent instantiations
    - Receives same arguments as __init__()

Use cases:

**SingletonMetaReinit**:
    - Configuration managers (reload config)
    - Connection pools (refresh connections)
    - Cache managers (update cache settings)
    - API clients (update credentials)

**SingletonMetaNoReinitNoError**:
    - Logger instances (consistent logging)
    - Database connections (single connection pool)
    - Application settings (immutable after load)

**SingletonMetaNoReinitError**:
    - License managers (ensure single license)
    - Hardware interfaces (prevent multiple initializations)
    - Resource managers (strict single instance)

Example: Config manager with reinitialization:
    ```python
    class Settings(Reinitializable, metaclass=SingletonMetaReinit):
        def __init__(self, env):
            self.env = env
            self.load_settings()

        def reinitialize(self, env):
            if self.env != env:
                self.env = env
                self.load_settings()

        def load_settings(self):
            # Load settings for environment
            pass


    # Development environment
    settings = Settings("development")

    # Switch to production (same instance, reinitialized)
    settings = Settings("production")
    assert settings.env == "production"
    ```

Pattern comparison:
    ```python
    # Traditional singleton (module-level)
    _instance = None


    def get_instance():
        global _instance
        if _instance is None:
            _instance = MyClass()
        return _instance


    # Metaclass singleton (cleaner)
    class MyClass(metaclass=SingletonMetaNoReinitNoError):
        pass


    instance = MyClass()  # Natural instantiation syntax
    ```

Advantages of metaclass approach:
    - Clean instantiation syntax (no get_instance())
    - Thread-safe by default
    - Per-class behavior (not global state)
    - Flexible reinitialization strategies
    - Inheritance support

Disadvantages:
    - More complex than simple module-level singleton
    - Metaclass can be confusing for beginners
    - Harder to test (global state)
    - Can hide dependencies

Best practices:
    ```python
    # Document singleton behavior clearly
    class APIClient(metaclass=SingletonMetaNoReinitNoError):
        \"\"\"Singleton API client. Only one instance exists.\"\"\"
        pass

    # Provide explicit reinitialize if using SingletonMetaReinit
    class ConfigManager(Reinitializable, metaclass=SingletonMetaReinit):
        def reinitialize(self, config):
            # Clear documentation of what happens
            pass

    # Use for true singletons only (not for caching)
    # Consider dependency injection instead of singletons
    ```

Testing singletons:
    ```python
    # Reset singleton for testing
    # (Not provided - singletons are hard to test)

    # Better: Use dependency injection
    def my_function(api_client=None):
        if api_client is None:
            api_client = APIClient()  # Singleton
        # Use api_client
    ```

Dependencies: threading (Lock), typing (type hints)

Related modules: config (uses singleton pattern for settings),
logger (singleton logger instance).
"""

from threading import Lock
from typing import Any

# ruff: noqa: RUF012 - Metaclass class attributes intentionally mutable for singleton pattern


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
