import argparse
from datetime import datetime
from pathlib import Path

import pandas as pd

from matcher import (
    build_rename_plan,
    load_records,
)


def parse_arguments():

    parser = argparse.ArgumentParser(
        description=(
            "Match files against records stored in an Excel "
            "spreadsheet and safely rename them."
        )
    )

    parser.add_argument(
        "--data",
        required=True,
        help="Path to the Excel file containing the records.",
    )

    parser.add_argument(
        "--files",
        required=True,
        help="Directory containing the files to process.",
    )

    parser.add_argument(
        "--output",
        default="output",
        help="Directory where reports will be saved.",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Simulate the operation without renaming files."
        ),
    )

    return parser.parse_args()


def execute_plan(
    plan,
    dry_run,
):

    results = []

    for item in plan:

        status = item["status"]

        source = item["source"]
        destination = item["destination"]

        if status != "READY":

            results.append(
                create_result(
                    item,
                    status,
                )
            )

            continue

        if (
            source.resolve()
            ==
            destination.resolve()
        ):

            results.append(
                create_result(
                    item,
                    "ALREADY_RENAMED",
                )
            )

            continue

        if destination.exists():

            results.append(
                create_result(
                    item,
                    "DESTINATION_EXISTS",
                )
            )

            continue

        if dry_run:

            print(
                f"[DRY RUN] "
                f"{source.name} "
                f"-> "
                f"{destination.name}"
            )

            results.append(
                create_result(
                    item,
                    "SIMULATED",
                )
            )

            continue

        try:

            source.rename(
                destination
            )

            print(
                f"[RENAMED] "
                f"{source.name} "
                f"-> "
                f"{destination.name}"
            )

            results.append(
                create_result(
                    item,
                    "RENAMED",
                )
            )

        except Exception as error:

            results.append(
                create_result(
                    item,
                    "ERROR",
                    str(error),
                )
            )

    return results


def create_result(
    item,
    status,
    details="",
):

    return {
        "Group": item["group"],
        "CurrentFile": item["current_file"],
        "NewFile": item["new_file"],
        "ID": item["id"],
        "Status": status,
        "Details": details,
    }


def save_report(
    results,
    output_directory,
    dry_run,
):

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    operation = (
        "dry_run"
        if dry_run
        else
        "rename"
    )

    report_path = (
        output_directory
        / f"report_{operation}_{timestamp}.csv"
    )

    dataframe = pd.DataFrame(
        results
    )

    dataframe.to_csv(
        report_path,
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    return report_path


def print_summary(
    results,
    dry_run,
):

    dataframe = pd.DataFrame(
        results
    )

    print()
    print("=" * 70)

    if dry_run:
        print("DRY RUN SUMMARY")
    else:
        print("RENAME SUMMARY")

    print("=" * 70)

    print(
        f"Files analyzed : "
        f"{len(dataframe)}"
    )

    if not dataframe.empty:

        counts = (
            dataframe["Status"]
            .value_counts()
        )

        for status, count in counts.items():

            print(
                f"{status:<25}: "
                f"{count}"
            )

    print("=" * 70)


def main():

    args = parse_arguments()

    excel_path = Path(
        args.data
    ).resolve()

    files_directory = Path(
        args.files
    ).resolve()

    output_directory = Path(
        args.output
    ).resolve()

    if not excel_path.is_file():
        raise FileNotFoundError(
            f"Data file not found: {excel_path}"
        )

    if not files_directory.is_dir():
        raise NotADirectoryError(
            f"Files directory not found: "
            f"{files_directory}"
        )

    print("=" * 70)
    print("FILE RECORD MATCHER & RENAMER")
    print("=" * 70)

    print()
    print(
        f"Mode: "
        f"{'DRY RUN' if args.dry_run else 'RENAME'}"
    )

    print()
    print("Loading records...")

    dataframe, records_index = load_records(
        excel_path
    )

    print(
        f"Records loaded: "
        f"{len(dataframe)}"
    )

    print()
    print("Analyzing files...")

    plan = build_rename_plan(
        files_directory,
        records_index,
    )

    results = execute_plan(
        plan,
        args.dry_run,
    )

    report_path = save_report(
        results,
        output_directory,
        args.dry_run,
    )

    print_summary(
        results,
        args.dry_run,
    )

    print()
    print(
        f"Report saved to:"
    )

    print(
        report_path
    )


if __name__ == "__main__":
    main()