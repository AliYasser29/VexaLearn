# Quickstart: Performance Optimization

## 1. Environment Setup

Ensure your local development environment has the Django Debug Toolbar installed to verify query reductions (optional but recommended):
```bash
pip install django-debug-toolbar
```

## 2. Configuration Changes

Update your `academy_project/settings.py` (or `.env`) to enable WhiteNoise caching:
```python
WHITENOISE_MAX_AGE = 31536000  # 1 year caching for static files
```

## 3. Verification

### N+1 Query Reduction
1. Load the Supervisor Dashboard.
2. Observe the SQL queries count in Django Debug Toolbar.
3. The query count should remain flat (e.g., under 15) regardless of the number of students or enrollments displayed.

### Static & Media Caching
1. Open the browser's Network Tab.
2. Reload the page twice.
3. Verify that static files (CSS/JS) return `304 Not Modified` or `(disk cache)` and feature a `Cache-Control: max-age=31536000` header.
