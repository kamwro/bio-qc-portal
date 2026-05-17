import pytest
from fastapi.testclient import TestClient

# ── Health ─────────────────────────────────────────────────────────────────────


def test_health(client: TestClient):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


# ── Projects ───────────────────────────────────────────────────────────────────


def test_create_and_list_projects(client: TestClient):
    r = client.post("/api/projects", json={"name": "Alpha", "description": "test"})
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "Alpha"

    r2 = client.get("/api/projects")
    assert r2.status_code == 200
    assert len(r2.json()) == 1


def test_get_project_not_found(client: TestClient):
    r = client.get("/api/projects/nonexistent")
    assert r.status_code == 404


def test_delete_project(client: TestClient):
    project_id = client.post("/api/projects", json={"name": "ToDelete"}).json()["id"]
    r = client.delete(f"/api/projects/{project_id}")
    assert r.status_code == 204
    assert client.get(f"/api/projects/{project_id}").status_code == 404


# ── Runs ───────────────────────────────────────────────────────────────────────


def test_create_and_list_runs(client: TestClient):
    project_id = client.post("/api/projects", json={"name": "P1"}).json()["id"]
    r = client.post(
        f"/api/projects/{project_id}/runs",
        json={"name": "Run-001", "platform": "Illumina NovaSeq 6000"},
    )
    assert r.status_code == 201
    assert r.json()["status"] == "pending"

    runs = client.get(f"/api/projects/{project_id}/runs").json()
    assert len(runs) == 1


# ── Import & QC ────────────────────────────────────────────────────────────────

SAMPLE_PAYLOAD = {
    "samples": [
        {
            "sample_name": "S001",
            "external_id": "EXT001",
            "total_reads": 50_000_000,
            "q30_score": 85.0,
            "gc_content": 50.0,
            "duplication_rate": 10.0,
            "adapter_content": 1.5,
            "mean_read_quality": 37.0,
        },
        {
            "sample_name": "S002",
            "external_id": "EXT002",
            "total_reads": 40_000_000,
            "q30_score": 75.0,  # WARN
            "gc_content": 50.0,
            "duplication_rate": 10.0,
            "adapter_content": 1.5,
            "mean_read_quality": 35.0,
        },
        {
            "sample_name": "S003",
            "total_reads": 20_000_000,
            "q30_score": 60.0,  # FAIL
            "gc_content": 50.0,
            "duplication_rate": 10.0,
            "adapter_content": 1.5,
            "mean_read_quality": 30.0,
        },
    ]
}


@pytest.fixture
def run_id(client: TestClient) -> str:
    project_id = client.post("/api/projects", json={"name": "P"}).json()["id"]
    return client.post(
        f"/api/projects/{project_id}/runs",
        json={"name": "R", "platform": "NextSeq"},
    ).json()["id"]


def test_import_samples(client: TestClient, run_id: str):
    r = client.post(f"/api/runs/{run_id}/import", json=SAMPLE_PAYLOAD)
    assert r.status_code == 201
    body = r.json()
    assert body["imported"] == 3
    assert body["pass_count"] == 1
    assert body["warn_count"] == 1
    assert body["fail_count"] == 1


def test_list_samples(client: TestClient, run_id: str):
    client.post(f"/api/runs/{run_id}/import", json=SAMPLE_PAYLOAD)
    samples = client.get(f"/api/runs/{run_id}/samples").json()
    assert len(samples) == 3
    assert all("qc_metric" in s for s in samples)


def test_qc_summary(client: TestClient, run_id: str):
    client.post(f"/api/runs/{run_id}/import", json=SAMPLE_PAYLOAD)
    summary = client.get(f"/api/runs/{run_id}/qc-summary").json()
    assert summary["total_samples"] == 3
    assert summary["pass_count"] == 1
    assert summary["warn_count"] == 1
    assert summary["fail_count"] == 1


def test_run_report(client: TestClient, run_id: str):
    client.post(f"/api/runs/{run_id}/import", json=SAMPLE_PAYLOAD)
    report = client.get(f"/api/runs/{run_id}/report").json()
    assert report["total_samples"] == 3
    assert "worst_samples_by_adapter_content" in report


def test_get_sample(client: TestClient, run_id: str):
    client.post(f"/api/runs/{run_id}/import", json=SAMPLE_PAYLOAD)
    sample_id = client.get(f"/api/runs/{run_id}/samples").json()[0]["id"]
    r = client.get(f"/api/samples/{sample_id}")
    assert r.status_code == 200
    assert "qc_metric" in r.json()


# ── File-based import ──────────────────────────────────────────────────────────

MANIFEST_CSV = """sample_name,organism,assay_type
S001,Homo sapiens,WGS
S002,Homo sapiens,WGS
"""

