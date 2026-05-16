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
