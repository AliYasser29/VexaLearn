# Research: Excel Data Export

## Decision 1: Integration with Unfold Admin
**Decision**: Use `unfold.contrib.import_export.ModelAdmin` in combination with standard `ImportExportModelAdmin` or `ExportActionMixin` from `django-import-export`.
**Rationale**: `django-unfold` explicitly provides an integration path (`unfold.contrib.import_export`) to ensure the export/import buttons render correctly within the Unfold UI, maintaining the established design system.
**Alternatives considered**: Standard `django-import-export` mixins without Unfold integration. Rejected because the buttons would either not appear or break the UI layout.

## Decision 2: Human-Readable Foreign Keys & Filtering
**Decision**: Create custom `ModelResource` classes for `Student`, `Teacher`, `Enrollment`, and `Attendance`. Use `dehydrate_fieldname` methods or `Field(attribute='...', column_name='...')` to resolve related data (e.g., `student.name` instead of `student_id`).
**Rationale**: `django-import-export` natively supports resolving relationships via the `dehydrate` hook or field definitions. Furthermore, `ExportActionMixin` automatically respects the active filters and selections made in the Django Admin list view.
**Alternatives considered**: Overriding the export querysets manually. Rejected because `django-import-export` inherently respects the `ModelAdmin`'s `get_export_queryset` and active filters.

## Decision 3: Role-Based Access Control (RBAC)
**Decision**: Rely on Django Admin's native permission system (`has_export_permission`).
**Rationale**: Django Admin and `django-import-export` check user permissions before displaying the export action. Superusers and Managers (with assigned permissions) will naturally have access, while unauthorized roles will not see the button.
**Alternatives considered**: Custom permission mixins. Not needed if native Django model permissions are configured correctly for the Manager role.

## Research Tasks (Completed)
- [x] Verify `django-import-export` and `unfold` compatibility. (Confirmed via Unfold documentation).
- [x] Determine mechanism for human-readable relational data. (Confirmed: `ModelResource` with `dehydrate_` methods).
- [x] Verify export action respects active list filters. (Confirmed: `ExportActionMixin` uses the changelist's queryset).
