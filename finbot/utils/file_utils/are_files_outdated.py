from __future__ import annotations

from collections.abc import Sequence
from datetime import date, datetime, timedelta
from pathlib import Path

from dateutil.relativedelta import relativedelta
from tqdm.contrib.concurrent import thread_map

from config import settings_accessors
from finbot.utils.file_utils.is_file_outdated import is_file_outdated

MAX_THREADS = settings_accessors.MAX_THREADS


def are_files_outdated(
    file_paths: Sequence[Path | str],
    threshold: datetime | date | None = None,
    time_period: str | relativedelta | timedelta | None = None,
    analyze_pandas: bool = False,
    file_time_type: str | None = None,
    align_to_period_start: bool = False,
    raise_error: bool = True,
) -> list[bool]:
    if threshold is not None or time_period is not None:
        raise NotImplementedError(
            "This function does not yet support threshold or time_period.",
        )

    # Using thread_map from tqdm for progress bar
    return list(
        thread_map(
            lambda path: is_file_outdated(
                file_path=path,
                analyze_pandas=analyze_pandas,
                file_time_type=file_time_type,
                align_to_period_start=align_to_period_start,
                file_not_found_error=raise_error,
            ),
            file_paths,
            max_workers=MAX_THREADS,
        ),
    )
