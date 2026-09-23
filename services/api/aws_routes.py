"""FastAPI router for AWS cloud status and integration endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from rivet.adapters.aws_s3 import generate_presigned_url, upload_audit_receipt, verify_s3_connection
from rivet.adapters.bedrock_planner import verify_bedrock_connection

router = APIRouter(prefix="/api/aws", tags=["aws"])


@router.get("/status")
def aws_status() -> dict[str, Any]:
    """Report live status of AWS Cloud services (S3 and Amazon Bedrock)."""
    s3_info = verify_s3_connection()
    bedrock_info = verify_bedrock_connection()

    cloud_ready = s3_info.get("available", False) or bedrock_info.get("available", False)

    return {
        "status": "online" if cloud_ready else "hybrid_local",
        "cloud_mode": "aws_native" if cloud_ready else "local_with_aws_fallback",
        "s3": s3_info,
        "bedrock": bedrock_info,
        "features": {
            "immutable_receipt_ledger": True,
            "deterministic_compositing": True,
            "presigned_media_urls": True,
            "ftc_claim_auditing": True,
        },
    }


@router.post("/s3/sync-receipt/{project_id}")
def sync_receipt_to_s3(project_id: str, receipt_payload: dict[str, Any]) -> dict[str, Any]:
    """Publish a verified campaign receipt to the Amazon S3 immutable audit bucket."""
    if not project_id:
        raise HTTPException(status_code=400, detail="Missing project_id")

    result = upload_audit_receipt(project_id, receipt_payload)
    return result


@router.get("/s3/presigned/{project_id}/{asset_path:path}")
def get_asset_presigned_url(project_id: str, asset_path: str) -> dict[str, str]:
    """Retrieve a secure AWS S3 pre-signed URL for an exported ad asset."""
    s3_key = f"campaigns/{project_id}/{asset_path}"
    url = generate_presigned_url(s3_key)
    return {"url": url, "s3_key": s3_key}
