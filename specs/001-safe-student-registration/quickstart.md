# Quickstart: Testing Safe Student Registration & Soft Deletes

## Setup and Migrations
After implementing the changes, generate and apply migrations for the `core` app since new schema paths (`is_deleted` boolean) have been injected into existing profile models:
```bash
python manage.py makemigrations core
python manage.py migrate
```

## Testing Scenario: Registration Backup
1. Spin up the local development server: `python manage.py runserver`
2. Log into the VexaLearn admin portal as a Manager or Superuser.
3. Navigate to the `admin_panel` registration flow and submit a new `Student` creation request.
4. Assure that upon completion, the top of the browser renders a Django success message containing the plaintext credentials (e.g. `Generated credentials: username123 / P@ssw0rd!`).
5. Terminate your local STMP dummy server (if any) and verify the admin is still safely provided the credentials in the UI.

## Testing Scenario: Safe Deletions
1. In the system, locate an existing active `Student` or `Teacher` profile.
2. Attempt to delete them using the standard system view functionality or via shell.
3. Access Django shell (`python manage.py shell`) and verify:
   ```python
   # Object should be hidden from normal manager
   Student.objects.filter(id=<deleted_id>).exists() == False
   
   # Object should still persist physically
   Student.all_objects.filter(id=<deleted_id>).exists() == True
   
   # Bound User account must be inactive
   User.objects.get(id=<linked_user_id>).is_active == False
   ```
4. Confirm attempting to login with that user's credentials now appropriately fails.
