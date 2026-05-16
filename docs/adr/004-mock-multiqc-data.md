# ADR-004: Use mock MultiQC-like data instead of processing real FASTQ files

**Date:** 2026-05-16
**Status:** Accepted

## Context

A real NGS QC workflow may involve large FASTQ files, command-line bioinformatics tools such as FastQC, and aggregation/reporting tools such as MultiQC. Running those tools requires a separate pipeline/runtime environment and is outside the scope of this portal service.

## Decision

Accept pre-computed QC metrics as a **JSON payload** via the import API, rather than running bioinformatics tools inside the web application.

Provide 20 synthetic samples in `samples/qc_metrics.json` that mimic the kind of per-sample summary a QC portal could consume from upstream pipeline outputs.

## Rationale

- The project goal is to model the QC review workflow around precomputed sequencing metrics, not to implement bioinformatics pipeline execution.
- This matches a realistic separation of concerns: upstream pipelines generate QC outputs, while the portal imports, stores, summarizes, and visualizes them.
- MultiQC can export standardized report data in formats such as JSON, TSV, and YAML, making downstream ingestion a reasonable future extension.
- Synthetic data avoids patient privacy concerns and keeps the repository small.
- The MVP import schema uses simplified QC fields: `q30_score`, `gc_content`, `duplication_rate`, `adapter_content`, `mean_read_quality`, and `total_reads`.

## Alternatives considered

- **Process real FASTQ files:** Out of scope for this service; would require larger test data, bioinformatics tooling, longer runtimes, and a separate pipeline/container setup.
- **Parse real MultiQC output in v1:** More realistic, but would add schema-mapping complexity before the core portal workflow is validated.
- **CSV import:** Simpler, but less flexible than JSON for nested or optional fields.

## Consequences

- The `POST /runs/{run_id}/import` endpoint is the sole data ingestion point in the MVP.
- The import format is intentionally simplified and should not be presented as a full MultiQC schema.
- A future improvement would be a parser that maps actual MultiQC JSON output to the portal's internal import schema.
