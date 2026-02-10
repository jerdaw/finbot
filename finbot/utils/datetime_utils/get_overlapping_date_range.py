def get_overlapping_date_range(*series, raise_error: bool = True):
    """
    Find the overlapping date range among a list of pandas Series.
    This is the range where all series have data.
    :param series: A variable number of pandas Series.
    :param raise_error: If True, raise an error if no overlapping range exists.
    :return: A tuple containing the start and end dates of the overlapping range.
    """
    start_date = max(serie.index.min() for serie in series)
    end_date = min(serie.index.max() for serie in series)

    if raise_error and start_date > end_date:
        raise ValueError("No overlapping date range exists among the provided series.")

    return start_date, end_date
