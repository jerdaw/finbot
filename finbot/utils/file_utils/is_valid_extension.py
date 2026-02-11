"""Validate file extensions against an allowed set.

Simple utility for checking if a file's extension is in a set of allowed
extensions. Case-insensitive matching ensures consistent validation regardless
of extension casing.

Typical usage:
    ```python
    from finbot.utils.file_utils.is_valid_extension import is_valid_extension

    # Check if image file
    if is_valid_extension("photo.jpg", {".jpg", ".jpeg", ".png", ".gif"}):
        process_image("photo.jpg")

    # Check if data file
    DATA_EXTENSIONS = {".csv", ".parquet", ".json", ".xlsx"}
    if is_valid_extension("data.csv", DATA_EXTENSIONS):
        load_data("data.csv")

    # Filter valid files
    files = ["data.csv", "image.png", "doc.pdf", "data.parquet"]
    valid_exts = {".csv", ".parquet"}
    data_files = [f for f in files if is_valid_extension(f, valid_exts)]
    # Result: ["data.csv", "data.parquet"]
    ```

Features:
    - Case-insensitive matching (.CSV == .csv)
    - Works with Path or str inputs
    - Fast set membership test (O(1))
    - No side effects (pure function)

Extension format:
    - Include the dot: `.csv` not `csv`
    - Lowercase recommended (function converts to lowercase)
    - Examples: `.txt`, `.json`, `.parquet`, `.csv`, `.xlsx`

Use cases:
    - File upload validation
    - Batch processing file filtering
    - Input validation for data pipelines
    - Type-specific file handlers
    - Security: preventing dangerous file types

Common extension sets:
    ```python
    # Data files
    DATA_EXTS = {".csv", ".parquet", ".json", ".xlsx", ".tsv"}

    # Image files
    IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"}

    # Document files
    DOC_EXTS = {".pdf", ".doc", ".docx", ".txt", ".md"}

    # Archive files
    ARCHIVE_EXTS = {".zip", ".tar", ".gz", ".zst", ".7z"}

    # Python files
    PY_EXTS = {".py", ".pyi", ".ipynb"}
    ```

Example with error handling:
    ```python
    def process_data_file(path):
        valid_exts = {".csv", ".parquet", ".json"}
        if not is_valid_extension(path, valid_exts):
            raise ValueError(f"Invalid file type. Expected {valid_exts}, got {Path(path).suffix}")
        # Process file...
    ```

Security considerations:
    - Use for whitelisting allowed file types
    - Combine with content validation (extension doesn't guarantee content)
    - Don't rely solely on extension for security-critical operations
    - Consider is_binary() for binary/text detection

Limitations:
    - Only checks extension, not file content
    - Doesn't validate file actually matches extension (JPEG named .png)
    - No MIME type detection
    - Simple string matching (no pattern support)

Related modules: is_binary (content-based detection), get_matching_files
(file discovery with patterns), load_text/save_text (extension-aware I/O).
"""

from __future__ import annotations

from pathlib import Path


def is_valid_extension(file_path: Path | str, valid_extensions: set) -> bool:
    """
    Check if a file's extension is in the allowed set.

    Args:
        file_path: The path of the file to check.
        valid_extensions: A set of allowed file extensions.

    Returns:
        True if the file's extension is in the set, False otherwise.
    """
    return Path(file_path).suffix.lower() in valid_extensions
