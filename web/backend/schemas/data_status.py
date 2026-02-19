"""Pydantic schemas for data status endpoints."""

from __future__ import annotations

from pydantic import BaseModel


class DataSourceInfo(BaseModel):
    """Status of a single data source."""

    name: str
    description: str
    file_count: int
    is_stale: bool
    age_str: str
    size_str: str
    oldest_file: str | None
    newest_file: str | None
    total_size_bytes: int
    max_age_days: int


class DataStatusResponse(BaseModel):
    """Response with all data source statuses."""

    sources: list[DataSourceInfo]
    total_files: int
    total_size_bytes: int
    fresh_count: int
    stale_count: int
