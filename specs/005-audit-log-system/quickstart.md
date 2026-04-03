# Quickstart: Audit Log System

Follow these steps to set up and verify the audit logging system.

## 1. Environment Setup

Add the required dependency:
```bash
pip install django-simple-history
```
Ensure it's added to `requirements.txt`.

## 2. Django Configuration

Update `academy_project/settings.py`:
```python
INSTALLED_APPS = [
    ...
    'simple_history',
    ...
]

MIDDLEWARE = [
    ...
    'simple_history.middleware.HistoryRequestMiddleware',
    ...
]
```

## 3. Database Migration

Run migrations to create the historical tables:
```bash
python manage.py makemigrations
python manage.py migrate
```

## 4. Verification

### Individual Object History
1. Log into the administrative dashboard.
2. Navigate to any tracked object (e.g., a Student).
3. Click the **"History"** button in the top-right corner.
4. Verify you can see past changes, the user who made them, and the field diffs.

### Tracking Soft Deletes
1. Delete a student from the dashboard.
2. Check the "History" for that student.
3. Verify an entry exists with `is_deleted` set to `True`.

## 5. Global History (Superuser Only)

A global view of all history entries can be accessed by registering `Historical` models in the admin sidebar.
1. Superusers can filter by model type or date to see cross-platform activity.
