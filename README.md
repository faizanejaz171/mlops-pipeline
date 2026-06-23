# CV Data Pipeline

Automated data ingestion, cleaning, annotation, and CVAT upload pipeline.

## Quick Start (Annotators)

### 1. Clone and setup config
```bash
git clone <repo-url>
cd cv-pipeline-data-pipeline
cp configs/config.template.yaml configs/config.yaml
# Edit config.yaml with your GCP path, dates, camera IDs
```

### 2. Add GCP credentials
```bash
# Place service-account.json in the project root (never commit this)
cp /path/to/service-account.json ./service-account.json
```

### 3. Run with Docker
```bash
docker compose up
```
The wizard will start in your terminal. Follow the prompts.

---

## Pipeline Stages

| Stage | What happens |
|-------|-------------|
| Config load | Reads `configs/config.yaml`, pauses for edits if new |
| GCP scan | Lists videos from bucket by camera/date/hour |
| Download | Pulls selected videos locally |
| Extraction | FFmpeg extracts frames/clips at configured FPS |
| Cleaning | MD5 dedup → blur removal → YOLO/DINO filtering → pHash sampling |
| Annotation | SFTP to Beast (10.20.30.15) → SAM3 auto-annotation |
| Verification | Upload to CVAT (10.20.30.14:2026) for human review |

---

## Development

### Run tests locally
```bash
pip install pytest pytest-cov
pytest tests/ -v
```

### Run linting
```bash
pip install flake8
flake8 src/ tests/ --max-line-length=120
```

---

## CI/CD

Every push to `main` or `develop` triggers:
1. Flake8 lint check
2. Unit tests (no GPU required)
3. Config template validation
4. Docker build check

See `.github/workflows/ci.yaml` for details.
# mlops-pipeline
