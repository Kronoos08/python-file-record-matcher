import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIRECTORY = PROJECT_ROOT / "src"

sys.path.insert(
    0,
    str(SRC_DIRECTORY),
)


from matcher import (
    build_rename_plan,
    load_records,
    parse_current_filename,
    parse_renamed_filename,
)


def create_excel(tmp_path, records):
    """Create a temporary Excel file."""

    excel_path = tmp_path / "records.xlsx"

    dataframe = pd.DataFrame(records)

    dataframe.to_excel(
        excel_path,
        index=False,
    )

    return excel_path


def create_group(tmp_path, group_name="GROUP_A"):
    """Create a temporary files/group structure."""

    files_directory = tmp_path / "files"

    group_directory = (
        files_directory
        / group_name
    )

    group_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    return files_directory, group_directory


def create_test_file(
    group_directory,
    filename,
):
    """Create a real temporary file for testing."""

    file_path = (
        group_directory
        / filename
    )

    file_path.write_bytes(b"")

    assert file_path.exists()
    assert file_path.is_file()

    return file_path


def create_plan(
    tmp_path,
    records,
    filenames,
):
    """
    Create records, temporary files and return
    the generated rename plan.
    """

    excel_path = create_excel(
        tmp_path,
        records,
    )

    files_directory, group_directory = (
        create_group(tmp_path)
    )

    for filename in filenames:
        create_test_file(
            group_directory,
            filename,
        )

    _, records_index = load_records(
        excel_path
    )

    return build_rename_plan(
        files_directory,
        records_index,
    )


def test_parse_current_filename():

    first_name, last_name = (
        parse_current_filename(
            "GROUP_A",
            "GROUP_A_PEREIRA DA SILVA_Alexandre.jpg",
        )
    )

    assert first_name == "Alexandre"
    assert last_name == "PEREIRA DA SILVA"


def test_parse_invalid_current_filename():

    first_name, last_name = (
        parse_current_filename(
            "GROUP_A",
            "invalid_file.jpg",
        )
    )

    assert first_name is None
    assert last_name is None


def test_parse_renamed_filename():

    first_name, last_name, identifier = (
        parse_renamed_filename(
            "Alexandre+PEREIRA DA SILVA_0001001.jpg"
        )
    )

    assert first_name == "Alexandre"
    assert last_name == "PEREIRA DA SILVA"
    assert identifier == "0001001"


def test_valid_record_is_ready(tmp_path):

    plan = create_plan(
        tmp_path,
        [
            {
                "FirstName": "Alexandre",
                "LastName": "Pereira da Silva",
                "ID": "0001001",
            }
        ],
        [
            "GROUP_A_PEREIRA DA SILVA_Alexandre.jpg"
        ],
    )

    assert len(plan) == 1

    assert plan[0]["status"] == "READY"

    assert plan[0]["new_file"] == (
        "Alexandre+PEREIRA DA SILVA_0001001.jpg"
    )


def test_record_not_found(tmp_path):

    plan = create_plan(
        tmp_path,
        [
            {
                "FirstName": "Alexandre",
                "LastName": "Pereira da Silva",
                "ID": "0001001",
            }
        ],
        [
            "GROUP_A_SILVA_Pedro.jpg"
        ],
    )

    assert len(plan) == 1

    assert plan[0]["status"] == (
        "RECORD_NOT_FOUND"
    )


def test_invalid_format(tmp_path):

    plan = create_plan(
        tmp_path,
        [
            {
                "FirstName": "Alexandre",
                "LastName": "Pereira da Silva",
                "ID": "0001001",
            }
        ],
        [
            "invalid_file.jpg"
        ],
    )

    assert len(plan) == 1

    assert plan[0]["status"] == (
        "INVALID_FORMAT"
    )


def test_ambiguous_record(tmp_path):

    plan = create_plan(
        tmp_path,
        [
            {
                "FirstName": "Daniel",
                "LastName": "Oliveira Santos",
                "ID": "0001009",
            },
            {
                "FirstName": "Daniel",
                "LastName": "Oliveira Santos",
                "ID": "0001010",
            },
        ],
        [
            "GROUP_A_OLIVEIRA SANTOS_Daniel.jpg"
        ],
    )

    assert len(plan) == 1

    assert plan[0]["status"] == (
        "AMBIGUOUS_RECORD"
    )


def test_duplicate_destination(tmp_path):

    plan = create_plan(
        tmp_path,
        [
            {
                "FirstName": "Mariana",
                "LastName": "Costa Oliveira",
                "ID": "0001002",
            }
        ],
        [
            "GROUP_A_COSTA OLIVEIRA_Mariana.jpg",
            "GROUP_A_COSTA-OLIVEIRA_Mariana.jpg",
        ],
    )

    assert len(plan) == 2

    statuses = [
        item["status"]
        for item in plan
    ]

    assert statuses.count(
        "DUPLICATE_DESTINATION"
    ) == 2


def test_already_renamed(tmp_path):

    plan = create_plan(
        tmp_path,
        [
            {
                "FirstName": "Alexandre",
                "LastName": "Pereira da Silva",
                "ID": "0001001",
            }
        ],
        [
            "Alexandre+PEREIRA DA SILVA_0001001.jpg"
        ],
    )

    assert len(plan) == 1

    assert plan[0]["status"] == (
        "ALREADY_RENAMED"
    )