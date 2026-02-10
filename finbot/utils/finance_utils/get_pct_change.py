def get_pct_change(
    start_val: float,
    end_val: float,
    mult_by_100: bool = False,
    allow_negative: bool = True,
    div_by_zero_error: bool = True,
) -> float:
    """
    Calculate the percentage change between two values.

    Args:
    start_val (float): The initial value.
    end_val (float): The final value.
    mult_by_100 (bool): If True, the result is multiplied by 100.
    allow_negative (bool): If False, the result is the absolute value of the percentage change.
    div_by_zero_error (bool): If False, returns float("inf") in case of division by zero, otherwise raises an error.

    Returns:
    float: The percentage change between the start and end values.
    """
    try:
        pct_change = (end_val - start_val) / start_val
        if not allow_negative:
            pct_change = abs(pct_change)
        if mult_by_100:
            pct_change *= 100
    except ZeroDivisionError as err:
        if not div_by_zero_error:
            return float("inf")
        else:
            raise ZeroDivisionError(
                f"Division by zero error: start_val cannot be zero. start_val={start_val}, end_val={end_val}",
            ) from err
    return pct_change


if __name__ == "__main__":
    print(get_pct_change(1, 2))
    print(get_pct_change(0, 2, div_by_zero_error=False))
    # print(get_pct_change(0, 2, div_by_zero_error=True))
