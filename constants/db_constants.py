"""
DB Constants

This module provides constants related to database operations, including connection strings,
retry intervals, timeout settings, and database-specific parameters. These constants help in
centralizing the configuration for database interactions.

Attributes:
    DB_RETRY_INTERVAL (int): Interval in seconds to wait between retry attempts on failed operations.
    MAX_CONNECTIONS (int): Maximum number of database connections in the connection pool.
"""
from __future__ import annotations
