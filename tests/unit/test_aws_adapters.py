import pytest
from rivet.adapters.aws_s3 import generate_presigned_url, upload_audit_receipt, verify_s3_connection
from rivet.adapters.bedrock_planner import verify_bedrock_connection
from services.api.main import create_app
from starlette.testclient import TestClient


def test_aws_s3_connection_verification():
    status = verify_s3_connection("test-bucket")
    assert "status" in status
    assert "bucket" in status
    assert status["bucket"] == "test-bucket"


def test_aws_s3_receipt_upload_fallback():
    receipt_data = {
        "project_id": "proj-123",
        "hash": "abc123sha",
        "passed": True,
        "checks": [{"id": "A01", "status": "pass"}],
    }
    result = upload_audit_receipt("proj-123", receipt_data, bucket="test-bucket")
    assert "s3_uri" in result
    assert "sha256" in result
    assert "proj-123" in result["s3_uri"]


def test_aws_s3_presigned_url():
    url = generate_presigned_url("campaigns/p1/video.mp4", bucket="my-bucket")
    assert "my-bucket" in url
    assert "campaigns/p1/video.mp4" in url


def test_bedrock_verification():
    status = verify_bedrock_connection()
    assert "status" in status
    assert "model_id" in status


def test_api_aws_status_endpoint():
    app = create_app()
    client = TestClient(app)
    resp = client.get("/api/aws/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data
    assert "s3" in data
    assert "bedrock" in data
    assert "features" in data
    assert data["features"]["immutable_receipt_ledger"] is True
