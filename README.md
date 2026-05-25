# Helsinki-NLP Translation API

A production-ready REST API for translating English text into French, German, 
and Spanish using MarianMT transformer models from Helsinki-NLP's OPUS-MT family.


---

## Architecture

Request → FastAPI → Safeguards → Translator → MarianMT (thread pool) → Response
↓                           ↓
HTTPException              HuggingFace cache
(422/400)                 (/.cache/huggingface)

**Key design decisions:**

- **Lazy loading with caching** — models load on first request per language and 
  are cached in memory for the application lifetime. Startup is instant.
- **Thread pool inference** — CPU-bound model inference runs via 
  `run_in_executor`, keeping the async event loop free for concurrent requests.
- **Separated concerns** — translation logic, validation, safeguarding, and 
  monitoring each live in dedicated modules. Changes to one do not touch others.
- **Baked model weights** — weights are downloaded at Docker build time. 
  Containers have zero internet dependency at runtime.

---

## Stack

- **Framework:** FastAPI + Uvicorn
- **Models:** Helsinki-NLP OPUS-MT (MarianMT architecture via HuggingFace)
- **Validation:** Pydantic v2
- **Monitoring:** Prometheus via prometheus-fastapi-instrumentator
- **Evaluation:** sacrebleu (BLEU score)
- **Containerisation:** Docker + Docker Compose
- **CI:** GitHub Actions

---

## Running The API

### Locally

```bash
git clone https://github.com/StanSouthwick/Helsinki-NLP-Translate.git
cd Helsinki-NLP-Translate

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Via Docker

```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000`.

---

## API Endpoints

### `GET /health`
Liveness check. Used by load balancers and orchestrators to verify the 
service is running.

```bash
curl http://localhost:8000/health
# {"status":"healthy"}
```

---

### `GET /languages`
Returns all supported language codes and their model identifiers.

```bash
curl http://localhost:8000/languages
# {
#   "supported_languages": {
#     "fr": "Helsinki-NLP/opus-mt-en-fr",
#     "de": "Helsinki-NLP/opus-mt-en-de",
#     "es": "Helsinki-NLP/opus-mt-en-es"
#   }
# }
```

---

### `POST /translate`
Translates English text into the specified target language.

```bash
curl -X POST http://localhost:8000/translate \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, how are you?", "target_language": "fr"}'

# {
#   "original_text": "Hello, how are you?",
#   "translated_text": "Bonjour, comment allez-vous ?",
#   "target_language": "fr",
#   "model_used": "Helsinki-NLP/opus-mt-en-fr"
# }
```

---

### `POST /evaluate`
Scores a translation against a human reference using BLEU score (0-1).
Used for continuous quality evaluation.

```bash
curl -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "source_text": "Hello, how are you?",
    "translated_text": "Bonjour, comment allez-vous ?",
    "reference_text": "Bonjour, comment allez-vous ?"
  }'

# {
#   "bleu_score": 1.0,
#   "interpretation": "Excellent — very close to human translation quality"
# }
```

---

### `GET /metrics`
Prometheus metrics endpoint. Scraped automatically every 15 seconds by a 
Prometheus server. Exposes request count, latency histograms, and 
requests in progress per endpoint.

---

## Running Tests

```bash
pytest tests/ -v
```

Tests use FastAPI's TestClient with the translation model mocked — no model 
download required. Full test suite runs in under 2 seconds.

---

## Research Questions

### Q1 — Multiple language support ✅ Implemented
The `SUPPORTED_LANGUAGES` dictionary maps language codes to HuggingFace model 
strings following the `Helsinki-NLP/opus-mt-en-{target}` naming convention. 
Adding a new language is a single line change in `translator.py` — no other 
file changes required. The architecture is open to extension without 
modification.

### Q2 — Continuous evaluation ✅ Implemented
The `/evaluate` endpoint accepts a machine translation and a human reference 
and returns a BLEU score. In production this would be integrated into a 
monitoring pipeline — a sample of translations reviewed by human annotators 
periodically, scored against their corrections, and tracked over time. A score 
drop below a defined threshold would trigger an alert.

### Q3 — Concurrent requests ✅ Implemented
Model inference runs via `asyncio.run_in_executor` in a thread pool. The async 
event loop remains free to accept and route new requests while inference runs 
in a separate thread. Models are shared across all requests via the cached 
instance in `app.state`.

### Q4 — Production monitoring ✅ Implemented
Prometheus metrics are exposed at `/metrics` via 
`prometheus-fastapi-instrumentator`. Metrics include request count by endpoint 
and status code, request latency histograms (enabling p50/p95/p99 
calculations), and requests currently in progress. In production these feed 
Grafana dashboards with alerts on p99 latency and error rate thresholds.

### Q5 — User feedback loop 📋 Documented
A `/feedback` endpoint would accept corrected translations from users, storing 
them in a database alongside the original input and model output. Accumulated 
corrections form a fine-tuning dataset. A scheduled retraining pipeline — 
triggered via CI/CD when the dataset reaches a defined size threshold — would 
produce an updated model, evaluated against a held-out test set before 
promotion to production.

### Q6 — Input and output safeguarding ✅ Implemented
`safeguards.py` validates all inputs before they reach the model and all 
outputs before they reach the caller. Input checks include empty string 
detection, repetition analysis, and regex-based prompt injection detection. 
Output checks catch empty or malformed model responses. Error messages for 
rejected inputs are deliberately vague to prevent attackers from enumerating 
detection patterns.

