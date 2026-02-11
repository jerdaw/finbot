"""Detect whether file data represents binary or text content.

Analyzes byte sequences to determine if a file contains binary (non-text) data
by checking for the presence of non-printable characters outside the standard
ASCII text character set.

Typical usage:
    ```python
    with open("file.dat", "rb") as f:
        data = f.read()
        if is_binary(data):
            print("Binary file detected")
    ```

Algorithm:
    Uses a character set of common text characters (ASCII 0x20-0x7F plus
    control characters like tab, newline, carriage return). Any bytes outside
    this set indicate binary content.

Text character set includes:
    - Printable ASCII (0x20-0x7F): letters, numbers, symbols, space
    - Control characters: BEL (7), BS (8), TAB (9), LF (10), FF (12), CR (13), ESC (27)

Use cases:
    - File type detection before processing
    - Preventing binary data from being treated as text
    - Content-aware file handling
    - Validation before text operations (regex, string manipulation)

Advantages:
    - Fast byte-level analysis
    - No file I/O (operates on bytes in memory)
    - Works with any byte sequence
    - Lightweight (no dependencies)

Limitations:
    - Simple heuristic (not foolproof)
    - May misclassify some text encodings (UTF-16, UTF-32)
    - Does not identify specific binary formats
    - False positives possible with non-ASCII text

Related modules: finbot.utils.file_utils.is_valid_extension (extension-based
validation), finbot.utils.file_utils.load_text (text file loading).
"""


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
