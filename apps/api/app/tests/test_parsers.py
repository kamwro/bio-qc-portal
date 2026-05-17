"""Unit tests for CSV manifest and MultiQC-like JSON parsers."""

import pytest

from app.services.parsers.manifest_csv import ManifestRow, parse_manifest_csv
from app.services.parsers.multiqc_json import parse_multiqc_like_json

# ── Manifest CSV ───────────────────────────────────────────────────────────────

VALID_CSV = """sample_name,organism,assay_type
SAMP001,Homo sapiens,WGS
SAMP002,Homo sapiens,WES
SAMP003,Mus musculus,ChIP-seq
"""


def test_manifest_csv_valid():
    rows = parse_manifest_csv(VALID_CSV)
    assert len(rows) == 3
    assert rows[0] == ManifestRow(
        sample_name="SAMP001", organism="Homo sapiens", assay_type="WGS"
    )
    assert rows[2].sample_name == "SAMP003"
    assert rows[2].organism == "Mus musculus"


def test_manifest_csv_extra_columns_are_ignored():
    csv = "sample_name,organism,assay_type,extra_col\nS1,Homo sapiens,WGS,ignored\n"
    rows = parse_manifest_csv(csv)
    assert len(rows) == 1
    assert rows[0].sample_name == "S1"


def test_manifest_csv_missing_organism_column():
    csv = "sample_name,assay_type\nS1,WGS\n"
    with pytest.raises(ValueError, match="Missing required columns"):
        parse_manifest_csv(csv)


def test_manifest_csv_missing_assay_type_column():
    csv = "sample_name,organism\nS1,Homo sapiens\n"
    with pytest.raises(ValueError, match="Missing required columns"):
        parse_manifest_csv(csv)


def test_manifest_csv_missing_sample_name_column():
    csv = "organism,assay_type\nHomo sapiens,WGS\n"
    with pytest.raises(ValueError, match="Missing required columns"):
        parse_manifest_csv(csv)


def test_manifest_csv_missing_multiple_columns():
    csv = "sample_name\nS1\n"
    with pytest.raises(ValueError, match="Missing required columns"):
        parse_manifest_csv(csv)


def test_manifest_csv_empty_sample_name_row():
    csv = "sample_name,organism,assay_type\n,Homo sapiens,WGS\n"
    with pytest.raises(ValueError, match="Row 2: sample_name is empty"):
        parse_manifest_csv(csv)


def test_manifest_csv_empty_content():
    with pytest.raises(ValueError, match="empty or has no header"):
        parse_manifest_csv("")


def test_manifest_csv_header_only_returns_empty_list():
    rows = parse_manifest_csv("sample_name,organism,assay_type\n")
    assert rows == []


def test_manifest_csv_whitespace_trimmed():
    csv = "sample_name,organism,assay_type\n  SAMP001 , Homo sapiens , WGS \n"
    rows = parse_manifest_csv(csv)
    assert rows[0].sample_name == "SAMP001"
    assert rows[0].organism == "Homo sapiens"
    assert rows[0].assay_type == "WGS"


# ── MultiQC-like JSON ──────────────────────────────────────────────────────────

VALID_MULTIQC = {
    "report_generated_on": "2024-01-15",
    "samples": {
        "SAMP001": {
            "total_sequences": 52000000,
            "percent_above_q30": 85.2,
            "percent_gc": 48.5,
            "percent_duplicates": 12.3,
            "adapter_content": 1.8,
            "mean_quality_score": 37.1,
        },
        "SAMP002": {
            "total_sequences": 48000000,
            "percent_above_q30": 78.4,
            "percent_gc": 51.0,
            "percent_duplicates": 22.1,
            "adapter_content": 3.2,
            "mean_quality_score": 35.6,
        },
    },
}


def test_multiqc_valid():
    items = parse_multiqc_like_json(VALID_MULTIQC)
    assert len(items) == 2
    samp1 = next(i for i in items if i.sample_name == "SAMP001")
    assert samp1.total_reads == 52000000
    assert samp1.q30_score == 85.2
    assert samp1.gc_content == 48.5
    assert samp1.duplication_rate == 12.3
    assert samp1.adapter_content == 1.8
    assert samp1.mean_read_quality == 37.1


def test_multiqc_field_mapping():
    items = parse_multiqc_like_json(VALID_MULTIQC)
    samp2 = next(i for i in items if i.sample_name == "SAMP002")
    assert samp2.total_reads == 48000000
    assert samp2.q30_score == 78.4
    assert samp2.duplication_rate == 22.1


def test_multiqc_missing_samples_key():
    with pytest.raises(ValueError, match="Expected a top-level 'samples' key"):
        parse_multiqc_like_json({"report_generated_on": "2024-01-15"})


def test_multiqc_samples_not_a_dict():
    with pytest.raises(ValueError, match="Expected a top-level 'samples' key"):
        parse_multiqc_like_json({"samples": ["not", "a", "dict"]})


def test_multiqc_empty_samples():
    with pytest.raises(ValueError, match="'samples' dict is empty"):
        parse_multiqc_like_json({"samples": {}})


def test_multiqc_missing_required_field():
    data = {
        "samples": {
            "SAMP001": {
                "total_sequences": 50000000,
                # percent_above_q30 missing
                "percent_gc": 48.5,
                "percent_duplicates": 12.3,
                "adapter_content": 1.8,
                "mean_quality_score": 37.1,
            }
        }
    }
    with pytest.raises(ValueError, match="SAMP001.*missing required fields"):
        parse_multiqc_like_json(data)


def test_multiqc_missing_multiple_fields():
    data = {
        "samples": {
            "SAMP001": {
                "total_sequences": 50000000,
            }
        }
    }
    with pytest.raises(ValueError, match="SAMP001.*missing required fields"):
        parse_multiqc_like_json(data)


def test_multiqc_non_numeric_field():
    data = {
        "samples": {
            "SAMP001": {
                "total_sequences": "not_a_number",
                "percent_above_q30": 85.2,
                "percent_gc": 48.5,
                "percent_duplicates": 12.3,
                "adapter_content": 1.8,
                "mean_quality_score": 37.1,
            }
        }
    }
    with pytest.raises(ValueError, match="could not convert metric value"):
        parse_multiqc_like_json(data)


def test_multiqc_sample_metrics_not_a_dict():
    data = {"samples": {"SAMP001": "not_a_dict"}}
    with pytest.raises(ValueError, match="SAMP001.*metrics must be a JSON object"):
        parse_multiqc_like_json(data)
