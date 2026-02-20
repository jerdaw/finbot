"""Function decorator for automatic logging with execution timing.

Provides a decorator that automatically logs function entry, exit, argument
types, return types, and execution time. Useful for debugging, profiling,
and understanding function behavior without manual logging.

Typical usage:
    ```python
    from finbot.utils.function_utils.log_with_header_footer import log_with_header_footer


    # Default: Auto-generated header/footer with timing
    @log_with_header_footer()
    def process_data(data, threshold=0.5):
        # Your function code
        return result


    # Custom header and footer
    @log_with_header_footer(header="Starting data processing", footer="Finished data processing")
    def process_data(data):
        return result


    # No timing (just entry/exit logs)
    @log_with_header_footer(timeit=False)
    def quick_function():
        return result


    # Mix custom footer with timing
    @log_with_header_footer(footer="Processing complete")
    def analyze(data):
        return analysis
    ```

Features:
    - Automatic entry/exit logging
    - Execution time measurement (optional)
    - Argument type logging
    - Return value type logging
    - Custom or auto-generated log messages
    - Handles errors gracefully (logs errors, function still executes)

Auto-generated logs (when header/footer=None):
    - Header: Function name, arg count, kwarg count, argument types
    - Footer: Function name, execution time, return count, return types

Example auto-generated logs:
    ```
    # Entry:
    DEBUG: Calling function process_data with 2 args and 1 kwargs.
           args: [<class 'pandas.core.frame.DataFrame'>, <class 'float'>],
           kwargs: [<class 'str'>]

    # Exit:
    DEBUG: Function process_data executed in 0.125 seconds with 2 returns:
           [<class 'pandas.core.frame.DataFrame'>, <class 'dict'>]
    ```

Parameters:
    - header: Custom header message (default: None = auto-generate)
    - footer: Custom footer message (default: None = auto-generate)
    - timeit: Whether to measure execution time (default: True)

Execution timing:
    - Uses time.perf_counter() for high-precision timing
    - Minimal overhead (<0.0001 seconds)
    - Useful for identifying slow functions
    - Included in auto-generated footer

Use cases:
    - Development debugging (trace function calls)
    - Performance profiling (identify slow functions)
    - Production monitoring (track function usage)
    - Understanding complex call chains
    - Automated testing (verify function behavior)

Example workflows:
    ```python
    # Debug mode: Log all function calls
    @log_with_header_footer()
    def step1(data):
        return processed_data


    @log_with_header_footer()
    def step2(data):
        return analyzed_data


    # Production: Custom messages, no automatic type logging
    @log_with_header_footer(header="Starting critical calculation", footer="Critical calculation complete")
    def critical_function(data):
        return result


    # Performance profiling: Focus on timing
    @log_with_header_footer(header="Expensive operation", timeit=True)
    def expensive_operation(data):
        return result
    ```

Type logging:
    - Logs type of each argument (not value)
    - Logs type of each return value (not value)
    - Handles single and multiple returns
    - Useful for debugging type mismatches

Error handling:
    - Logging errors don't prevent function execution
    - Header logging errors → logs error, continues to function
    - Footer logging errors → logs error, returns function result
    - Robust: Won't crash your function due to logging issues

Multiple returns:
    ```python
    @log_with_header_footer()
    def analyze(data):
        return stats, plot, summary  # 3 returns


    # Footer log:
    # Function analyze executed in 0.5s with 3 returns:
    # [<class 'dict'>, <class 'matplotlib.figure.Figure'>, <class 'str'>]
    ```

Decorator pattern:
    - Uses functools.wraps to preserve function metadata
    - __name__, __doc__, __annotations__ preserved
    - Works with help() and IDE inspection
    - Can stack with other decorators

Performance overhead:
    - Negligible for most functions (<0.0001 seconds)
    - Type inspection has minimal cost
    - perf_counter() is very fast
    - Main cost: logger.debug() calls

Best practices:
    ```python
    # Use in development, remove in production (or set log level to INFO)
    # Avoid for very frequently called functions (overhead accumulates)
    # Use custom messages for user-facing operations
    # Use auto-generated logs for debugging

    # Good: Decorate high-level operations
    @log_with_header_footer()
    def run_backtest(strategy, data):
        pass


    # Bad: Decorate inner loop operations
    @log_with_header_footer()  # Called millions of times!
    def calculate_return(price1, price2):
        pass
    ```

Comparison with manual logging:
    ```python
    # Manual logging (verbose)
    def process(data):
        logger.debug(f"Starting process with {type(data)}")
        start = time.perf_counter()
        result = do_work(data)
        elapsed = time.perf_counter() - start
        logger.debug(f"Finished process in {elapsed:.3f}s")
        return result


    # Decorator (clean)
    @log_with_header_footer()
    def process(data):
        return do_work(data)
    ```

Limitations:
    - DEBUG level only (not configurable)
    - Type logging, not value logging (privacy/security)
    - No conditional logging (always logs when function called)
    - Single timing (no per-section timing)

Why type logging (not value logging):
    - Privacy: Don't log sensitive data
    - Size: Values can be huge (DataFrames, large dicts)
    - Security: Avoid logging secrets, credentials
    - Clarity: Types often more useful than values for debugging

Dependencies: logger (from finbot.config), time.perf_counter, functools.wraps

Related modules: Used throughout finbot for debugging and profiling,
especially in services modules.
"""

