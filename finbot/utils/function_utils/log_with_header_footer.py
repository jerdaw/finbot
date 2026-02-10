from collections.abc import Callable, Iterable
from functools import wraps
from time import perf_counter
from typing import Any

from config import logger


def _is_iterable_not_str(obj: Any) -> bool:
    """Check if an object is iterable but not a string."""
    return isinstance(obj, Iterable) and not isinstance(obj, str)


def _get_len(obj: Any) -> int:
    """Get the length of an object."""
    return len(obj) if _is_iterable_not_str(obj) else 1


def log_with_header_footer(header: str | None = None, footer: str | None = None, timeit: bool = True) -> Callable:
    """Decorator to log header, footer, and runtime for a function."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                nonlocal header, footer
                if header is None:
                    n_args, n_kwargs = _get_len(args), _get_len(kwargs)
                    arg_types = [type(arg) for arg in args] if _is_iterable_not_str(args) else [type(args)]
                    kwarg_types = [type(kwarg) for kwarg in kwargs] if _is_iterable_not_str(kwargs) else [type(kwargs)]  # type: ignore
                    header = f"Calling function {func.__name__} with {n_args} args and {n_kwargs} kwargs. args: {arg_types}, kwargs: {kwarg_types}"
                logger.debug(header)
                if timeit:
                    start_time = perf_counter()
            except Exception as e:
                logger.error(f"Error in logging wrapper header for function {func.__name__}: {e}")

            result = func(*args, **kwargs)

            try:
                if timeit:
                    execution_time = perf_counter() - start_time

                if footer is None:
                    n_returns = _get_len(result)
                    return_types = [type(r) for r in result] if _is_iterable_not_str(result) else [type(result)]
                    footer = f"Function {func.__name__}"
                    if timeit:
                        footer += f" executed in {execution_time} seconds with"
                    footer += f" {n_returns} returns: {return_types}"
                elif timeit:
                    footer += f" with an execution time of {execution_time} seconds"

                logger.debug(footer)
            except Exception as e:
                logger.error(f"Error in logging wrapper footer for function {func.__name__}: {e}")

            return result

        return wrapper

    return decorator


if __name__ == "__main__":
    print()

    @log_with_header_footer(header="CUSTOM WRAPPER HEADER", footer="CUSTOM WRAPPER FOOTER")
    def test_func1():
        """Example function to demonstrate the decorator with logging."""
        print("This is my test func" * 3)
        return 1

    @log_with_header_footer()
    def test_func2():
        """Example function to demonstrate the decorator with logging."""
        print("This is my test func" * 3)
        return "Test Function Result", 7, [1, 2, 3], {"a": 1, "b": 2}

    @log_with_header_footer()
    def test_func3(myint):
        """Example function to demonstrate the decorator with logging."""
        print("This is my test func" * 3)
        return bool(myint)

    test_func1()
    test_func2()
    test_func3(3)
