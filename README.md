
# Python File Record Matcher & Renamer

A Python command-line tool that matches files against structured records stored in an Excel spreadsheet and safely renames them using standardized identifiers.

This project was inspired by a real-world administrative automation problem involving hundreds of files that needed to be matched with official records and renamed consistently.

The public version of the project uses **synthetic data only**. No personal, student, employee, or organizational data from the original environment is included.

## Overview

Manually matching and renaming hundreds of files can be slow and error-prone, especially when filenames and official records use slightly different formatting.

This tool automates that workflow by:

1. Reading official records from an Excel spreadsheet.
2. Scanning files organized into group directories.
3. Parsing information from the current filenames.
4. Normalizing names for reliable comparison.
5. Matching each file against the corresponding spreadsheet record.
6. Detecting missing, ambiguous, or conflicting matches.
7. Generating standardized filenames.
8. Optionally simulating the operation before modifying any files.
9. Producing a CSV report for auditing.

## Real-World Background

The original automation was developed to solve a real operational problem involving several hundred files.

In the production workflow:

* **463 files** were processed.
* A final validation audit checked all renamed files.
* **463 out of 463 files passed the final audit.**
* No missing identifiers, duplicate identifiers, invalid filename formats, or name mismatches remained after the final validation.

The implementation in this repository has been refactored into a generic portfolio project and uses synthetic sample records.

## Features

* Excel-based record matching
* Batch file processing
* Unicode and accent normalization
* Case-insensitive matching
* Identifier formatting and preservation
* Windows-safe filename sanitization
* Dry-run mode
* CSV audit reports
* Missing-record detection
* Ambiguous-record detection
* Duplicate-destination detection
* Existing-destination protection
* Already-renamed file detection
* Idempotent processing for successfully renamed files
* Automated tests with `pytest`

## Technologies

* Python 3
* pandas
* openpyxl
* pathlib
* argparse
* pytest

## Project Structure

```text
python-file-record-matcher/
├── src/
│   ├── main.py
│   ├── matcher.py
│   └── utils.py
│
├── tests/
│   ├── test_matcher.py
│   └── test_utils.py
│
├── sample_data/
│   ├── records.xlsx
│   └── files/
│       ├── GROUP_A/
│       └── GROUP_B/
│
├── output/
├── .gitignore
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

## Input Data

The Excel spreadsheet must contain the following columns:

| Column        | Description              |
| ------------- | ------------------------ |
| `FirstName` | Official first name      |
| `LastName`  | Official last name       |
| `ID`        | Unique record identifier |

Example:

| FirstName | LastName         | ID      |
| --------- | ---------------- | ------- |
| Alexandre | Pereira da Silva | 0001001 |
| Mariana   | Costa Oliveira   | 0001002 |
| Gabriel   | Santos Ferreira  | 0001003 |

All records included in this repository are synthetic.

## Expected Source Filename

Files are organized inside group directories.

Example:

```text
sample_data/
└── files/
    ├── GROUP_A/
    │   ├── GROUP_A_PEREIRA DA SILVA_Alexandre.jpg
    │   └── GROUP_A_COSTA OLIVEIRA_Mariana.jpg
    │
    └── GROUP_B/
        └── GROUP_B_MARTINS SOUZA_Lucas.jpg
```

The expected source pattern is:

```text
GROUP_LASTNAME_FirstName.ext
```

## Generated Filename

When a unique record is found, the program generates:

```text
FirstName+LASTNAME_ID.ext
```

Example:

```text
GROUP_A_PEREIRA DA SILVA_Alexandre.jpg
```

becomes:

```text
Alexandre+PEREIRA DA SILVA_0001001.jpg
```

The official name and identifier are taken from the spreadsheet rather than blindly copied from the source filename.

## Installation

Clone the repository and enter the project directory:

```bash
git clone https://github.com/Kronoos08/python-file-record-matcher.git
cd python-file-record-matcher
```

Create a virtual environment:

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the runtime dependencies:

```powershell
pip install -r requirements.txt
```

For development and testing:

```powershell
pip install -r requirements-dev.txt
```

## Usage

### Dry Run

A dry run analyzes the files and generates a report without renaming anything:

```powershell
python src/main.py --data sample_data/records.xlsx --files sample_data/files --dry-run
```

Example:

```text
======================================================================
FILE RECORD MATCHER & RENAMER
======================================================================

Mode: DRY RUN

Loading records...
Records loaded: 8

Analyzing files...

