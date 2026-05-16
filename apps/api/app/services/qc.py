from dataclasses import dataclass


@dataclass(frozen=True)
class QCThresholds:
    q30_pass: float = 80.0
    q30_warn: float = 70.0
    gc_min_pass: float = 40.0
    gc_max_pass: float = 60.0
    gc_min_warn: float = 35.0
    gc_max_warn: float = 65.0
    dup_pass: float = 20.0
    dup_warn: float = 50.0
    adapter_pass: float = 5.0
    adapter_warn: float = 10.0


THRESHOLDS = QCThresholds()


def calculate_qc_status(
    q30_score: float,
    gc_content: float,
    duplication_rate: float,
    adapter_content: float,
    thresholds: QCThresholds = THRESHOLDS,
) -> str:
    """Return PASS, WARN, or FAIL based on QC metric thresholds.

    FAIL if any metric is outside the WARN range.
    WARN if any metric is outside the PASS range but within WARN.
    PASS otherwise.
    """
    gc_in_warn = thresholds.gc_min_warn <= gc_content <= thresholds.gc_max_warn
    gc_in_pass = thresholds.gc_min_pass <= gc_content <= thresholds.gc_max_pass

    if (
        q30_score < thresholds.q30_warn
        or not gc_in_warn
        or duplication_rate > thresholds.dup_warn
        or adapter_content > thresholds.adapter_warn
    ):
        return "FAIL"

    if (
        q30_score < thresholds.q30_pass
        or not gc_in_pass
        or duplication_rate > thresholds.dup_pass
        or adapter_content > thresholds.adapter_pass
    ):
        return "WARN"

    return "PASS"
