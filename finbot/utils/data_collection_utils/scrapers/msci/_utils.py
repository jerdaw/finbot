"""Scrape MSCI index data using Selenium automation.

Automates web scraping of MSCI index data (World, EAFE, Emerging Markets,
etc.) from the MSCI website using Selenium with headless Firefox. Handles
complex web interactions including date pickers, dropdowns, and dynamic
content loading.

Features:
    - Automated browser control via Selenium WebDriver
    - Handles daily, monthly, and yearly data
    - Incremental updates (only fetches missing dates)
    - Automatic retry logic for web errors
    - Screenshot capture for debugging
    - Excel file parsing from downloads

Typical usage:
    - Historical performance analysis of international indexes
    - Building global equity factor models
    - Backtesting international allocation strategies

Data source: MSCI (Morgan Stanley Capital International)
Update frequency: Daily
Scraping method: Selenium + BeautifulSoup

Note: This code was written quickly and may benefit from refactoring.
"""

import datetime
import os
import re
import time
from pathlib import Path

import pandas as pd
from dateutil.relativedelta import relativedelta
from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC  # noqa: N812 - Standard Selenium convention
from selenium.webdriver.support.ui import Select, WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager

from config import logger, settings_accessors
from constants.path_constants import MSCI_DATA_DIR
from finbot.utils.datetime_utils.get_missing_us_business_dates import get_missing_us_business_dates
from finbot.utils.datetime_utils.get_us_business_dates import get_us_business_dates
from finbot.utils.file_utils.is_file_outdated import is_file_outdated
from finbot.utils.pandas_utils.load_dataframe import load_dataframe
from finbot.utils.pandas_utils.save_dataframe import save_dataframe

MAX_THREADS = settings_accessors.MAX_THREADS


class element_has_style_value:  # noqa: N801 - Selenium expected_condition naming convention
    """An expectation for checking that an element has a particular style value.

    locator - used to find the element
    style_value - the style value to check
    """

    def __init__(self, locator, style_value):
        self.locator = locator
        self.style_value = style_value

    def __call__(self, driver):
        element = driver.find_element(*self.locator)  # Finding the referenced element
        if self.style_value in element.get_attribute("style"):
            return element
        else:
            return False


def _check_loaded(wait, locale_type, do_sleep=0):
    try:
        time.sleep(do_sleep)
        wait.until(element_has_style_value((By.ID, "loading-image-graph"), "display: none"))
        wait.until_not(EC.visibility_of_element_located((By.ID, "loading-image-graph")))
        for check_func in [EC.presence_of_element_located, EC.element_to_be_clickable]:
            for el_txt in ["Term", "Frequency", "Start Date", "End Date"]:
                wait.until(check_func((By.XPATH, f"//label[text()='{el_txt}']/following::div[1]//select")))
            wait.until(check_func((By.XPATH, "//button[text()='Update']")))
            wait.until(check_func((By.XPATH, "//a[text()='Download Data']")))

            for el_id in [
                f"updateTerm{locale_type}",
                f"updateFrequency{locale_type}",
                "startDateFilterShow",
                "endDateFilterShow",
            ]:
                wait.until(check_func((By.ID, el_id)))

        logger.info("Loading completed.")
    except Exception as err:
        logger.info(err)


def _take_screencap(driver, dl_dir_path, file_name=None):
    # Taking a screenshot before clicking the download link
    screenshot_path = os.path.join(dl_dir_path, file_name)
    driver.save_screenshot(screenshot_path)
    logger.info(f"Screenshot saved to {screenshot_path}.")


