# ADR-005: Use simple threshold-based QC rules for explainability

**Date:** 2026-05-16
**Status:** Accepted

## Context

We need to classify each sample as PASS, WARN, or FAIL based on its QC metrics. The classification logic must be understandable by wet lab scientists, analysts, and engineers reviewing the dashboard.

Real sequencing QC interpretation depends on assay type, organism, library preparation, sequencing platform, and downstream analysis goals. For this MVP, we need a transparent rule set that is easy to explain and unit test, rather than a production-grade scientific QC policy.

## Decision

Use **hard threshold comparisons** on four simplified QC metrics with two threshold levels each: PASS/WARN and WARN/FAIL.

| Metric              | PASS    | WARN      | FAIL          |
| ------------------- | ------- | --------- | ------------- |
| Q30 score (%)       | ≥ 80    | 70 – 79.9 | < 70          |
| GC content (%)      | 40 – 60 | 35 – 65   | outside 35–65 |
| Duplication (%)     | ≤ 20    | 20.1 – 50 | > 50          |
| Adapter content (%) | ≤ 5     | 5.1 – 10  | > 10          |

A sample FAILs if **any** metric is outside the WARN range. It WARNs if **any** metric is outside the PASS range. Otherwise it PASSes.

## Rationale

- The selected metrics are common sequencing QC review signals: base quality, GC content, duplication, adapter contamination, and read volume.
- Q30 is a widely used sequencing quality concept; Illumina describes Q30 as approximately a 1 in 1,000 incorrect base-call probability, or 99.9% base-call accuracy.
- FastQC uses PASS/WARN/FAIL-style quality modules, which makes threshold-based classification familiar to users who have seen sequencing QC reports.
- The adapter-content thresholds intentionally mirror FastQC’s warning above 5% and failure above 10%.
- The duplication thresholds are FastQC-inspired: FastQC warns above 20% non-unique sequences and fails above 50%.
- GC content is simplified for the MVP. FastQC evaluates GC content by deviation from an expected distribution, so the absolute GC ranges here should be treated as demo thresholds, not a FastQC-equivalent rule.
- A simple worst-metric-wins rule is transparent: the UI can show exactly which metric caused a WARN or FAIL.
- Threshold values are centralized in a `QCThresholds` dataclass, making them easy to override in tests or extend to per-project configuration.

## Alternatives considered

- **ML-based outlier detection:** Powerful but opaque to wet lab users; unnecessary for the current threshold-based review workflow.
- **Weighted scoring:** More nuanced but harder to explain and debug.
- **Assay-specific QC profiles:** More realistic, but out of scope for the MVP.

## Consequences

- The thresholds are currently global and simplified.
- The classification should be documented in the UI so users understand that this is a review aid, not a clinical or production QC decision engine.
- A future improvement is per-project or per-assay configurable thresholds stored in the database.
- The `calculate_qc_status` function is pure, with no DB access, making it easy to unit test exhaustively.

## References

- Illumina. _Quality Scores for Next-Generation Sequencing_. Explains Q30 as 1 incorrect base call in 1,000, or 99.9% base-call accuracy.
  https://www.illumina.com/documents/products/technotes/technote_Q-Scores.pdf

- FastQC. _Adapter Content_. Documents warning above 5% and failure above 10% adapter content.
  https://www.bioinformatics.babraham.ac.uk/projects/fastqc/Help/3%20Analysis%20Modules/10%20Adapter%20Content.html

- FastQC. _Duplicate Sequences_. Documents warning above 20% and failure above 50% non-unique sequences.
  https://www.bioinformatics.babraham.ac.uk/projects/fastqc/Help/3%20Analysis%20Modules/8%20Duplicate%20Sequences.html

- FastQC. _Per Sequence GC Content_. Documents GC evaluation based on deviation from an expected distribution, not fixed absolute GC ranges.
  https://www.bioinformatics.babraham.ac.uk/projects/fastqc/Help/3%20Analysis%20Modules/5%20Per%20Sequence%20GC%20Content.html
