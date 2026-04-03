# Data Model & Schema: Dynamic Quiz Formsets

## Entites & Forms

### `QuestionForm`
- **Fields**: standard fields mapped to `Question`.
- **Role**: Validates parent question structure.

### `Choice` Model (existing)
- **Relationships**: Many-to-One linked to `Question`.
- **Fields**: `text`, `is_correct`.

### `ChoiceFormSet` (`inlineformset_factory`)
- **Base class**: Custom `BaseChoiceFormSet` inheriting `BaseInlineFormSet`.
- **Validation**:
  - Overrides `clean()`:
    1. Checks if total valid forms (non-deleted, populated choices) `>= 2`.
    2. Maps validations tracking `is_correct` flags across sub-forms to guarantee exactly `1` correctly flagged true option.

## Expected Database Operations

- Inserting a multi-form payload will atomically:
  1. Save `Question`.
  2. Iterate children and save `Choice` lines associated with the primary key of `Question`.
