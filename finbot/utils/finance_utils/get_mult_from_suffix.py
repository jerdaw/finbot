"""Parse numeric suffixes (k, million, billion, etc.) to multipliers.

Converts human-readable number suffixes to their numeric equivalents. Supports
common abbreviations and full names, both singular and plural forms.

Supported suffixes:
    - k, thousand(s): 1,000
    - m, million(s): 1,000,000
    - b, billion(s): 1,000,000,000
    - t, trillion(s): 1,000,000,000,000
    - %, percent: 0.01
    - h, hundred(s): 100

Typical usage:
    - Parse user input with abbreviated numbers (e.g., "2.5M")
    - Normalize financial data from various sources
    - Handle human-friendly number formatting
"""


def _generate_suffix_map():
    base_values = {
        "hundred": 100,
        "thousand": 1_000,
        "million": 1_000_000,
        "billion": 1_000_000_000,
        "trillion": 1_000_000_000_000,
        "percent": 0.01,
    }
    suffix_map = {}

    for base, value in base_values.items():
        suffix_map[base] = value
        suffix_map[base + "s"] = value  # Adding plural forms

        # Handling special abbreviations
        if base == "thousand":
            suffix_map["k"] = value
        elif base == "trillion":
            suffix_map["t"] = value
        elif base == "percent":
            suffix_map["%"] = value  # Special case for percent
        else:
            suffix_map[base[0]] = value  # General abbreviation

    # Sorting by value size and then by key
    return dict(sorted(suffix_map.items(), key=lambda item: (item[1], item[0])))


def get_mult_from_suffix(suffix: str) -> int:
    """
    Returns the integer multiplier for a given suffix.

    Parameters:
    suffix (str): A suffix like 'million' or 'k'.

    Returns:
    int: The integer multiplier corresponding to the suffix.
    """
    suffix_map = _generate_suffix_map()
    return suffix_map.get(suffix.lower(), 1)


if __name__ == "__main__":
    sf = _generate_suffix_map()
    for key, value in sf.items():
        print(f"'{key}': {value:_}")
