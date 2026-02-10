def get_common_date_range(*series, raise_error: bool = True):
    """
    Find the actual common date range among a list of pandas Series.
    This is the range where all series share the exact same dates.
    :param series: A variable number of pandas Series.
    :param raise_error: If True, raise an error if no common range exists.
    :return: A tuple containing the start and end dates of the common range, or None if no common range exists.
    """
    # Intersect the index of all series to find common dates
    common_dates = series[0].index
    for serie in series[1:]:
        common_dates = common_dates.intersection(serie.index)

    if len(common_dates) > 0:
        return common_dates.min(), common_dates.max()
    elif raise_error:
        raise ValueError("No common date range exists among the provided series.")
    else:
        return None, None