def _set_term(wait, locale_type, long_wait_time, data_term_options, driver, dl_dir_path, index_name):
    term_select_xpath = "//label[text()='Term']/following::div[1]//select"

    try:
        _check_loaded(wait=wait, locale_type=locale_type)

        term_select_element = wait.until(EC.element_to_be_clickable((By.XPATH, term_select_xpath)))
        term_select = Select(term_select_element)
        for option in data_term_options:
            try:
                term_select.select_by_value(option)
                break
            except NoSuchElementException:
                pass
    except (TimeoutException, NoSuchElementException, StaleElementReferenceException, WebDriverException) as e:
        _take_screencap(driver, dl_dir_path, file_name=f"{index_name}_pre-term-set_screenshot.png")
        logger.warning(f"Failed to set term ({type(e).__name__}: {e}). Retrying in {long_wait_time} seconds.")
        _check_loaded(wait=wait, do_sleep=long_wait_time, locale_type=locale_type)
        # retry
        term_select_element = wait.until(EC.element_to_be_clickable((By.XPATH, term_select_xpath)))
        term_select = Select(term_select_element)
        for option in data_term_options:
            try:
                term_select.select_by_value(option)
                break
            except NoSuchElementException:
                pass
    logger.info(f"Set 'Term' to: {option}.")


def _get_date(date_type, driver):
    valid_date_types = ["start", "end"]
    if date_type not in valid_date_types:
        raise ValueError(f"date_type must be one of {valid_date_types}.")

    try:
        date_input = driver.find_element(By.ID, f"{date_type}DateFilterShow")
        date_str = date_input.get_attribute("value")
        # Assuming the date is in the format "MMM d, YYYY" (e.g., "Jan 1, 2020")
        return datetime.datetime.strptime(date_str, "%b %d, %Y")
    except NoSuchElementException:
        logger.error(f"{date_type.capitalize()} Date input field not found.")
        return None
    except ValueError:
        logger.error(f"Failed to parse the {date_type} date.")
        return None


def _set_frequency(driver, data_frequency, wait, long_wait_time, locale_type, dl_dir_path, index_name):
    # Select the most frequent option ('Daily', 'Monthly', 'Yearly') in the 'Frequency' dropdown
    frequency_select_xpath = "//label[contains(text(), 'Frequency')]/following::div[1]//select"
    try:
        _check_loaded(wait=wait, locale_type=locale_type)
        WebDriverWait(driver, long_wait_time).until(EC.presence_of_element_located((By.XPATH, frequency_select_xpath)))
        frequency_select_element = driver.find_element(By.XPATH, frequency_select_xpath)
        frequency_select = Select(frequency_select_element)
        frequency_select.select_by_visible_text(data_frequency)
    except (TimeoutException, NoSuchElementException, StaleElementReferenceException, WebDriverException) as e:
        _take_screencap(driver, dl_dir_path, file_name=f"{index_name}_pre-term-set_screenshot.png")
        logger.warning(f"Failed to set frequency ({type(e).__name__}: {e}). Retrying in {long_wait_time} seconds.")
        _check_loaded(wait=wait, do_sleep=long_wait_time, locale_type=locale_type)
        WebDriverWait(driver, long_wait_time).until(EC.presence_of_element_located((By.XPATH, frequency_select_xpath)))
        frequency_select_element = driver.find_element(By.XPATH, frequency_select_xpath)
        frequency_select = Select(frequency_select_element)
        frequency_select.select_by_visible_text(data_frequency)
    logger.info(f"Set frequency to {data_frequency}.")


def _get_max_date_range(driver, wait, locale_type, long_wait_time, dl_dir_path, index_name):
    _set_frequency(
        driver=driver,
        data_frequency="Monthly",
        wait=wait,
        long_wait_time=long_wait_time,
        locale_type=locale_type,
        dl_dir_path=dl_dir_path,
        index_name=index_name,
    )
    time.sleep(5)
    _set_term(
        wait=wait,
        locale_type=locale_type,
        long_wait_time=long_wait_time,
        data_term_options=["Full", "Full History"],
        driver=driver,
        dl_dir_path=dl_dir_path,
        index_name=index_name,
    )
    time.sleep(3)
    start_date = _get_date(date_type="start", driver=driver)
    end_date = _get_date(date_type="end", driver=driver)
    return start_date, end_date


