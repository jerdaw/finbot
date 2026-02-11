"""
Error Codes and Messages

This module defines constants related to error codes and standard error messages used throughout
the application. These constants help maintain consistency in the error responses and simplify
the error handling logic by providing a centralized source of truth for such information.

Attributes:
    GENERIC_ERROR_CODE (int): Default error code for unspecified errors.
    NOT_FOUND_ERROR_CODE (int): Error code for "not found" errors.
    NOT_FOUND_ERROR_MSG (str): Standard error message for "not found" errors.
"""

from __future__ import annotations

GENERIC_ERROR_CODE = 1000
NOT_FOUND_ERROR_CODE = 1001
NOT_FOUND_ERROR_MSG = "The requested resource was not found."
