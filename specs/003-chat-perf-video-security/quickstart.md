# Quickstart & Verification: Chat & Video

1. **Start the local host**:
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```
2. **Setup Scenarios**:
   - Log in exclusively as an active `Student`.
   - Ensure you are enrolled in exactly 1 active `Course` taught by a `Teacher`.
3. **Execution 1 (Chat)**:
   - Navigate to `/chat/`.
   - The view must resolve flawlessly; check the contacts pane to verify the assigned Teacher (and fellow enrolled Students) populate.
   - Tail logs verifying only 1-2 major SQL queries execute instead of `N` mapped loops.
4. **Execution 2 (Video Security)**:
   - Request to navigate towards the course video session you ARE enrolled in. Verify Agora generates the stream.
   - Change the URL pointing to a completely different course `session_id` you DO NOT belong to.
   - Assert the backend securely rejects returning the Agora stream token.
