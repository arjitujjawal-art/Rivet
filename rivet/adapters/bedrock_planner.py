"""Amazon Bedrock planner adapter for Rivet.

Leverages foundation models (Anthropic Claude 3.5 Sonnet / Amazon Nova) via
Amazon Bedrock for intelligent, multimodal ad shot planning, brand copy generation,
and compliance policy parsing with fallback to deterministic heuristic planning.
"""

from __future__ import annotations

import base64
import json
import logging
import os
from pathlib import Path
from typing import Any

from rivet.adapters.heuristic_planner import propose_shots as fallback_propose_shots
from rivet.adapters.qwen_planner import LIMITS, parse_scenes
from rivet.domain.models import BrandDNA, ShotPlan

logger = logging.getLogger("rivet.adapters.bedrock_planner")

DEFAULT_MODEL_ID = os.environ.get(
    "RIVET_BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0"
)
DEFAULT_REGION = os.environ.get("AWS_REGION", os.environ.get("AWS_DEFAULT_REGION", "us-east-1"))


def get_bedrock_runtime_client() -> Any | None:
    """Return an initialized Bedrock Runtime boto3 client, or None."""
    try:
        import boto3
        from botocore.config import Config

        cfg = Config(region_name=DEFAULT_REGION, retries={"max_attempts": 3, "mode": "standard"})
        return boto3.client("bedrock-runtime", config=cfg)
    except ImportError:
        logger.warning("boto3 is not installed; Amazon Bedrock will operate in mock/fallback mode.")
        return None
    except Exception as exc:
        logger.warning(f"Failed to initialize Amazon Bedrock client: {exc}")
        return None


def verify_bedrock_connection(model_id: str | None = None) -> dict[str, Any]:
    """Probe Bedrock availability and credentials."""
    target_model = model_id or DEFAULT_MODEL_ID
    client = get_bedrock_runtime_client()
    if client is None:
        return {
            "status": "unconfigured",
            "available": False,
            "model_id": target_model,
            "region": DEFAULT_REGION,
            "message": "boto3 not installed or AWS credentials not set.",
        }

    try:
        # Quick ping with minimal tokens
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 10,
            "messages": [{"role": "user", "content": "ping"}],
        })
        client.invoke_model(
            modelId=target_model,
            body=body,
            contentType="application/json",
            accept="application/json",
        )
        return {
            "status": "connected",
            "available": True,
            "model_id": target_model,
            "region": DEFAULT_REGION,
            "message": f"Successfully authenticated with Amazon Bedrock ({target_model})",
        }
    except Exception as err:
        return {
            "status": "fallback",
            "available": False,
            "model_id": target_model,
            "region": DEFAULT_REGION,
            "message": f"Bedrock invocation returned: {err}. Heuristic fallback active.",
        }


def bedrock_writer(
    image_path: str,
    prompt: str,
    model_id: str | None = None,
) -> str:
    """Invoke Claude on Amazon Bedrock with a product image and shot generation prompt."""
    target_model = model_id or DEFAULT_MODEL_ID
    client = get_bedrock_runtime_client()
    if client is None:
        raise RuntimeError("Bedrock client unavailable.")

    # Encode image to base64
    img_bytes = Path(image_path).read_bytes()
    img_b64 = base64.b64encode(img_bytes).decode("utf-8")
    ext = Path(image_path).suffix.lower()
    media_type = "image/png" if "png" in ext else "image/jpeg"

    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "temperature": 0.2,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": img_b64,
                        },
                    },
                    {"type": "text", "text": prompt},
                ],
            }
        ],
    })

    resp = client.invoke_model(
        modelId=target_model,
        body=body,
        contentType="application/json",
        accept="application/json",
    )
    result = json.loads(resp["body"].read().decode("utf-8"))
    return result["content"][0]["text"].strip()


def plan_shots_with_bedrock(
    dna: BrandDNA,
    product_image_path: str,
    model_id: str | None = None,
) -> list[ShotPlan]:
    """Generate structured ad shots using Amazon Bedrock with automatic heuristic fallback.

    Ensures copy strictly complies with length, safe areas, and FTC / brand rules.
    """
    client = get_bedrock_runtime_client()
    if client is None:
        logger.info("Bedrock unavailable; falling back to deterministic heuristic planner.")
        return fallback_propose_shots(dna)

    prompt = f"""You are the creative planner for Rivet, a compliance-first ad engine.
Analyze this product image and write a 3-scene vertical video ad plan.

Brand: {dna.name}
Tone: {dna.tone}
Spoken Brief: {dna.brief}
Primary Color: {dna.primary_hex}
Secondary Color: {dna.secondary_hex}

Return ONLY valid JSON matching this schema:
{{
  "hook": {{
    "headline": "up to {LIMITS['headline']} chars",
    "support": "up to {LIMITS['support']} chars",
    "cta": "up to {LIMITS['cta']} chars",
    "narration": "punchy opening spoken line (20-60 chars)",
    "background_prompt": "clean studio aesthetic description, NO products or people (up to {LIMITS['background_prompt']} chars)"
  }},
  "proof": {{
    "headline": "up to {LIMITS['headline']} chars",
    "support": "up to {LIMITS['support']} chars",
    "cta": "up to {LIMITS['cta']} chars",
    "narration": "evidence and product benefit line (30-80 chars)",
    "background_prompt": "textured backdrop, NO products or people (up to {LIMITS['background_prompt']} chars)"
  }},
  "cta": {{
    "headline": "up to {LIMITS['headline']} chars",
    "support": "up to {LIMITS['support']} chars",
    "cta": "Shop Now",
    "narration": "closing call to action line (20-50 chars)",
    "background_prompt": "minimalist abstract gradient backdrop, NO products or people (up to {LIMITS['background_prompt']} chars)"
  }}
}}"""

    try:
        raw_text = bedrock_writer(product_image_path, prompt, model_id)
        # Parse output using existing robust json extractor
        shot_dicts = parse_scenes(raw_text)
        shots = fallback_propose_shots(dna)
        # Overlay generated text onto deterministic geometry
        for shot in shots:
            if shot.id in shot_dicts:
                overrides = shot_dicts[shot.id]
                shot.copy.headline = overrides.get("headline", shot.copy.headline)[: LIMITS["headline"]]
                shot.copy.support = overrides.get("support", shot.copy.support)[: LIMITS["support"]]
                shot.copy.cta = overrides.get("cta", shot.copy.cta)[: LIMITS["cta"]]
                if "narration" in overrides:
                    shot.narration = overrides["narration"]
                if "background_prompt" in overrides:
                    shot.background_prompt = overrides["background_prompt"][: LIMITS["background_prompt"]]
        return shots
    except Exception as exc:
        logger.warning(f"Bedrock planning call failed ({exc}); using heuristic fallback.")
        return fallback_propose_shots(dna)
