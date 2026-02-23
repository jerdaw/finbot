"""Data status router — wraps data freshness checking."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from finbot.services.data_quality.check_data_freshness import check_all_freshness
from web.backend.schemas.data_status import DataSourceInfo, DataStatusResponse

router = APIRouter()


@router.get("/", response_model=DataStatusResponse)
def get_data_status() -> DataStatusResponse:
    """Check freshness of all data sources."""
    try:
        statuses = check_all_freshness()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check data freshness: {e}") from e

    sources = []
    total_files = 0
    total_bytes = 0
    fresh = 0
    stale = 0

    for s in statuses:
        sources.append(
            DataSourceInfo(
                name=s.source.name,
                description=s.source.description,
                file_count=s.file_count,
                is_stale=s.is_stale,
                age_str=s.age_str,
                size_str=s.size_str,
                oldest_file=s.oldest_file.isoformat() if s.oldest_file else None,
                newest_file=s.newest_file.isoformat() if s.newest_file else None,
                total_size_bytes=s.total_size_bytes,
                max_age_days=s.source.max_age_days,
            )
        )
        total_files += s.file_count
        total_bytes += s.total_size_bytes
        if s.is_stale:
            stale += 1
        else:
            fresh += 1

    return DataStatusResponse(
        sources=sources,
        total_files=total_files,
        total_size_bytes=total_bytes,
        fresh_count=fresh,
        stale_count=stale,
    )
