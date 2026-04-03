# Research: Comprehensive Table Views

## Decision 1: Table Implementation Strategy
**Decision**: Use native Django Admin List Views augmented by Unfold's filtering and display capabilities.
**Rationale**: Django Admin inherently provides server-side pagination, search functionality (`search_fields`), and list displays (`list_display`). Unfold naturally reskins these into a modern grid. Reinventing this with a custom view and a separate frontend table library (like DataTables) is unnecessary and violates the "DRY" principle, given the existing Admin UI.
**Alternatives considered**: 
- Creating custom views with `django-tables2`. Rejected as it duplicates effort when the Admin interface is already the primary data interaction point and handles pagination/search natively.

## Decision 2: Advanced Filtering Integration
**Decision**: Utilize `django-filter` within custom Admin filters, or rely on Unfold's native `unfold.contrib.filters` combined with standard Django Admin `list_filter`.
**Rationale**: The prompt explicitly mentions `'django-filter'`. However, standard Django Admin filters combined with Unfold provide robust relational filtering out of the box (e.g., `list_filter = ('academic_year', 'country')`). We will research if `django-filter` can be natively injected into Unfold's admin interface or if we should implement custom `admin.SimpleListFilter` classes that mimic advanced filtering.
*Correction*: Unfold has built-in support for advanced filters. We will implement robust `list_filter` configurations in `core/admin.py` for Student and Teacher models to meet the requirement without necessarily adding an entirely new filtering UI paradigm if the native one suffices.

## Decision 3: Displaying Relational Data
**Decision**: Use custom methods on the `ModelAdmin` classes to aggregate and display relational data (e.g., list of courses, active enrollments count).
**Rationale**: Django Admin's `list_display` accepts callable methods. We can create methods like `get_active_courses` that return a comma-separated string or an HTML snippet (using `format_html`) to summarize data without requiring the user to click into the detail view.
**Alternatives considered**: Denormalizing data into the main table. Rejected as it violates data integrity principles.

## Research Tasks (Completed)
- [x] Verify Django Admin's native pagination and search capabilities. (Confirmed: `list_per_page` and `search_fields`).
- [x] Check `django-unfold` documentation for custom list views and filtering. (Confirmed: Unfold fully supports standard Django Admin features and provides enhanced filter UI).