def _update_url_date(url, end_date: datetime.datetime):
    # Define the current date in the desired format
    current_date = end_date.strftime("%d/%b/%Y")
    # Define the regular expression pattern for the date format (e.g., 10/Jan/2020)
    date_pattern = r"\d{2}/[Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec]{3}/\d{4}"
    # Replace the date in the original string with the current date
    updated_url = re.sub(date_pattern, current_date, url)

    return updated_url


def _nav_driver(driver, url):
    driver.get(url=url)
    logger.info(f"Selenium driver navigated to {url}.")


def _get_driver(dl_dir_path, long_wait_time, idx_id):
    # Set up Firefox options for headless mode
    firefox_options = FirefoxOptions()
    firefox_options.add_argument("--headless")
    firefox_options.add_argument("--width=1920")
    firefox_options.add_argument("--height=1080")

    # Set Firefox Profile to handle downloads
    firefox_options.set_preference("browser.download.folderList", 2)
    firefox_options.set_preference("browser.download.dir", f"{dl_dir_path!s}/{idx_id}")
    firefox_options.set_preference("browser.download.useDownloadDir", True)
    firefox_options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/vnd.ms-excel")

    # Set up the Selenium WebDriver with headless Firefox
    service = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=firefox_options)
    driver.set_page_load_timeout(long_wait_time)
    return driver


def _set_date(date, date_type, driver, long_wait_time, wait, locale_type, dl_dir_path, index_name):
    valid_date_types = ["start", "end"]
    if date_type not in valid_date_types:
        raise ValueError(f"date_type must be one of {valid_date_types}.")
    date_str = date.strftime("%b %d, %Y")
    try:
        _check_loaded(wait=wait, locale_type=locale_type)
        date_input = driver.find_element(By.ID, f"{date_type}DateFilterShow")
        date_input.clear()  # Clear any pre-filled values
        date_input.send_keys(date_str)
        date_input.send_keys(Keys.ENTER)
    except (TimeoutException, NoSuchElementException, StaleElementReferenceException, WebDriverException) as e:
        _take_screencap(driver, dl_dir_path, file_name=f"{index_name}_pre-term-set_screenshot.png")
        logger.warning(f"Failed to set date ({type(e).__name__}: {e}). Retrying in {long_wait_time} seconds.")
        _check_loaded(wait=wait, do_sleep=long_wait_time, locale_type=locale_type)
        date_input = driver.find_element(By.ID, f"{date_type}DateFilterShow")
        date_input.clear()  # Clear any pre-filled values
        date_input.send_keys(date_str)
        date_input.send_keys(Keys.ENTER)

    logger.info(f"Set {date_type.capitalize()} date to {date_str}.")


def _click_update_btn(wait, locale_type):
    # Click the 'Update' button
    update_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Update']")))
    update_button.click()
    _check_loaded(wait=wait, locale_type=locale_type, do_sleep=2)
    logger.info("Clicked the 'Update' button.")


def _click_download_btn(wait, locale_type, screencap, driver, dl_dir_path, index_name, long_wait_time):
    # Wait for update to complete
    try:
        _check_loaded(wait=wait, locale_type=locale_type)
        download_data_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[text()='Download Data']")))
        if screencap:
            _take_screencap(driver, dl_dir_path, file_name=f"{index_name}_pre-download_screenshot.png")
        dl_start_time = time.time()
        download_data_link.click()
    except (TimeoutException, NoSuchElementException, StaleElementReferenceException, WebDriverException) as e:
        logger.warning(f"Failed to click download ({type(e).__name__}: {e}). Retrying in {long_wait_time} seconds.")
        time.sleep(long_wait_time)
        _check_loaded(wait, do_sleep=long_wait_time, locale_type=locale_type)
        # retry
        download_data_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[text()='Download Data']")))
        if screencap:
            _take_screencap(driver, dl_dir_path, file_name=f"{index_name}_pre-download_screenshot.png")
        dl_start_time = time.time()
        download_data_link.click()
    logger.info("Clicked the 'Download Data' button.")
    return dl_start_time


