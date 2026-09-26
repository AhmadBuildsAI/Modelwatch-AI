# Data Quality

Checks production data for:
- Null rate
- Outlier rate (>3σ)
- Range violations vs training
- Unexpected categories

Implementation: `backend/app/services/quality_service.py`