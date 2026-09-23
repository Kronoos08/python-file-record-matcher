import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIRECTORY = PROJECT_ROOT / "src"

sys.path.insert(
    0,
    str(SRC_DIRECTORY),
)


from utils import (
    create_record_key,
    normalize_text,
    prepare_identifier,
    remove_accents,
    sanitize_filename,
)


def test_remove_accents():
    assert remove_accents("João") == "Joao"
    assert remove_accents("Álvares") == "Alvares"
    assert remove_accents("Coração") == "Coracao"


def test_normalize_text():
    assert normalize_text(
        "Pereira da Silva"
    ) == "PEREIRA DA SILVA"

    assert normalize_text(
        "PEREIRA-DA-SILVA"
    ) == "PEREIRA DA SILVA"

    assert normalize_text(
        "  João   da   Costa  "
    ) == "JOAO DA COSTA"


def test_create_record_key():
    key = create_record_key(
        "João",
        "Pereira da Silva",
    )

    assert key == (
        "JOAO|PEREIRA DA SILVA"
    )


def test_prepare_identifier_from_number():
    assert prepare_identifier(
        "1234"
    ) == "0001234"


def test_prepare_identifier_preserves_leading_zeros():
    assert prepare_identifier(
        "0001234"
    ) == "0001234"


def test_prepare_identifier_from_excel_number():
    assert prepare_identifier(
        "1234.0"
    ) == "0001234"


def test_sanitize_filename():
    result = sanitize_filename(
        'João: Pereira/da*Silva?'
    )

    assert result == (
        "João PereiradaSilva"
    )