def _wait_for_download_complete(directory, timeout, start_time=None, new_files_only=True):
    """
    Wait for the download to complete in the specified directory.
    """
    if start_time is None:
        start_time = time.time()

    end_time = start_time + timeout
    prev_files = set(os.listdir(directory))

    while True:
        current_files = set(os.listdir(directory))
        new_files = (current_files - prev_files) if new_files_only else current_files
        if new_files:
            latest_file = max(new_files, key=lambda f: os.path.getctime(os.path.join(directory, f)))
            logger.info(f"Downloaded file found: {latest_file}")

            return os.path.join(directory, latest_file)

        if time.time() > end_time:
            raise TimeoutError("Timed out waiting for download to complete.")

        time.sleep(1)


def _read_msci_data(file_path, index_name=None, remove=True):
    index_name = index_name or "Value"

    try:
        # Open the file to determine the rows to skip and the number of rows to read
        with pd.ExcelFile(file_path) as xls:
            sheet = xls.parse(xls.sheet_names[0], header=None)  # Read without headers
            # Find the index of the row that contains 'Date'
            start_idx = sheet.apply(lambda row: row.astype(str).str.contains("Date").any(), axis=1).idxmax()
            # Find the index of the row before the row that contains 'Copyright'
            end_idx = sheet.apply(lambda row: row.astype(str).str.contains("Copyright").any(), axis=1).idxmax()
    except ValueError:
        # retry specifying format
        with pd.ExcelFile(file_path, engine="xlrd") as xls:
            sheet = xls.parse(xls.sheet_names[0], header=None)  # Read without headers
            start_idx = sheet.apply(lambda row: row.astype(str).str.contains("Date").any(), axis=1).idxmax()
            end_idx = sheet.apply(lambda row: row.astype(str).str.contains("Copyright").any(), axis=1).idxmax()

    # Reopen the file, skipping rows above 'Date' and stopping before 'Copyright'
    data = pd.read_excel(file_path, skiprows=start_idx, nrows=end_idx - start_idx - 1)

    # Assuming the first column is the 'Date' column
    data.columns = pd.Index(["Date", "Data"])  # Rename columns for clarity
    data["Date"] = pd.to_datetime(data["Date"], format="mixed")  # Convert 'Date' column to datetime
    data.set_index("Date", inplace=True)  # Set 'Date' column as index
    data = data.dropna()
    data = data.sort_index()

    # Convert "Value" column from strings to numeric
    if data["Data"].dtype == "object":
        data["Data"] = pd.to_numeric(data["Data"].str.replace(",", "", regex=False), errors="coerce")
    else:
        data["Data"] = pd.to_numeric(data["Data"], errors="coerce")

    # Rename file
    if remove and os.path.exists(file_path):
        os.remove(file_path)
        logger.info(f"Removed temporary data: {file_path}")

    return data


def _process_download(wait, locale_type, dl_dir_path, dl_start_time, long_wait_time, index_name, idx_id):
    dl_dir_path = dl_dir_path / idx_id
    try:
        # _check_loaded(wait=wait, locale_type=locale_type)
        file_path = _wait_for_download_complete(
            directory=dl_dir_path,
            timeout=long_wait_time,
            start_time=dl_start_time,
            new_files_only=True,
        )
    except (FileNotFoundError, TimeoutError, OSError) as e:
        logger.warning(
            f"Failed to find downloaded file ({type(e).__name__}: {e}). Retrying in {long_wait_time} seconds."
        )
        _check_loaded(wait=wait, do_sleep=long_wait_time, locale_type=locale_type)
        file_path = _wait_for_download_complete(
            directory=dl_dir_path,
            timeout=long_wait_time,
            start_time=dl_start_time,
            new_files_only=False,
        )
        # TODO
    return _read_msci_data(file_path=file_path, index_name=index_name)


