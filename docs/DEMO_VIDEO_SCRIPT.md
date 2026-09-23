# Rivet — 3-Minute Video Demo Script (Ship It Track)

**First Commit — WeMakeDevs x AWS Hackathon 2026**  
**Team choco (`PYY34M`)** — Ganesh Nair & Arjit Ujjawal  
**Target Video Duration:** Exactly 2:45 to 3:00 minutes.  
**Core Thesis:** *Rivet generates AI ads, but only lets them ship when product assets, claims, and brand rules are verified—and it gives you proof of what passed.*

---

## Screenplay & Shot Breakdown

### [0:00 - 0:40] The Problem & The Amazon Seller Dilemma
- **Visual:** 
  - Open on a browser showing an AI-generated product ad with distorted logos, text overlapping safe areas, or claiming "100% Waterproof & Clinically Proven".
  - Cut to Rivet's Landing Page (`http://localhost:8000`).
- **Audio / Narration:**
  > "Generative AI made creating video ads instantaneous. But for e-commerce operators and Amazon Sellers, AI ads are dangerous. Models hallucinate claims like 'clinically proven', bend brand logos, and violate platform safe areas. A single unverified claim can trigger FTC fines or get an Amazon Ads account suspended. Small brands can't afford a team of corporate lawyers to review every AI-generated variant. Most AI tools ask you to trust the model. Rivet doesn't. In Rivet, a failing ad is mathematically blocked from export."

---

### [0:40 - 1:30] The Verified Flow & AWS Architecture
- **Visual:**
  - Click **Open Studio** -> lands on `http://localhost:8000/studio`.
  - Point to the bottom-left sidebar badge: **AWS Cloud Native** (`BEDROCK + S3`).
  - Highlight the 3 scenes: **Hook**, **Proof**, and **Call to Action**.
  - Show the right-hand **Quality Control Panel**:
    - `A01` Asset Lineage: `exact sha256 match`
    - `A02` Logo Fidelity: `9.3 px` (threshold $\le 40$)
    - `A03` Copy Integrity: `match`
    - `A10` Text Contrast: `7.28` (WCAG threshold $\ge 4.0$)
  - Click **Export**: Notice the export pack is generated, and expand the **Campaign Receipt** drawer showing:
    - `AWS S3 Ledger`: `s3://rivet-campaigns/66ea.../receipt.json`
    - `Audit Result`: `100% PASSED (EXPORT CERTIFIED)`
- **Audio / Narration:**
  > "Here is Rivet in action. Built with Amazon Bedrock and Amazon S3. We feed in our source product image, approved brand kit, and a spoken brief. Claude 3.5 Sonnet on Bedrock plans our three-scene story beats. But notice our protected layers—the speaker cutout, logo, and typography—are never re-imagined by the model. They are deterministically composited from approved vector and raster assets.
  > Every scene runs through 11 named verification checks. Not a vague confidence score, but exact numbers: logo pixel drift of 9.3 against a threshold of 40, contrast ratio of 7.28. All 11 checks pass, the export gate opens, and an immutable audit receipt is cryptographically tagged and pushed to Amazon S3."

---

### [1:30 - 2:30] The Climax: Tampered Asset & The Hard Export Gate
- **Visual:**
  - In the sidebar bottom toggle under **Demo state**, click **Tampered**.
  - **Immediate visual change:**
    - The preview stage border glows red with a danger banner: *"Product mismatch detected. Repair the scene before export."*
    - The preview image switches to `/scene-blocked.jpg` (subtle distortion/unapproved variant).
    - In the Quality Control Panel: `A01` lights up bright red with `FAIL: MISMATCH · Export Gated`.
    - Point mouse to the bottom-right **Export Button**: It is locked and disabled with the label: **"Export blocked"**.
    - Click it repeatedly to prove the system refuses to write the export pack.
- **Audio / Narration:**
  > "Now, here is what sets Rivet apart from every other AI generator. Let's simulate a tampered asset—someone swapped the product file with an unapproved mock, or the model attempted to inject an unverified claim.
  > Visually, the ad still looks convincing to human eyes. But Rivet doesn't rely on human eyes or trust. Check A01 performs a byte-level SHA-256 hash comparison against the brand registry. It detects a mismatch.
  > The status immediately flips to 'Export Blocked'. The export button is hard-gated. The ad cannot ship. The system records why in a signed S3 audit receipt. We don't just generate ads; we guarantee brand compliance before a single dollar of ad spend is wasted."

---

### [2:30 - 3:00] AWS "Ship It" Track Summary & Live Deployment
- **Visual:**
  - Switch to terminal: run `curl http://localhost:8000/api/aws/status` showing real-time JSON response.
  - Show the `Dockerfile` and `deploy/cloudformation.yaml`.
  - Display the team credentials: **Team choco (`PYY34M`) — Ganesh Nair & Arjit Ujjawal**.
- **Audio / Narration:**
  > "For the Ship It track, Rivet is packaged as a unified multi-stage container running React 19 and FastAPI on port 8000, deployable in one command to AWS App Runner or ECS, with CloudFormation provisioning our S3 audit ledger.
  > Rivet gives e-commerce sellers the speed of generative advertising with the rigor of cryptographic verification. Built for the WeMakeDevs x AWS Hackathon 2026 by Team choco. Thank you."

---

## Recording Tips for the Team

1. **Resolution:** 1080p (1920×1080) at 60fps.
2. **Audio:** Crisp microphone, clean speaking cadence (130-150 words per minute).
3. **Cursor Movement:** Smooth and deliberate. Hover over `A01` when it turns red to draw the viewer's eye directly to the failure evidence.
4. **Pacing:** Give the "Tampered" state transition 5 full seconds on screen so judges see the red border, the `FAIL: MISMATCH` badge, and the locked `Export blocked` button.