SIMPLE_JSON_FILE = """{
  "samples": [
    {
      "sample_name": "S001",
      "total_reads": 50000000,
      "q30_score": 85.0,
      "gc_content": 50.0,
      "duplication_rate": 10.0,
      "adapter_content": 1.5,
      "mean_read_quality": 37.0
    },
    {
      "sample_name": "S002",
      "total_reads": 40000000,
      "q30_score": 75.0,
      "gc_content": 50.0,
      "duplication_rate": 10.0,
      "adapter_content": 1.5,
      "mean_read_quality": 35.0
    }
  ]
}"""

MULTIQC_LIKE_FILE = """{
  "report_generated_on": "2024-01-15",
  "samples": {
    "S001": {
      "total_sequences": 50000000,
      "percent_above_q30": 85.0,
      "percent_gc": 50.0,
      "percent_duplicates": 10.0,
      "adapter_content": 1.5,
      "mean_quality_score": 37.0
    },
    "S002": {
      "total_sequences": 40000000,
      "percent_above_q30": 75.0,
      "percent_gc": 50.0,
      "percent_duplicates": 10.0,
      "adapter_content": 1.5,
      "mean_quality_score": 35.0
    }
  }
}"""


def _file_import(client: TestClient, run_id: str, qc_body: str, qc_format: str):
    return client.post(
        f"/api/runs/{run_id}/import/files",
        files={
            "manifest_file": ("manifest.csv", MANIFEST_CSV, "text/csv"),
            "qc_file": ("qc.json", qc_body, "application/json"),
        },
        data={"qc_format": qc_format},
    )


def test_file_import_simple_json(client: TestClient, run_id: str):
    r = _file_import(client, run_id, SIMPLE_JSON_FILE, "simple_json")
    assert r.status_code == 201
    body = r.json()
    assert body["imported"] == 2
    assert body["pass_count"] + body["warn_count"] + body["fail_count"] == 2


def test_file_import_multiqc_like(client: TestClient, run_id: str):
    r = _file_import(client, run_id, MULTIQC_LIKE_FILE, "multiqc_like")
    assert r.status_code == 201
    body = r.json()
    assert body["imported"] == 2


def test_file_import_filters_by_manifest(client: TestClient, run_id: str):
    # Manifest only has S001; QC file has S001 and S002 — only S001 should import
    manifest = "sample_name,organism,assay_type\nS001,Homo sapiens,WGS\n"
    r = client.post(
        f"/api/runs/{run_id}/import/files",
        files={
            "manifest_file": ("manifest.csv", manifest, "text/csv"),
            "qc_file": ("qc.json", MULTIQC_LIKE_FILE, "application/json"),
        },
        data={"qc_format": "multiqc_like"},
    )
    assert r.status_code == 201
    assert r.json()["imported"] == 1


def test_file_import_invalid_manifest_columns(client: TestClient, run_id: str):
    bad_manifest = "sample_name,wrong_col\nS001,foo\n"
    r = client.post(
        f"/api/runs/{run_id}/import/files",
        files={
            "manifest_file": ("manifest.csv", bad_manifest, "text/csv"),
            "qc_file": ("qc.json", MULTIQC_LIKE_FILE, "application/json"),
        },
        data={"qc_format": "multiqc_like"},
    )
    assert r.status_code == 422
    assert "Manifest CSV error" in r.json()["detail"]


def test_file_import_no_matching_samples(client: TestClient, run_id: str):
    manifest = "sample_name,organism,assay_type\nNOT_IN_QC,Homo sapiens,WGS\n"
    r = client.post(
        f"/api/runs/{run_id}/import/files",
        files={
            "manifest_file": ("manifest.csv", manifest, "text/csv"),
            "qc_file": ("qc.json", MULTIQC_LIKE_FILE, "application/json"),
        },
        data={"qc_format": "multiqc_like"},
    )
    assert r.status_code == 422
    assert "No QC samples matched" in r.json()["detail"]


def test_file_import_unknown_format(client: TestClient, run_id: str):
    r = _file_import(client, run_id, SIMPLE_JSON_FILE, "unknown_format")
    assert r.status_code == 422
    assert "Unknown qc_format" in r.json()["detail"]


def test_file_import_invalid_json_qc_file(client: TestClient, run_id: str):
    r = client.post(
        f"/api/runs/{run_id}/import/files",
        files={
            "manifest_file": ("manifest.csv", MANIFEST_CSV, "text/csv"),
            "qc_file": ("qc.json", "not valid json{{{", "application/json"),
        },
        data={"qc_format": "simple_json"},
    )
    assert r.status_code == 422
    assert "not valid JSON" in r.json()["detail"]