def _download_msci_single(
    driver,
    wait,
    locale_type,
    url: str,
    dl_dir_path: Path,
    index_name: str,
    idx_id: str,
    long_wait_time: int,
    data_term_options: list | None = None,
    data_frequency: str | None = None,
    start_date: None | datetime.datetime = None,
    end_date: None | datetime.datetime = None,
    screencap: bool = False,
):
    if end_date is None:
        end_date = datetime.datetime.now()

    url = _update_url_date(url=url, end_date=end_date)
    _nav_driver(driver=driver, url=url)

    logger.info(f"Attemping to get {start_date}-{end_date} {data_frequency} from {url}")

    time.sleep(5)

    if data_term_options:
        _set_term(
            wait=wait,
            locale_type=locale_type,
            long_wait_time=long_wait_time,
            data_term_options=data_term_options,
            driver=driver,
            dl_dir_path=dl_dir_path,
            index_name=index_name,
        )
        time.sleep(1)

    if start_date:
        _set_date(
            date=start_date,
            date_type="start",
            driver=driver,
            long_wait_time=long_wait_time,
            wait=wait,
            locale_type=locale_type,
            dl_dir_path=dl_dir_path,
            index_name=index_name,
        )
        time.sleep(1)

    if end_date:
        _set_date(
            date=end_date,
            date_type="end",
            driver=driver,
            long_wait_time=long_wait_time,
            wait=wait,
            locale_type=locale_type,
            dl_dir_path=dl_dir_path,
            index_name=index_name,
        )
        time.sleep(1)

    if data_frequency:
        _set_frequency(
            driver=driver,
            data_frequency=data_frequency,
            wait=wait,
            long_wait_time=long_wait_time,
            locale_type=locale_type,
            dl_dir_path=dl_dir_path,
            index_name=index_name,
        )
        time.sleep(1)

    _click_update_btn(wait=wait, locale_type=locale_type)
    time.sleep(5)

    dl_start_time = _click_download_btn(
        wait=wait,
        locale_type=locale_type,
        screencap=screencap,
        driver=driver,
        dl_dir_path=dl_dir_path,
        index_name=index_name,
        long_wait_time=long_wait_time,
    )

    data_df = _process_download(
        wait=wait,
        locale_type=locale_type,
        dl_dir_path=dl_dir_path,
        dl_start_time=dl_start_time,
        long_wait_time=long_wait_time,
        index_name=index_name,
        idx_id=idx_id,
    )

    return data_df


def _prep_params(idx_name: str, idx_id: str, data_frequency: str, dir_path: Path):
    valid_freqs = ["Daily", "Monthly", "Yearly"]
    if data_frequency not in valid_freqs:
        raise ValueError(f"Duration must be one of {valid_freqs}.")

    # Contsants
    url = f"https://app2.msci.com/products/index-data-search/regional_chart.jsp?asOf=10/Jan/2024&size=Standard%20(Large%2BMid%20Cap)&scope=R&style=None&currency=USD&priceLevel=STRD&indexId={idx_id.replace(' ', '%20')}&indexName={idx_name.replace(' ', '%20')}&suite=K"
    url = _update_url_date(url=url, end_date=datetime.datetime.now())
    wait_time = 35
    data_term_options = [f"{n} Year" for n in (5, 4, 3)] if data_frequency == "Daily" else ["Full", "Full History"]

    # Setup driver
    driver = _get_driver(dl_dir_path=dir_path, long_wait_time=wait_time, idx_id=idx_id)
    _nav_driver(driver=driver, url=url)

    return url, wait_time, dir_path, data_term_options, driver


