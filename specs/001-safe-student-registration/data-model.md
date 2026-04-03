# Data Model: Soft Delete Entities

## Entities & Models

### `SoftDeleteModel` (Abstract Base Class)
- **Concept**: A base model for critical application entities that prevents physical deletion.
- **Fields**:
  - `is_deleted` (Boolean, default: `False`): Flag denoting deletion state.
- **Managers**:
  - `objects` (Custom Manager): Overrides `get_queryset()` to append `.filter(is_deleted=False)`.
  - `all_objects` (Base Manager): Retains standard `.all()` capability without filters.
- **Methods**:
  - `delete()`: Overridden to update `is_deleted = True` instead of `super().delete()`.
  
### App Profile Models (`Teacher`, `Student`, `Supervisor`, `Manager`)
- **Relationship**: Inherits from `SoftDeleteModel`.
- **Constraint/Relationship**: Has a One-to-One or Foreign Key relationship to the core Django `User` model.
- **State Transition (`delete()` execution)**:
  1. Sets `self.is_deleted = True`.
  2. Traverses to the linked `User` account: `self.user.is_active = False`.
  3. `self.save()` and `self.user.save()`.
  4. Optionally ends any active sessions if supported by the app's token/session engine.
  
## Data Validation
- The `admin_panel` view requires capturing the dynamically generated `<username>` and `<password>` strings in RAM directly after atomic commit to render the Django message.
