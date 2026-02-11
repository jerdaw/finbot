import datetime

from dateutil.relativedelta import relativedelta


def get_duration(
    start_datetime: datetime.datetime,
    end_datetime: datetime.datetime,
    granularity: None | str = None,
) -> relativedelta | float:
    rd = relativedelta(end_datetime, start_datetime)

    if granularity is None:
        return rd

    # For years, months, and days, use relativedelta's properties
    if granularity in ["years", "months", "days"]:
        if granularity == "years":
            return rd.years + rd.months / 12 + rd.days / 365.25
        elif granularity == "months":
            total_months = rd.years * 12 + rd.months + rd.days / 30.44
            return total_months
        elif granularity == "days":
            total_seconds = (end_datetime - start_datetime).total_seconds()
            return total_seconds / (24 * 60 * 60)  # Convert seconds to days, including fractional part

    # Calculate total seconds for smaller units
    total_seconds = (end_datetime - start_datetime).total_seconds()
    units_in_seconds = {
        "hours": 60 * 60,
        "minutes": 60,
        "seconds": 1,
        "microseconds": 1e-6,
    }

    if granularity not in units_in_seconds:
        raise ValueError(
            f"Invalid granularity '{granularity}'. Valid granularity values are {['years', 'months', 'days', *list(units_in_seconds.keys())]}",
        )

    return total_seconds / units_in_seconds.get(granularity, 1)


# Test the function
if __name__ == "__main__":
    d1 = datetime.datetime(year=1000, month=1, day=1)
    d2 = datetime.datetime(year=2000, month=7, day=1, hour=12, minute=30, second=30, microsecond=50000)
    for unit in [None, "years", "months", "days", "hours", "minutes", "seconds", "microseconds"]:
        print(f"Total {unit}: {get_duration(d1, d2, granularity=unit)}")
