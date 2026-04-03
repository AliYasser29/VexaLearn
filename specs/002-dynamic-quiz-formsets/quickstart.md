# Quickstart & Verification: Dynamic Quiz Formsets

1. **Start the localized server**:
   ```bash
   python manage.py runserver
   ```
2. **Setup**:
   - Create a quiz module via the administration panel if none exists.
3. **Execution**:
   - Access the quiz view as a Teacher.
   - Click "Add Question".
   - You should see the base Question configuration and initially loaded empty choices.
4. **Validating DOM interactions**:
   - Click "Add another choice" -> Validates instantaneous appending to screen.
   - Click "Remove choice" on an appended choice -> Option vanishes.
5. **Validating integrity logic**:
   - Populate only 1 Choice. Submit form. Output: Validation error triggering.
   - Populate 4 Choices. Select multiple correct choices. Submit. Output: Validation error triggering.
   - Populate minimum 2 choices. Select 1 correct mark. Submit. Output: Validation succeeds, records hit DB.
