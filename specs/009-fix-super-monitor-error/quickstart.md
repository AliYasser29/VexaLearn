# Quickstart: Fix Super Monitor Error

## Setup

Since this is a template-only fix, standard Django setup procedures apply.

1. Ensure the virtual environment is active.
2. Ensure you have the necessary dependencies installed (`pip install -r requirements.txt`).

## Running the Application

1. Start the Django development server:
   ```bash
   python manage.py runserver
   ```
2. Navigate to `/super-monitor/` (or the corresponding URL pattern) in your browser as a logged-in superuser.

## Testing

1. Test using the existing pytest suite:
   ```bash
   pytest
   ```
2. Verify that there are no longer 500 errors on the page when rendering the `universal_chat_monitor.html` template.
