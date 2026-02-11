"""Scrape popular FRED series IDs from FRED website.

Scrapes the Federal Reserve Economic Data (FRED) website to identify
currently popular economic data series based on page view statistics.
Results are cached to JSON for 30 days to avoid excessive scraping.

Scraping details:
    - Uses BeautifulSoup to parse FRED series tables
    - Multithreaded scraping for performance
    - Filters for USA nation-tagged series sorted by popularity
    - Default: scrapes top 10 pages (varies by page size)

Typical usage:
    - Discovery of trending economic indicators
    - Building comprehensive economic dashboards
    - Identifying newly relevant data series
"""

from concurrent.futures import ThreadPoolExecutor
from threading import Lock

import pandas as pd
from bs4 import BeautifulSoup

from finbot.constants.path_constants import FRED_DATA_DIR
from finbot.utils.json_utils.load_json import load_json
from finbot.utils.json_utils.save_json import save_json
from finbot.utils.request_utils.request_handler import RequestHandler

DEFAULT_MAX_PAGES = 10


def _scrape_fred_page_for_symbols(max_pages: int) -> list[str]:
    """
    Scrape the FRED database names from a specified number of pages.

    Args:
        max_pages (int): The maximum number of pages to scrape.

    Returns:
        List[str]: A list of database names scraped from the FRED website.

    Raises:
        ValueError: If unable to parse FRED database name from the href attribute.
    """
    db_names_ordered: list[str] = []
    lock = Lock()  # For thread-safe access to shared data structures

    def _process_fred_page(page_n: int) -> None:
        """
        Process a single page from the FRED website and update the database names.

        Args:
            page_n (int): The page number to process.
        """
        nonlocal db_names_ordered
        req_url = f"https://fred.stlouisfed.org/tags/series?ob=pv&od=desc&t=nation%3Busa&et=&pageID={page_n}"
        html = RequestHandler().make_text_request(url=req_url)
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table", id="series-pager")
        soup = BeautifulSoup(str(table), "html.parser")
        hrefs = soup.findAll("a", href=True)

        local_ordered = []
        for href in hrefs:
            cur_id = href.attrs["href"].split("/")[-1].upper()
            if not cur_id:
                raise ValueError(f"Unable to parse FRED database name for href: {href}")
            local_ordered.append(cur_id)

        with lock:  # Ensure thread-safe update
            for item in local_ordered:
                db_names_ordered.append(item)

    with ThreadPoolExecutor() as executor:
        executor.map(_process_fred_page, range(1, max_pages + 1))

    # Remove duplicates while preserving order
    db_names_ordered = list(dict.fromkeys(db_names_ordered))

    return db_names_ordered


def get_popular_fred_symbols(
    force_update: bool = False,
    auto_update_days: int | None = None,
    max_pages_to_scrape: int | None = None,
) -> list[str]:
    """
    Get a list of popular database names from the FRED website, either by reading from a file or updating by scraping.

    Args:
        force_update (bool): Force the update of the database names by scraping. Defaults to False.
        auto_update_days (int | None): The number of days after which the database should be updated. Defaults to 30.
        max_pages_to_scrape (int | None): The maximum number of pages to scrape from the FRED website. Defaults to 10.

    Returns:
        List[str]: A list of popular database names.
    """
    if auto_update_days is None:
        auto_update_days = 30
    if max_pages_to_scrape is None:
        max_pages_to_scrape = DEFAULT_MAX_PAGES

    save_dir = FRED_DATA_DIR
    file_name = "popular_fred_db_symbols.json"
    file_path = save_dir / file_name

    # consider the file outdated if it doesn't exist or if it hasn't been updated in auto_update_days days
    is_outdated = (
        not file_path.exists()
        or (pd.Timestamp.now() - pd.Timestamp(file_path.stat().st_mtime, unit="s")).days >= auto_update_days
    )

    if force_update or is_outdated:
        db_names = _scrape_fred_page_for_symbols(max_pages=max_pages_to_scrape)
        save_json(save_dir=save_dir, file_name=file_name, data=db_names, compress=False)
    else:
        db_names = list(load_json(file_path=file_path))
        if not isinstance(db_names, list):
            raise TypeError(f"Expected list, got {type(db_names)}")

    return db_names


if __name__ == "__main__":
    prev_symbols = get_popular_fred_symbols(force_update=False)
    updated_symbols = get_popular_fred_symbols(force_update=True)
    print(f"Previous symbols: {prev_symbols}\n")
    print(f"Updated symbols: {updated_symbols}\n")
    print(f"Symbols removed: {set(prev_symbols) - set(updated_symbols)}\n")
    print(f"Symbols added: {set(updated_symbols) - set(prev_symbols)}")
