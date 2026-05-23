# Quickstart: Fix Template Inheritance and Missing CSS

## Verification Steps

### 1. Tag Ordering Check
Run the following command to verify that `{% extends %}` is always on Line 1 for all templates that use it:
```bash
grep -rn "{% extends" core/templates/ quiz/templates/ | grep -v ":1:"
```
*Expected Output*: No results (empty).

### 2. Global CSS Check
Open any page that extends `base.html` (e.g., the landing page or profile page) and inspect the HTML source.
- Verify that `<link rel="stylesheet" href="/static/css/global_ux.css">` (or similar depending on your `STATIC_URL`) is present in the `<head>`.
- Verify that the page reflects the intended styling (Cairo font, indigo accents, etc.).

### 3. Template Syntax Check
Run Django's built-in system check to ensure no template syntax errors were introduced:
```bash
python manage.py check
```

## Troubleshooting
- **Missing Styles**: If the CSS is still missing, ensure that `templates/base.html` is being correctly loaded and that `STATIC_ROOT` and `STATIC_URL` are properly configured in `settings.py`.
- **Recursion Error**: If you encounter a recursion error, check `templates/unfold/layouts/base.html` and ensure it's not extending itself.
