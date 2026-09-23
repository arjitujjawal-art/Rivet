# Rivet — AWS Hackathon Submission Dossier

**First Commit — WeMakeDevs x AWS Hackathon 2026**  
**Track:** *Ship It* (Production-Ready, Fully Deployed Platforms)  
**Team Code:** `PYY34M`  
**Team Name:** Team choco  
**Members:**  
- **Ganesh Nair** (Team Lead)  
- **Arjit Ujjawal**  

---

## 1. Executive Summary

Generative AI allows brands to generate dozens of ad variations in seconds. However, **generative AI is fundamentally unsafe for advertising**:
- Models alter logos, packaging colors, and product geometry.
- Models hallucinate unverified superlatives ("clinically proven", "100% waterproof", "FDA approved"), triggering catastrophic FTC penalties and Amazon Ad rejections.
- Small and medium e-commerce sellers lack full-time legal, brand-safety, and compliance teams.

**Rivet is the compliance-first AI advertising platform that turns ad generation from a trust-based workflow into a cryptographic, verification-based one.**

Instead of blindly shipping AI output, Rivet isolates generative creativity to background rendering while **compositing all protected brand assets (product, logo, typography) deterministically**. Furthermore, every scene is evaluated against **11 named audit checks (`A01`–`A11`)**. If even one check fails, **export is refused**, and an immutable signed **Campaign Audit Receipt** is stored in **Amazon S3**.

---

## 2. AWS Cloud Architecture

Rivet is engineered natively for AWS Cloud deployment under the *Ship It* track criteria:

```
                  +----------------------------------------------+
                  |               E-Commerce Client              |
                  |     (Brand Kit + Spoken Brief + Product)     |
                  +----------------------+-----------------------+
                                         |
                                         v
+---------------------------------------------------------------------------------+
|                                AWS Cloud Boundary                               |
|                                                                                 |
|   +------------------------------------+    +-------------------------------+   |
|   |         Amazon S3 Bucket           |    |        Amazon Bedrock         |   |
|   |  - Approved Brand Kit Vectors      |    |  - Claude 3.5 Sonnet / Nova   |   |
|   |  - Immutable Audit Receipts        |    |  - Multimodal Scene Planning  |   |
|   |  - Exported Multi-Format Packs     |    |  - FTC Claim Validation (A07) |   |
|   +-----------------+------------------+    +---------------+---------------+   |
|                     ^                                       ^                   |
|                     |                                       |                   |
|                     +-------------------+-------------------+                   |
|                                         |                                       |
|                                         v                                       |
|   +-------------------------------------------------------------------------+   |
|   |                  AWS App Runner / ECS Fargate Container                 |   |
|   |                                                                         |   |
|   |   +------------------------+          +-----------------------------+   |   |
|   |   | React 19 Web Studio    | <------> | FastAPI Verification API    |   |   |
|   |   | (GSAP, Tailwind, Vite) |          | (Pillow, NumPy, FFmpeg)     |   |   |
|   |   +------------------------+          +--------------+--------------+   |   |
|   |                                                      |                  |   |
|   |                                                      v                  |   |
|   |                                       +-----------------------------+   |   |
|   |                                       | 11 Named Verification Checks|   |   |
|   |                                       | (A01 Tamper, A02 Fidelity,  |   |   |
|   |                                       |  A03 Copy, A05 Safe Area,   |   |   |
|   |                                       |  A07 Claims, A10 Contrast)  |   |   |
|   |                                       +--------------+--------------+   |   |
|   +------------------------------------------------------|------------------+   |
|                                                          |                      |
|                                                          v                      |
|                                           +-----------------------------+       |
|                                           | Cryptographic Export Gate   |       |
|                                           | Pass: Signed Export Pack    |       |
|                                           | Fail: Needs Repair Refusal  |       |
|                                           +-----------------------------+       |
+---------------------------------------------------------------------------------+
```

### AWS Services Breakdown

1. **Amazon Bedrock (Generative Intelligence & Compliance)**:
   - Evaluates the spoken brief and product shot to propose structured hook/proof/CTA scene plans.
   - Enforces FTC and marketplace advertising guidelines by identifying forbidden claim patterns (`A07`).
   - Advisory visual semantic fit evaluation (`A08`).

2. **Amazon S3 (Immutable Audit Ledger & Asset Hub)**:
   - Stores master brand kits with version control.
   - Acts as an immutable legal audit ledger: every campaign export or refusal writes a cryptographically hashed `receipt.json` with SHA-256 metadata tags.
   - Secure pre-signed URLs allow advertisers to share verified ads with partners safely.

3. **AWS App Runner / ECS Fargate (Unified Fullstack Server)**:
   - Multi-stage Docker container serving both the React 19 frontend and Python FastAPI backend on port 8000.
   - Zero-ops autoscaling from low-traffic SMB sellers to high-volume brand agencies.

4. **AWS IAM & CloudFormation**:
   - Infrastructure-as-code template (`deploy/cloudformation.yaml`) provisions least-privilege policies, S3 buckets, and service roles with one CLI invocation.

---

## 3. The 11 Core Audit Checks (`A01`–`A11`)

| Code | Check Name | Target | Mathematical / Algorithmic Guarantee |
| :--- | :--- | :--- | :--- |
| **A01** | Lineage & Tamper | Product & Logo | Byte-exact SHA-256 match against brand kit registration |
| **A02** | Logo Fidelity | Rendered Logo | Mean pixel difference $\le 40$ against source logo |
| **A03** | Copy Integrity | Typography | Exact character match between approved copy and rendered text |
| **A04** | Palette Drift | Backgrounds | Delta-E color distance within brand allowable harmony |
| **A05** | Safe Area | Geometry | Zero pixels intersecting platform title/safe-zone boundaries |
| **A06** | Product Share | Prominence | Cutout area must exceed required minimum frame share ($\ge 5\%$) |
| **A07** | Forbidden Claims | Language/Audio | 0 unverified or disallowed claims; automated copy repair |
| **A08** | Semantic Fit | Ad Concept | Advisory scene relevance scored by foundation model |
| **A09** | Cutout Accuracy | Segmentation | Mask pixel difference $\le 40$ against source cutout |
| **A10** | Text Contrast | Accessibility | Minimum 4.5:1 WCAG luminance ratio against dynamic background |
| **A11** | Font Coverage | Typography | Validates that 100% of unicode glyphs exist in the loaded font |

---

## 4. How to Deploy & Verify

### One-Command Local / Docker Run
```bash
# Spins up fullstack Studio and API in seconds
docker compose up --build
```
Navigate to: **`http://localhost:8000`**

### One-Command AWS Cloud Deployment
```bash
# Requires AWS CLI configured
./deploy/aws-deploy.sh
```

### Automated Verification
```bash
# Verify AWS status endpoint
curl http://localhost:8000/api/aws/status

# Run test suite
pytest -q tests/unit/test_audit_checks.py tests/unit/test_receipt.py
```

---

## 5. Hackathon Submission Checklist

- [x] Working code for all 11 audit checks
- [x] Deterministic Pillow compositing engine (zero model hallucination on products)
- [x] AWS S3 immutable audit receipt ledger integration
- [x] Amazon Bedrock foundation model adapter
- [x] React 19 + Tailwind + GSAP Web Studio interface
- [x] Multi-format video/feed/banner rendering pipeline
- [x] Turnkey `Dockerfile`, `docker-compose.yml`, and `cloudformation.yaml`
- [x] Production documentation and team credentials (Team choco, code `PYY34M`)
