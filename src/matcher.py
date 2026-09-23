from pathlib import Path

import pandas as pd

from utils import (
    create_record_key,
    is_supported_image,
    prepare_identifier,
    sanitize_filename,
)


def load_records(excel_path: Path):
    """
    Load records from Excel and create a normalized lookup index.

    Required columns:
        FirstName
        LastName
        ID
    """

    dataframe = pd.read_excel(
        excel_path,
        dtype=str,
    ).fillna("")

    required_columns = {
        "FirstName",
        "LastName",
        "ID",
    }

    missing_columns = (
        required_columns
        - set(dataframe.columns)
    )

    if missing_columns:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(sorted(missing_columns))
        )

    index = {}

    for _, row in dataframe.iterrows():

        first_name = str(
            row["FirstName"]
        ).strip()

        last_name = str(
            row["LastName"]
        ).strip()

        identifier = prepare_identifier(
            row["ID"]
        )

        if not first_name or not last_name or not identifier:
            continue

        key = create_record_key(
            first_name,
            last_name,
        )

        index.setdefault(
            key,
            [],
        ).append(
            {
                "first_name": first_name,
                "last_name": last_name,
                "id": identifier,
            }
        )

    return dataframe, index


def parse_current_filename(
    group_name: str,
    filename: str,
):
    """
    Parse files using the following pattern:

        GROUP_LASTNAME_FirstName.ext

    Example:

        GROUP_A_SMITH_John.jpg
    """

    base_name = Path(filename).stem

    prefix = f"{group_name}_"

    if not base_name.lower().startswith(
        prefix.lower()
    ):
        return None, None

    remaining = base_name[
        len(prefix):
    ]

    if "_" not in remaining:
        return None, None

    last_name, first_name = remaining.rsplit(
        "_",
        1,
    )

    last_name = last_name.strip()
    first_name = first_name.strip()

    if not first_name or not last_name:
        return None, None

    return first_name, last_name
def parse_renamed_filename(filename: str):
    """
    Parse files that already use the final naming pattern:

        FirstName+LASTNAME_ID.ext

    Example:

        Alexandre+PEREIRA DA SILVA_0001001.jpg

    Returns:
        first_name, last_name, identifier

    Returns None values when the filename does not match
    the expected final format.
    """

    base_name = Path(filename).stem

    if "+" not in base_name:
        return None, None, None

    first_name, remaining = base_name.split(
        "+",
        1,
    )

    if "_" not in remaining:
        return None, None, None

    last_name, identifier = remaining.rsplit(
        "_",
        1,
    )

    first_name = first_name.strip()
    last_name = last_name.strip()
    identifier = identifier.strip()

    if (
        not first_name
        or not last_name
        or not identifier
    ):
        return None, None, None

    return (
        first_name,
        last_name,
        identifier,
    )
def build_rename_plan(
    files_directory: Path,
    records_index: dict,
):
    """
    Analyze all files and create a rename plan.

    No files are modified in this step.
    """

    plan = []

    groups = sorted(
        directory
        for directory in files_directory.iterdir()
        if directory.is_dir()
    )

    for group_directory in groups:

        group_name = group_directory.name

        for file_path in group_directory.iterdir():

            if not is_supported_image(file_path):
                continue

            # ---------------------------------------------------------
            # 1. Check whether the file already uses the final format
            # ---------------------------------------------------------

            (
                renamed_first_name,
                renamed_last_name,
                renamed_identifier,
            ) = parse_renamed_filename(
                file_path.name
            )

            if renamed_first_name is not None:

                key = create_record_key(
                    renamed_first_name,
                    renamed_last_name,
                )

                candidates = records_index.get(
                    key,
                    [],
                )

                matching_records = [
                    record
                    for record in candidates
                    if record["id"] == renamed_identifier
                ]

                if len(matching_records) == 1:

                    plan.append(
                        {
                            "group": group_name,
                            "current_file": file_path.name,
                            "new_file": file_path.name,
                            "id": renamed_identifier,
                            "status": "ALREADY_RENAMED",
                            "source": file_path,
                            "destination": file_path,
                        }
                    )

                    continue

            # ---------------------------------------------------------
            # 2. Try the original filename format
            # ---------------------------------------------------------

            first_name, last_name = (
                parse_current_filename(
                    group_name,
                    file_path.name,
                )
            )

            # ---------------------------------------------------------
            # 3. Invalid original filename
            # ---------------------------------------------------------

            if first_name is None:

                plan.append(
                    {
                        "group": group_name,
                        "current_file": file_path.name,
                        "new_file": "",
                        "id": "",
                        "status": "INVALID_FORMAT",
                        "source": file_path,
                        "destination": None,
                    }
                )

                continue

            # ---------------------------------------------------------
            # 4. Find the corresponding record
            # ---------------------------------------------------------

            key = create_record_key(
                first_name,
                last_name,
            )

            candidates = records_index.get(
                key,
                [],
            )

            # ---------------------------------------------------------
            # 5. No matching record
            # ---------------------------------------------------------

            if len(candidates) == 0:

                plan.append(
                    {
                        "group": group_name,
                        "current_file": file_path.name,
                        "new_file": "",
                        "id": "",
                        "status": "RECORD_NOT_FOUND",
                        "source": file_path,
                        "destination": None,
                    }
                )

                continue

            # ---------------------------------------------------------
            # 6. More than one matching record
            # ---------------------------------------------------------

            if len(candidates) > 1:

                plan.append(
                    {
                        "group": group_name,
                        "current_file": file_path.name,
                        "new_file": "",
                        "id": "",
                        "status": "AMBIGUOUS_RECORD",
                        "source": file_path,
                        "destination": None,
                    }
                )

                continue

            # ---------------------------------------------------------
            # 7. Exactly one matching record
            # ---------------------------------------------------------

            record = candidates[0]

            official_first_name = sanitize_filename(
                record["first_name"]
            )

            official_last_name = sanitize_filename(
                record["last_name"]
            ).upper()

            identifier = record["id"]

            new_filename = (
                f"{official_first_name}"
                f"+"
                f"{official_last_name}"
                f"_"
                f"{identifier}"
                f"{file_path.suffix.lower()}"
            )

            destination = (
                group_directory
                / new_filename
            )

            plan.append(
                {
                    "group": group_name,
                    "current_file": file_path.name,
                    "new_file": new_filename,
                    "id": identifier,
                    "status": "READY",
                    "source": file_path,
                    "destination": destination,
                }
            )

    # -------------------------------------------------------------
    # 8. Detect collisions before any rename operation
    # -------------------------------------------------------------

    detect_duplicate_destinations(
        plan
    )

    return plan
def detect_duplicate_destinations(
    plan: list,
):
    """
    Detect when multiple source files would generate
    the same destination filename.
    """

    destination_count = {}

    for item in plan:

        if item["status"] != "READY":
            continue

        destination = str(
            item["destination"].resolve()
        ).lower()

        destination_count[destination] = (
            destination_count.get(
                destination,
                0,
            )
            + 1
        )

    for item in plan:

        if item["status"] != "READY":
            continue

        destination = str(
            item["destination"].resolve()
        ).lower()

        if destination_count[destination] > 1:
            item["status"] = "DUPLICATE_DESTINATION"