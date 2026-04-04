# Phase 1: Quickstart / Testing

To verify the UI/UX overhauls locally:

1. **Start the server**: Run `python manage.py runserver`.
2. **Clear Cache**: Perform a hard refresh (`Ctrl + Shift + R`) to ensure the new global CSS loads.
3. **Verify Layouts**:
   - Navigate to `/` (Landing Page) and resize from 320px to 1080px to check mobile responsiveness.
   - Navigate to login pages and trigger an invalid form submission to test pseudo-class visual feedback.
4. **Dashboard Views**: Log in as different user roles and check `profile.html` empty states.
5. **Chat Interface**: Open two windows, emulate a chat conversation, and verify message bubble alignments, color contrast, and async spinners.
6. **Admin Theme**: Check `/admin/` and ensure the `django-unfold` configuration matches the new color scheme and sidebar hierarchy.
