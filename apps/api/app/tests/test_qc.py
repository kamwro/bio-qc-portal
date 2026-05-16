import pytest

from app.services.qc import QCThresholds, calculate_qc_status

T = QCThresholds()


@pytest.mark.parametrize(
    "q30,gc,dup,adapter,expected",
    [
        # Clear PASS
        (85.0, 50.0, 15.0, 2.0, "PASS"),
        # Q30 exactly at pass threshold
        (80.0, 50.0, 15.0, 2.0, "PASS"),
        # Q30 just below pass → WARN
        (79.9, 50.0, 15.0, 2.0, "WARN"),
        # Q30 below warn → FAIL
        (69.9, 50.0, 15.0, 2.0, "FAIL"),
        # GC too low → FAIL
        (85.0, 30.0, 15.0, 2.0, "FAIL"),
        # GC warn-low range → WARN
        (85.0, 37.0, 15.0, 2.0, "WARN"),
        # GC warn-high range → WARN
        (85.0, 63.0, 15.0, 2.0, "WARN"),
        # GC too high → FAIL
        (85.0, 70.0, 15.0, 2.0, "FAIL"),
        # Dup above pass threshold -> WARN
        (85.0, 50.0, 25.0, 2.0, "WARN"),
        # Dup remains WARN up to the FastQC-inspired failure threshold
        (85.0, 50.0, 40.0, 2.0, "WARN"),
        (85.0, 50.0, 50.0, 2.0, "WARN"),
        # Dup above warn threshold -> FAIL
        (85.0, 50.0, 50.1, 2.0, "FAIL"),
        # Adapter above pass threshold → WARN
        (85.0, 50.0, 15.0, 7.0, "WARN"),
        # Adapter above warn threshold → FAIL
        (85.0, 50.0, 15.0, 12.0, "FAIL"),
        # Multiple borderline metrics → WARN (worst single metric drives it)
        (79.0, 41.0, 21.0, 6.0, "WARN"),
    ],
)
def test_calculate_qc_status(q30, gc, dup, adapter, expected):
    result = calculate_qc_status(q30, gc, dup, adapter)
    assert result == expected


def test_custom_thresholds():
    strict = QCThresholds(q30_pass=90.0, q30_warn=85.0)
    assert calculate_qc_status(88.0, 50.0, 15.0, 2.0, strict) == "WARN"
    assert calculate_qc_status(84.0, 50.0, 15.0, 2.0, strict) == "FAIL"
