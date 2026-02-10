from collections.abc import Callable

import numpy as np


def nan_helper(y: np.ndarray) -> tuple[np.ndarray, Callable]:
    """
    Helper function to identify NaNs in a NumPy array and provide a callable for indexing.

    This function returns the logical indices of NaNs in the input array and a callable that
    can be used to convert these logical indices into numerical indices.

    Parameters:
    y (np.ndarray): Input array.

    Returns:
    Tuple containing:
    - np.ndarray: Logical indices of NaNs in the input array.
    - callable: Function to convert logical indices of NaNs to numerical indices.

    Example:
    >>> y = np.array([np.nan, 1, np.nan, 3])
    >>> nans, index_func = nan_helper(y)
    >>> nans
    array([ True, False,  True, False])
    >>> index_func(nans)
    array([0, 2])
    """
    if y.size == 0:
        return y, lambda z: np.array([])

    return np.isnan(y), lambda z: z.nonzero()[0]


def np_linear_interpolation(arr: np.ndarray, inplace: bool = False) -> np.ndarray:
    """
    Interpolates NaN values in a NumPy array using linear interpolation.

    This function identifies NaN values in the array and replaces them with interpolated values
    based on non-NaN values. The interpolation is linear.

    Parameters:
    arr (np.ndarray): Input array containing NaN values to interpolate.
    inplace (bool): If True, performs interpolation in-place. Default is False.

    Returns:
    np.ndarray: Array with NaN values interpolated.

    Example:
    >>> arr = np.array([np.nan, 1, 2, np.nan, 4])
    >>> np_interpolate_array(arr)
    array([1., 1., 2., 3., 4.])
    """
    if not isinstance(arr, np.ndarray):
        raise TypeError("Input must be a NumPy array.")

    if arr.size == 0:
        return arr

    if not inplace:
        arr = arr.copy()

    nans, x = nan_helper(arr)
    arr[nans] = np.interp(x(nans), x(~nans), arr[~nans])
    return arr


if __name__ == "__main__":
    from numpy import NaN

    orig = np.array([NaN, 1, 1, NaN, NaN, 2, 2, NaN, 0])
    print(np_linear_interpolation(orig))
    print(orig)
    np_linear_interpolation(orig, inplace=True)
    print(orig)
