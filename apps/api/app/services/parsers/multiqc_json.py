"""Parser for MultiQC-like JSON report files.

Expected top-level shape:
{
    "report_generated_on": "<timestamp>",
    "samples": {
        "<sample_name>": {
            "total_sequences":    <int>,
            "percent_above_q30":  <float>,
            "percent_gc":         <float>,
            "percent_duplicates": <float>,
            "adapter_content":    <float>,
            "mean_quality_score": <float>
        },
        ...
    }
}

Field mapping to internal schema:
    total_sequences    -> total_reads
    percent_above_q30  -> q30_score
    percent_gc         -> gc_content
    percent_duplicates -> duplication_rate
    adapter_content    -> adapter_content
    mean_quality_score -> mean_read_quality
"""

from app.schemas.qc_metric import SampleImportItem

REQUIRED_FIELDS = {
    "total_sequences",
    "percent_above_q30",
    "percent_gc",
    "percent_duplicates",
    "adapter_content",
    "mean_quality_score",
}


def parse_multiqc_like_json(data: dict) -> list[SampleImportItem]:
    """Parse a MultiQC-like JSON dict and return SampleImportItems.

    Raises ValueError with a descriptive message on any validation failure.
    """
    samples_data = data.get("samples")
    if not isinstance(samples_data, dict):
        raise ValueError(
            "Expected a top-level 'samples' key containing a dict of sample entries"
        )
    if not samples_data:
        raise ValueError("'samples' dict is empty — no samples to import")

    items: list[SampleImportItem] = []
    for sample_name, metrics in samples_data.items():
        if not isinstance(metrics, dict):
            raise ValueError(
                f"Sample '{sample_name}': metrics must be a JSON object, "
                f"got {type(metrics).__name__}"
            )

        missing = REQUIRED_FIELDS - set(metrics.keys())
        if missing:
            raise ValueError(
                f"Sample '{sample_name}' is missing required fields: "
                f"{', '.join(sorted(missing))}"
            )

        try:
            items.append(
                SampleImportItem(
                    sample_name=sample_name,
                    total_reads=int(metrics["total_sequences"]),
                    q30_score=float(metrics["percent_above_q30"]),
                    gc_content=float(metrics["percent_gc"]),
                    duplication_rate=float(metrics["percent_duplicates"]),
                    adapter_content=float(metrics["adapter_content"]),
                    mean_read_quality=float(metrics["mean_quality_score"]),
                )
            )
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"Sample '{sample_name}': could not convert metric value — {exc}"
            ) from exc

    return items
