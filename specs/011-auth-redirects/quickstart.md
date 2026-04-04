# Phase 1: Quickstart / Testing

To verify this implementation locally:

1. Start the server: `python manage.py runserver`
2. Open an incognito browser window.
3. Access `http://localhost:8000/dashboard/`. You should seamlessly be redirected to `http://localhost:8000/management/login/?next=/dashboard/`.
4. Log in with a valid account on that form.
5. Manually navigate back to `http://localhost:8000/management/login/`.
6. You should automatically be redirected to `http://localhost:8000/dashboard/`.
