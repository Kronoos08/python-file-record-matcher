import re
import unicodedata
from pathlib import Path


IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
}


def remove_accents(text: str) -> str:
    """Remove accents from text for comparison purposes."""

    text = str(text)

    normalized = unicodedata.normalize("NFD", text)

    return "".join(
        char
        for char in normalized
        if unicodedata.category(char) != "Mn"
    )


def normalize_text(text: str) -> str:
    """
    Normalize text for matching.

    - Removes accents
    - Converts to uppercase
    - Replaces special characters with spaces
    - Removes duplicate whitespace
    """

    text = remove_accents(str(text).strip())

    text = text.upper()

    text = re.sub(
        r"[^A-Z0-9]+",
        " ",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


def create_record_key(
    first_name: str,
    last_name: str,
) -> str:
    """Create the normalized key used to match records."""

    return (
        f"{normalize_text(first_name)}"
        f"|"
        f"{normalize_text(last_name)}"
    )


def prepare_identifier(
    value,
    minimum_length: int = 7,
) -> str:
    """
    Normalize an identifier read from Excel.

    Numeric identifiers are padded with leading zeros.
    """

    value = str(value).strip()

    if value.endswith(".0"):
        value = value[:-2]

    if value.isdigit():
        value = value.zfill(minimum_length)

    return value


def sanitize_filename(text: str) -> str:
    """
    Remove characters that are invalid in Windows filenames.
    """

    text = str(text).strip()

    text = re.sub(
        r'[<>:"/\\|?*]',
        "",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


def is_supported_image(path: Path) -> bool:
    """Return True when the file has a supported image extension."""

    return (
        path.is_file()
        and path.suffix.lower() in IMAGE_EXTENSIONS
    )