def _scrape_msci_data(  # noqa: C901 - Complex web scraping logic with multiple steps
    driver,
    url,
    dir_path,
    index_name,
    idx_id,
    wait_time,
    data_term_options,
    data_frequency,
    dl_dir_path,
    missing_business_days,
):
    try:
        wait = WebDriverWait(driver=driver, timeout=wait_time)
        locale_type = "Country" if driver.find_elements(By.ID, "updateTermCountry") else "Region"

        start_date = datetime.date(1999, 1, 1) if data_frequency == "Daily" else datetime.date(1800, 1, 1)

        params = {
            "driver": driver,
            "wait": wait,
            "locale_type": locale_type,
            "url": url,
            "dl_dir_path": dir_path,
            "index_name": index_name,
            "idx_id": idx_id,
            "long_wait_time": wait_time,
            "data_term_options": data_term_options,
            "data_frequency": data_frequency,
            "start_date": start_date,
            "end_date": datetime.datetime.now(),
        }

        data_dfs_list = []

        missing_start_date = min(missing_business_days) if missing_business_days else start_date
        chunk_end_dates = []
        if data_frequency != "Daily":
            chunk_end_dates.append(datetime.date.today())
        else:
            step = relativedelta(years=3)
            cur_chunk_end_dt = max(missing_business_days)
            while cur_chunk_end_dt >= missing_start_date:
                cur_chunk_start_dt = cur_chunk_end_dt - step
                missing_in_chunk = [dt for dt in missing_business_days if cur_chunk_start_dt <= dt <= cur_chunk_end_dt]
                if missing_in_chunk:
                    chunk_end_dates.append(cur_chunk_end_dt)
                # Update the chunk end date to the next missing business day before the current chunk start date
                cur_chunk_end_dt = max([dt for dt in missing_business_days if dt < cur_chunk_start_dt], default=None)
                if not cur_chunk_end_dt:
                    break

        for cur_end_dt in chunk_end_dates:
            params["end_date"] = cur_end_dt
            params["start_date"] = (
                None if data_frequency != "Daily" else max(params["end_date"] - relativedelta(years=3), start_date)
            )

            try:
                data_df = _download_msci_single(**params)
                data_dfs_list.append(data_df)
            except (TimeoutException, NoSuchElementException, WebDriverException, FileNotFoundError, OSError) as e:
                fail_str = f"Failed to get {params['start_date']}-{params['end_date']} {data_frequency} {index_name} msci data from {url}."
                # retry
                logger.warning(f"\n\n {fail_str} ({type(e).__name__}: {e}). Retrying now.")
                try:
                    data_df = _download_msci_single(**params)
                    data_dfs_list.append(data_df)
                except (
                    TimeoutException,
                    NoSuchElementException,
                    WebDriverException,
                    FileNotFoundError,
                    OSError,
                ) as err:
                    with open(dir_path / "failed.txt", "a") as f:
                        f.write(fail_str + f" Err: {err}\n")

        merged_df = pd.concat(data_dfs_list).drop_duplicates().dropna().sort_index()

        return merged_df

    except Exception as e:
        driver.save_screenshot(MSCI_DATA_DIR / "error_screenshot.png")
        logger.error(f"An error occurred: {e}")
        raise

    finally:
        # Remove the temporary directory and its contents
        tmp_dir = dl_dir_path / idx_id
        if os.path.exists(tmp_dir):
            for file_name in os.listdir(tmp_dir):
                os.remove(tmp_dir / file_name)
            os.rmdir(tmp_dir)
            logger.info(f"Removed temporary directory: {tmp_dir}")

        # Close the browser
        driver.quit()


def _filter_msci_data(
    df: pd.DataFrame,
    start_date: datetime.date | None,
    end_date: datetime.date | None,
) -> pd.DataFrame:
    if not isinstance(df.index, pd.DatetimeIndex):
        df = df.set_index(
            pd.DatetimeIndex(
                df["Date"] if "Date" in df.columns else df.index,
            ),
        )

    start_date = start_date or df.index.min()
    end_date = end_date or df.index.max()

    start_date = max(pd.Timestamp(start_date), df.index.min())
    end_date = min(pd.Timestamp(end_date), df.index.max())
    return df.loc[(df.index >= start_date) & (df.index <= end_date)]


def _validate_initial_params(idx_name, idx_id, data_frequency, start_date, end_date):
    # Validate and get the parameters needed to check the existing data
    if not idx_name or not idx_id:
        raise ValueError("idx_name and idx_id must be specified.")
    dir_path = MSCI_DATA_DIR
    processed_index_name = f"MSCI_{idx_name.replace(' ', '_').upper()}"
    file_name = f"{processed_index_name}_{data_frequency.lower()}.parquet"
    file_path = dir_path / file_name
    if start_date is not None and data_frequency == "Daily" and start_date < datetime.datetime(1999, 1, 1):
        logger.warning("Start date is before 1999-01-01. MSCI daily data is only available from 1999-01-01.")
    return dir_path, processed_index_name, file_name, file_path


