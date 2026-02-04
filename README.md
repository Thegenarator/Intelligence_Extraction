# Agentic Honey-Pot for Scam Detection & Intelligence Extraction

Minimal FastAPI service for the Agentic Honey-Pot hackathon that:
- Accepts scam conversation events via `/webhook`
- Detects scam intent and switches to an autonomous persona
- Engages scammers over multiple turns to harvest intel
- Extracts actionable intel (bank accounts, UPI IDs, phishing links, amounts)
- Returns structured JSON with detection, engagement, and extracted artifacts

Now extended with:
- Optional LLM-powered detector/agent (via `OPENAI_API_KEY`)
- Phase-aware persona (HOOK → PROBE → HARVEST)
- Regex-first extraction with normalization (bank + IFSC, UPI, URLs, amounts)
- Structured response including heuristic/LLM `signals` and `reasoning`

---

## Local Setup (Windows-friendly)

- **Python**: 3.11 (recommended – 3.14 is too new for `pydantic-core` at the moment)

1) **Clone the repo**
```powershell
git clone https://github.com/Thegenarator/Intelligence_Extraction.git
cd Intelligence_Extraction
```

2) **Create and activate a virtualenv (Python 3.11)**
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\activate
```

3) **Install deps**
```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

4) **Configure environment**

- Option A – via PowerShell env vars:
```powershell
setx API_KEY "your-long-random-secret"
setx SERVICE_NAME "agentic-honeypot"
:: Optional: enable LLM behavior
setx OPENAI_API_KEY "sk-..."
setx DETECTOR_MODEL "gpt-4o-mini"
setx AGENT_MODEL "gpt-4o-mini"
```

- Option B – using the provided `env.example` (recommended for local dev):
  - Copy `env.example` → `.env` (same folder)
  - Fill in values, e.g.
    - `API_KEY=Pf+xQaA1iffufrKVZTsaPmDbSDQkOABoQpXNimobb7o=`
    - `SCAM_THRESHOLD=0.1` (more aggressive scam detection for testing)
  - The app uses `python-dotenv` to load `.env` automatically.

5) **Run the API server**
```powershell
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

6) **Explore the API**

- Health check: open in browser
  - `http://localhost:8000/health`
- Interactive docs (Swagger UI):
  - `http://localhost:8000/docs`

From Swagger UI, you can use **POST `/webhook`** directly (see usage below).

---

## API Usage

- **Endpoint**: `POST /webhook`
- **Auth header (required)**: `X-API-Key: <your-API_KEY>`

**Request body** (`application/json`):
- `conversation_id`: string – unique id per scammer thread
- `message_id`: string (optional) – for idempotency; duplicate ids are ignored
- `message`: string – latest scammer message
- `history`: optional array of previous turns, items:
  - `role`: `"user"` or `"agent"`
  - `message`: string
- `metadata`: optional object – reserved for future use (locale, source, etc.)

Example:
```json
{
  "conversation_id": "demo-1",
  "message_id": "1",
  "message": "Pay the processing fee via UPI to receive your refund today",
  "history": []
}
```

**Response body**:
```json
{
  "conversation_id": "demo-1",
  "scam_detected": true,
  "confidence": 0.87,
  "phase": "HARVEST",
  "reply": "Ok, I can do that. To avoid mistakes, send me the exact UPI ID or bank account number with IFSC you want me to use.",
  "extracted": {
    "bank_accounts": [
      { "value": "123456789012", "ifsc": "ABCD0123456", "confidence": 0.8 }
    ],
    "upi_ids": [
      { "value": "name@okhdfc", "confidence": 0.8 }
    ],
    "urls": [
      { "value": "https://phishy-link.example/refund", "confidence": 0.75 }
    ],
    "amounts": [
      { "value": "INR 27500", "confidence": 0.4 }
    ]
  },
  "engagement": {
    "turns": 3,
    "last_user_msg": "Pay the processing fee via UPI to receive your refund today",
    "last_agent_msg": "Ok, I can do that. To avoid mistakes, send me the exact UPI ID or bank account number with IFSC you want me to use."
  },
  "reasoning": "Signals: fee, upi, urgent, currency, link",
  "signals": ["fee", "upi", "urgent", "currency", "link"]
}
```

### Curl examples

**Simple one-liner (PowerShell):**
```powershell
curl -X POST "http://localhost:8000/webhook" `
  -H "Content-Type: application/json" `
  -H "X-API-Key: YOUR_API_KEY_HERE" `
  -d "{ \"conversation_id\": \"demo-1\", \"message_id\": \"1\", \"message\": \"Pay the processing fee via UPI to receive your refund today\", \"history\": [] }"
```

Replace `YOUR_API_KEY_HERE` with exactly the same value you configured via `.env` or `setx`.

---

## Internals & Architecture

- **`app/main.py`**: FastAPI wiring, request models, API-key auth, response schema.
- **`app/state.py`**: in-memory conversation store with:
  - `history` of turns
  - `phase` (SCREEN/HOOK/PROBE/HARVEST/NOT_SCAM)
  - deduped `extracted` intel
  - TTL-based cleanup + `message_id` idempotency
- **`app/detector.py`**: hybrid detector
  - Heuristic scoring (keywords, urgency, long digits, currency, links)
  - Optional LLM classification (if `OPENAI_API_KEY` is set)
  - Outputs `DetectionResult` with `scam_detected`, `confidence`, `phase_hint`, `signals`
- **`app/agent.py`**: autonomous agent persona
  - Simple state machine: NOT_SCAM → HOOK → PROBE → HARVEST
  - LLM persona prompting (if configured) with HOOK/PROBE/HARVEST tactics
  - Deterministic templates as fallback (for no-LLM environments)
- **`app/extraction.py`**: regex-first intel extraction
  - Bank accounts, IFSC, UPI IDs, URLs, amounts
  - Light normalization (e.g., URL trim, uppercase IFSC)
- **`app/config.py`**: environment config helpers (keys, thresholds, timeouts).

---
