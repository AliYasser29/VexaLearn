# Research: Audit Log System

## Decision 1: Tracking Package Choice
**Decision**: Use `django-simple-history` for model-level auditing.
**Rationale**: 
- It tracks all field changes (before/after).
- It stores the user who made the change automatically via middleware.
- it is highly customizable and integrates well with Django Admin.
- It supports tracking "Soft Deletes" as updates to the `is_deleted` field.
**Alternatives considered**: 
- **Django LogEntry**: Too limited; only tracks admin actions and doesn't store the full state of the object before/after.
- **Custom Signal-based system**: High maintenance; reinventing the wheel when `django-simple-history` is industry standard.

## Decision 2: Integration with SoftDeleteModel
**Decision**: Configure `django-simple-history` on all models inheriting from `SoftDeleteModel`.
**Rationale**: Since `SoftDeleteModel.delete()` calls `self.save()`, `django-simple-history` will record this as an update (`~`) where `is_deleted` changes from `False` to `True`. This fulfills the requirement to track soft deletions.
**Alternatives considered**: Overriding `SimpleHistoryManager` to mark history as `-` (deleted) even on soft delete. Rejected for now to keep implementation simple and technically accurate (it *is* an update in the DB).

## Decision 3: Admin Dashboard Integration (Unfold)
**Decision**: Use `SimpleHistoryAdmin` mixin from `django-simple-history` and register it with `unfold.admin.ModelAdmin`.
**Rationale**: Unfold is compatible with standard Django Admin mixins. This provides a "History" button in the admin interface that shows the audit log for each specific object. A global "Audit Log" view can also be created by registering the `Historical` models directly.
**Alternatives considered**: Custom Unfold dashboard widgets. This can be added as a secondary improvement (P2/P3).

## Decision 4: Global Audit View
**Decision**: Create a dedicated "Global Audit Log" section in the Unfold sidebar that aggregates historical records across all tracked models.
**Rationale**: Meets the requirement for superusers to "see all database changes ... across the platform" in one place, rather than just per-object.
**Alternatives considered**: Only per-object history. Rejected as it doesn't meet the "across the platform" requirement.

## Research Tasks (Completed)
- [x] Verify `django-simple-history` compatibility with Django 5.0.
- [x] Confirm `SoftDeleteModel` implementation in `core/models.py`.
- [x] Check `django-unfold` documentation for custom sidebar/dashboard items.
