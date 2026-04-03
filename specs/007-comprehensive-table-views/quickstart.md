# Quickstart: Comprehensive Table Views

Follow these steps to verify the implementation of the new table views.

## 1. Environment Setup

Ensure `django-filter` is installed (if explicitly required for custom API views later, though Admin handles most needs natively):
```bash
pip install django-filter
```

Update `academy_project/settings.py` if needed:
```python
INSTALLED_APPS = [
    ...
    'django_filters',
    ...
]
```

## 2. Verification

### Student Grid View
1. Log into the administrative dashboard.
2. Navigate to "الطلاب" (Students).
3. Verify the table columns: Name, Academic Year, Country, Parent Phone, and a new column summarizing "Active Courses".
4. Test the **Search Bar**: Search by a student's name or phone number.
5. Test the **Filters** (Right Sidebar): Apply multiple filters (e.g., specific Country and Academic Year) and ensure the results update correctly.
6. Verify **Pagination**: Ensure the page loads quickly and you can navigate between pages of results.

### Teacher Grid View
1. Navigate to "المعلمون" (Teachers).
2. Verify the table columns: Name, Subjects, Phone, Email, and a new column summarizing "Active Students" or workload.
3. Test Search, Filters, and Pagination similarly to the Student view.