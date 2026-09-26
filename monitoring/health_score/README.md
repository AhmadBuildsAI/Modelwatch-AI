# Health Score

Composite score combining:
- 25% data quality
- 30% data drift
- 15% prediction drift
- 30% performance

Range: 0-100. Status: HEALTHY (≥80), WARNING (60-79), CRITICAL (<60).

Implementation: `backend/app/services/health_service.py`