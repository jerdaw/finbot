"""
Custom Exceptions

Custom exception classes for the application.
"""

from __future__ import annotations


class InvalidExtensionError(ValueError):
    """Exception raised for errors in the input due to invalid file extension."""

    def __init__(self, message="File has an invalid extension. Please provide a valid file extension."):
        super().__init__(message)


class SaveError(Exception):
    """Exception raised for errors that occur during saving process."""

    def __init__(self, message="An error occurred while saving data. Please check your data object."):
        super().__init__(message)


class LoadError(Exception):
    """Exception raised for errors that occur during loading process."""

    def __init__(self, message="An error occurred while loading data. Please check your file."):
        super().__init__(message)


class ParseError(Exception):
    """Custom exception for parsing errors."""

    def __init__(self, message="An error occurred while parsing data. Please check the data format."):
        super().__init__(message)


class DataTypeError(Exception):
    """Custom exception for data type related errors."""

    def __init__(self, message="An error occurred regarding data types. Please check the data types used."):
        super().__init__(message)
