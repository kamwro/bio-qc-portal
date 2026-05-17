"""Parser for sample manifest CSV files.

Expected columns: sample_name, organism, assay_type
"""

import csv
import io
from dataclasses import dataclass

REQUIRED_COLUMNS = {"sample_name", "organism", "assay_type"}


@dataclass
class ManifestRow:
    sample_name: str
    organism: str
    assay_type: str


def parse_manifest_csv(content: str) -> list[ManifestRow]:
    """Parse a CSV manifest string and return a list of ManifestRow objects.

    Raises ValueError with a descriptive message on any validation failure.
    """
    reader = csv.DictReader(io.StringIO(content))

    if reader.fieldnames is None:
        raise ValueError("CSV is empty or has no header row")

    actual_columns = {name.strip() for name in reader.fieldnames if name}
    missing = REQUIRED_COLUMNS - actual_columns
    if missing:
        raise ValueError(
            f"Missing required columns: {', '.join(sorted(missing))}. "
            f"Expected: {', '.join(sorted(REQUIRED_COLUMNS))}"
        )

    rows: list[ManifestRow] = []
    for line_num, row in enumerate(reader, start=2):
        sample_name = (row.get("sample_name") or "").strip()
        if not sample_name:
            raise ValueError(f"Row {line_num}: sample_name is empty")

        rows.append(
            ManifestRow(
                sample_name=sample_name,
                organism=(row.get("organism") or "").strip(),
                assay_type=(row.get("assay_type") or "").strip(),
            )
        )

    return rows
