def is_binary(file_data: bytes) -> bool:
    """
    Check if a given byte string represents binary data.

    Args:
        file_data: Byte string to check.

    Returns:
        True if the data is binary, False otherwise.
    """
    text_characters = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x7F + 1)))
    return bool(file_data.translate(None, text_characters))