from collections.abc import Callable, Iterable
from functools import wraps
from time import perf_counter
from typing import Any, ParamSpec, TypeVar, cast

from finbot.config import logger

P = ParamSpec("P")
R = TypeVar("R")


def _is_iterable_not_str(obj: Any) -> bool:
    """Check if an object is iterable but not a string."""
    return isinstance(obj, Iterable) and not isinstance(obj, str)


def _get_len(obj: Any) -> int:
    """Get the length of an object."""
    return len(obj) if _is_iterable_not_str(obj) else 1


def log_with_header_footer(  # noqa: C901 - Decorator with multiple optional parameters
    header: str | None = None,
    footer: str | None = None,
    timeit: bool = True,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Decorator to log header, footer, and runtime for a function."""

    def decorator(func: Callable[P, R]) -> Callable[P, R]:  # noqa: C901 - Nested decorator complexity by design
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:  # noqa: C901 - Logging + timing branches are intentional
            start_time: float | None = None
            try:
                nonlocal header, footer
                if header is None:
                    n_args, n_kwargs = _get_len(args), _get_len(kwargs)
                    arg_types = [type(arg) for arg in args] if _is_iterable_not_str(args) else [type(args)]
                    kwarg_types = [type(kwarg) for kwarg in kwargs.values()] if kwargs else []
                    header = f"Calling function {func.__name__} with {n_args} args and {n_kwargs} kwargs. args: {arg_types}, kwargs: {kwarg_types}"
                logger.debug(header)
                if timeit:
                    start_time = perf_counter()
            except Exception as e:
                logger.error(f"Error in logging wrapper header for function {func.__name__}: {e}")

            result = func(*args, **kwargs)

            try:
                if timeit:
                    if start_time is None:
                        raise RuntimeError("Timing start value missing for timed function execution")
                    execution_time = perf_counter() - start_time

                if footer is None:
                    n_returns = _get_len(result)
                    if _is_iterable_not_str(result):
                        iterable_result = cast(Iterable[Any], result)
                        return_types = [type(r) for r in iterable_result]
                    else:
                        return_types = [type(result)]
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
    def test_func1() -> int:
        """Example function to demonstrate the decorator with logging."""
        print("This is my test func" * 3)
        return 1

    @log_with_header_footer()
    def test_func2() -> tuple[str, int, list[int], dict[str, int]]:
        """Example function to demonstrate the decorator with logging."""
        print("This is my test func" * 3)
        return "Test Function Result", 7, [1, 2, 3], {"a": 1, "b": 2}

    @log_with_header_footer()
    def test_func3(myint: int) -> bool:
        """Example function to demonstrate the decorator with logging."""
        print("This is my test func" * 3)
        return bool(myint)

    test_func1()
    test_func2()
    test_func3(3)