======================================================================
DRY RUN SUMMARY
======================================================================
Files analyzed : 8
SIMULATED                : 8
======================================================================
```

Dry-run mode is recommended before performing a real batch rename.

### Rename Files

After reviewing the dry-run result:

```powershell
python src/main.py --data sample_data/records.xlsx --files sample_data/files
```

Example:

```text
[RENAMED] GROUP_A_PEREIRA DA SILVA_Alexandre.jpg -> Alexandre+PEREIRA DA SILVA_0001001.jpg
```

The operation also generates a CSV report inside the configured output directory.

## Safety Checks

The application builds the complete rename plan before modifying files.

Several conditions are checked during analysis:

| Status                    | Meaning                                                  |
| ------------------------- | -------------------------------------------------------- |
| `READY`                 | File has a unique matching record and can be renamed     |
| `SIMULATED`             | Rename was successfully simulated                        |
| `RENAMED`               | File was successfully renamed                            |
| `ALREADY_RENAMED`       | File already matches its validated final record          |
| `INVALID_FORMAT`        | Source filename does not follow the expected structure   |
| `RECORD_NOT_FOUND`      | No matching spreadsheet record was found                 |
| `AMBIGUOUS_RECORD`      | Multiple spreadsheet records match the same file         |
| `DUPLICATE_DESTINATION` | Multiple source files would produce the same destination |
| `DESTINATION_EXISTS`    | The target filename already exists                       |
| `ERROR`                 | An unexpected error occurred during the rename operation |

This prevents potentially destructive rename operations from being performed silently.

## Name Normalization

Matching is performed using normalized values.

For example, differences involving:

* uppercase/lowercase characters,
* accents,
* repeated spaces,
* punctuation,

can be normalized before comparison.

Examples:

```text
João
JOAO
joão
```

normalize to the same comparison value:

```text
JOAO
```

Similarly:

```text
COSTA-OLIVEIRA
```

and:

```text
Costa Oliveira
```

produce compatible normalized values for matching.

The final filename still uses the official record stored in the spreadsheet.

## Idempotency

The application recognizes files that have already been successfully renamed.

For example, after:

```text
GROUP_A_PEREIRA DA SILVA_Alexandre.jpg
```

has become:

```text
Alexandre+PEREIRA DA SILVA_0001001.jpg
```

a later execution validates the name and identifier against the spreadsheet and returns:

```text
ALREADY_RENAMED
```

instead of renaming the file again.

This allows the tool to be safely rerun as part of repeatable workflows.

## Reports

Each execution creates a timestamped CSV report.

Example:

```text
report_dry_run_YYYYMMDD_HHMMSS.csv
```

or:

```text
report_rename_YYYYMMDD_HHMMSS.csv
```

The report contains information such as:

* group,
* original filename,
* proposed/final filename,
* identifier,
* status,
* error details when applicable.

Reports use semicolon-separated values and UTF-8 encoding with BOM for compatibility with spreadsheet applications.

## Automated Tests

The project includes automated tests covering the core matching and filename-processing logic.

Run:

```powershell
pytest -v
```

Current test suite:

```text
16 passed
```

The tests cover scenarios including:

* accent removal,
* text normalization,
* identifier formatting,
* filename sanitization,
* source filename parsing,
* final filename parsing,
* successful record matching,
* missing records,
* invalid filename formats,
* ambiguous records,
* duplicate destinations,
* already-renamed files.

The test suite also helped identify a regression introduced while adding already-renamed file detection, demonstrating the value of automated regression testing during development.

## Design Decisions

### Dry-run first

Batch filesystem operations can be destructive. The application therefore provides a simulation mode so the complete operation can be reviewed before files are modified.

### Separate planning from execution

The matching and planning phase does not modify files. Renaming happens only after the plan has been constructed and validated.

### Use official records as the source of truth

Source filenames are used to locate a record, but the final filename is generated from the official spreadsheet data.

### Detect ambiguity instead of guessing

If multiple records match the same normalized identity, the application reports the ambiguity rather than choosing one automatically.

### Detect collisions before renaming

Destination paths are analyzed before execution so multiple files cannot silently overwrite one another.

### Make repeated execution safe

Already-processed files are validated against their official record and classified as `ALREADY_RENAMED`.

## Privacy

This repository does **not** contain the original production dataset.

Names, identifiers, directories, sample files, and spreadsheet records included in the repository are synthetic and exist only to demonstrate the application.

The project was intentionally refactored before publication to separate the reusable engineering solution from the private data involved in the original workflow.

## What This Project Demonstrates

This project demonstrates practical experience with:

* Python application development
* File-system automation
* Excel data processing
* Data normalization
* Record matching
* Defensive programming
* Batch-operation safety
* CLI design
* Audit/report generation
* Automated testing
* Regression testing
* Refactoring a production-oriented script into a reusable application
* Privacy-conscious software publication

## Possible Future Improvements

Potential future improvements include:

* configurable filename patterns,
* CSV input support,
* structured logging,
* configuration files,
* recursive directory options,
* richer validation rules,
* GitHub Actions for automated test execution,
* packaging the application as an installable Python CLI.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