def get_msci_single(
    idx_name: str,
    idx_id: str,
    data_frequency: str,
    start_date: datetime.date | None = None,
    end_date: datetime.date | None = None,
    check_update: bool = False,
    force_update: bool = False,
):
    logger.info(f"\n\nAttempting to get {data_frequency} data from msci for index {idx_name}\n")

    # Validate and get the parameters needed to check the existing data
    dir_path, processed_index_name, file_name, file_path = _validate_initial_params(
        idx_name=idx_name,
        idx_id=idx_id,
        data_frequency=data_frequency,
        start_date=start_date,
        end_date=end_date,
    )

    # Check if the index should be updated
    if force_update:
        is_outdated = True
    elif not check_update:
        is_outdated = not file_path.exists()
    else:
        is_outdated = is_file_outdated(
            file_path=file_path,
            analyze_pandas=True,
            align_to_period_start=False,
            file_not_found_error=False,
        )
    _update_status = "outdated" if is_outdated else "up to date" if check_update else "not being checked for updates"
    logger.info(f"Data for {idx_name} is {_update_status}.")

    if file_path.exists():
        missing_business_days = get_missing_us_business_dates(
            dates=pd.Series(load_dataframe(file_path=file_path).index),
            end_date=datetime.date.today(),
        )
    else:
        missing_business_days = get_us_business_dates(
            start_date=datetime.date(1999, 1, 1) if data_frequency == "Daily" else datetime.date(1800, 1, 1),
            end_date=datetime.date.today(),
        )
    # Hack to try to repair international holiday issues, only keep missing_business_days where the previous or next day is also missing
    # TODO: Implement better way to solve this
    missing_business_days = [
        dt
        for dt in missing_business_days
        if dt - relativedelta(days=1) in missing_business_days or dt + relativedelta(days=1) in missing_business_days
    ]
    logger.info(f"Missing business days: {missing_business_days}")

    # Load the data if it is up to date
    # if not is_outdated and not missing_business_days:
    if not missing_business_days:
        logger.info(f"Data for {idx_name} is up to date.")
        data_df = load_dataframe(file_path=file_path)
    else:
        # Validate and get the parameters needed to scrape the data
        url, wait_time, dir_path, data_term_options, driver = _prep_params(
            idx_name=idx_name,
            idx_id=idx_id,
            data_frequency=data_frequency,
            dir_path=dir_path,
        )

        # Get the data from msci
        data_df = _scrape_msci_data(
            driver=driver,
            url=url,
            dir_path=dir_path,
            index_name=processed_index_name,
            idx_id=idx_id,
            wait_time=wait_time,
            data_term_options=data_term_options,
            data_frequency=data_frequency,
            dl_dir_path=dir_path,
            missing_business_days=missing_business_days,
        )

        # If there is already partial data available, merge it with the new data
        if file_path.exists():
            existing_data = load_dataframe(file_path=file_path)
            data_df = pd.concat([existing_data, data_df]).drop_duplicates().dropna().sort_index()

        # Save the updated data
        save_dataframe(df=data_df, file_name=file_name, save_dir=dir_path)

    # Filter data
    filtered_df = _filter_msci_data(df=data_df, start_date=start_date, end_date=end_date)

    # Sort data and drop NaNs
    sorted_df = filtered_df.dropna().sort_index()

    return sorted_df


if __name__ == "__main__":
    from constants.tracked_collections.tracked_msci import TRACKED_MSCI

    for msci_idx in TRACKED_MSCI[33:]:
        data_df = get_msci_single(
            idx_name=msci_idx["name"],
            idx_id=msci_idx["id"],
            data_frequency="Daily",
        )
        print(data_df)
