#!/usr/bin/env python3
"""Seed demo data into the running BioQC Portal API."""

import json
import sys
from pathlib import Path

import httpx

API_URL = "http://localhost:8000/api"
SAMPLES_FILE = Path(__file__).parent.parent.parent / "samples" / "qc_metrics.json"


def main() -> None:
    client = httpx.Client(base_url=API_URL, timeout=10)

    project = client.post(
        "/projects",
        json={
            "name": "Demo WGS Project",
            "description": (
                "Example whole-genome sequencing project with 20 synthetic samples."
            ),
        },
    )
    project.raise_for_status()
    project_id = project.json()["id"]
    print(f"Created project:  {project_id}")

    run = client.post(
        f"/projects/{project_id}/runs",
        json={"name": "Run-2024-Q1-NovaSeq", "platform": "Illumina NovaSeq 6000"},
    )
    run.raise_for_status()
    run_id = run.json()["id"]
    print(f"Created run:      {run_id}")

    with open(SAMPLES_FILE) as f:
        payload = json.load(f)

    result = client.post(f"/runs/{run_id}/import", json=payload)
    result.raise_for_status()
    body = result.json()

    print(
        f"Imported {body['imported']} samples: "
        f"{body['pass_count']} PASS  "
        f"{body['warn_count']} WARN  "
        f"{body['fail_count']} FAIL"
    )
    print("\nDemo data ready — visit http://localhost:5173")


if __name__ == "__main__":
    try:
        main()
    except httpx.ConnectError:
        print(
            "ERROR: Cannot reach http://localhost:8000 — is the API running?",
            file=sys.stderr,
        )
        sys.exit(1)
