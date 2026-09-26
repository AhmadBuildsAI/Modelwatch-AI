# Drift Detection

Per-feature drift metrics:
- **PSI** (Population Stability Index): <0.1 LOW, 0.1-0.25 MEDIUM, >0.25 HIGH
- **KS Test**: p<0.05 → drift
- **JS Divergence**: <0.1 LOW, 0.1-0.2 MEDIUM, >0.2 HIGH

Implementation: `backend/app/services/drift_service.py`