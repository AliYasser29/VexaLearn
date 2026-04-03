# Quickstart: Excel Data Export

Follow these steps to configure and test the export functionality.

## 1. Environment Setup

Ensure `django-import-export` is installed and configured in `academy_project/settings.py`.
```python
INSTALLED_APPS = [
    ...
    'import_export',
    ...
]
```

## 2. Verification

### Exporting User Records
1. Log into the administrative dashboard as a Superuser or Manager.
2. Navigate to "الطلاب" (Students).
3. Select a few students using the checkboxes (or leave unchecked to export all).
4. Click the **"Export"** (تصدير) button at the top right of the Unfold interface.
5. Select `.xlsx` as the format and confirm.
6. Open the downloaded Excel file and verify that the country and academic year are displayed as names, not IDs.

### Exporting Filtered Operational Data
1. Navigate to "سجلات الحضور" (Attendances).
2. Use the right sidebar to filter attendances by a specific date or course.
3. Click **"Export"**.
4. Verify the downloaded file only contains the filtered records, and that the student name and status ("حضور"/"غياب") are readable.

### Access Control Check
1. Log in with a standard Teacher account (if they have limited admin access).
2. Navigate to an allowed list view.
3. Verify that the "Export" button is NOT visible.
