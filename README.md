# BugLens AI

A local, offline bug detection tool powered by per-language TF-IDF + ML models.
Supports **Java**, **C**, **C++**, and **Python** source code analysis.

---

## Setup

```bash
python -m venv venv && pip install -r requirements.txt
```

## Train Models

```bash
python generate_data.py && python train_model.py
```

## Run

```bash
python app.py
```

Then open [http://localhost:5000](http://localhost:5000)

---

## API

| Method | Endpoint    | Description                        |
|--------|-------------|------------------------------------|
| POST   | `/analyze`  | Analyze a code snippet for bugs    |
| GET    | `/health`   | Server and model health check      |
| GET    | `/languages`| List supported languages           |

### POST `/analyze`

**Request**
```json
{ "code": "...", "language": "java" }
```

**Response**
```json
{
  "is_bug": true,
  "confidence": 0.91,
  "bug_type": "Null Dereference",
  "line_number": 4,
  "description": "Potential null pointer dereference detected.",
  "fixed_code": "...",
  "complexity_score": 12,
  "quality_grade": "B",
  "language": "java"
}
```

## Notes

- All processing is **100% local** — no external API calls.
- Models are stored as `.pkl` files in `data/` after training.
- Input is capped at **10 000 characters** per request.
