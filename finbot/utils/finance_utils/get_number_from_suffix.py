from finbot.utils.finance_utils.get_mult_from_suffix import get_mult_from_suffix


def get_number_from_suffix(num_str: str, require_suffix: bool = False):
    """
    Converts a string representation of a number with an optional suffix into a numerical value.

    Args:
        num_str (str): The string representation of the number.
        require_suffix (bool, optional): Whether a suffix is required. Defaults to False.

    Returns:
        int or float: The converted numerical value.

    Raises:
        ValueError: If the input is invalid or if a required suffix is not found.
    """
    try:
        normalized_str = num_str.lower().replace(" ", "")
        has_suffix = False

        for i in range(len(normalized_str)):
            if normalized_str[i:].isalpha() or normalized_str[i] == "%":
                number_part = normalized_str[:i]
                suffix = normalized_str[i:]
                multiplier = get_mult_from_suffix(suffix)
                result = float(number_part) * multiplier
                has_suffix = True
                break

        if not has_suffix:
            result = float(normalized_str)
            if require_suffix:
                raise ValueError(f"No valid suffix found in input '{num_str}'")

        return int(result) if result.is_integer() else result
    except ValueError as e:
        raise ValueError(f"Invalid input '{num_str}': {e}") from e


# Test the function
if __name__ == "__main__":
    test_inputs = [
        "2.5",
        "2500",
        "2.5k",
        "7 Million",
        "1b",
        "4.2 Trillion",
        "100",
        "300 hundreds",
        "50 millions",
        "100%",
        "2.5 percent",
        "0.0009 %",
        "100x",
    ]
    for input_str in test_inputs:
        try:
            result = get_number_from_suffix(input_str)
            print(f"{input_str} -> {result} (Type: {type(result).__name__})")
        except ValueError as e:
            print(e)
