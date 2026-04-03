# Data Model: Audit Log System

This feature introduces historical tracking for all primary business entities. Instead of a single "Audit Log" table, we utilize `django-simple-history` which generates "Historical" shadow tables for each model to provide full field-level diffs.

## Tracked Entities

The following models will be augmented with `history = HistoricalRecords(inherit=True)` to track all state changes:

### `Core` App Models
- **`SoftDeleteModel` (Abstract Base Class)**: Inherits `HistoricalRecords` to provide history for all derived models.
  - **Inherited by**: `Teacher`, `Supervisor`, `Manager`, `Student`, `Course`, `Enrollment`, `Academy`.
- **`Country`, `EducationType`, `AcademicYear`, `Subject`**: Will have individual `HistoricalRecords()` added to track configuration changes.

### `Quiz` App Models
- **`Quiz`, `Question`, `Choice`, `QuizAttempt`**: Will have individual `HistoricalRecords()` added.

## Historical Table Structure

Each tracked model (e.g., `Student`) will have a corresponding historical table (e.g., `HistoricalStudent`) with the following schema:

| Field | Type | Description |
|-------|------|-------------|
| `history_id` | AutoField | Primary key for the history record. |
| `history_date` | DateTime | Timestamp when the change occurred. |
| `history_user` | ForeignKey(User) | The superuser/admin who performed the action. |
| `history_type` | Char(1) | `+` for Created, `~` for Updated, `-` for Deleted. |
| `[Original Fields]` | (Various) | A snapshot of all fields from the original model at that point in time. |

## M2M Relationship Tracking

`ManyToMany` relationships (e.g., `Teacher.subjects`) are **not** tracked by default. If tracking is required for these fields, we will implement custom signals to record changes in a generic `AuditLogEntry` or utilize `m2m_changed` signals to update the model's history record.

## Soft Delete Integration

When a model is "Soft Deleted" via `SoftDeleteModel.delete()`:
1. `is_deleted` is set to `True`.
2. `save()` is called.
3. `django-simple-history` records an **Update (`~`)** event.
4. The history record clearly shows the transition of `is_deleted` from `False` to `True`.
