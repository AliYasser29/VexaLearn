# Conceptual Data Model: Template Inheritance Tree

## Overview
This document maps the hierarchy of templates and their inheritance relationships to ensure a consistent UI across the application.

## Template Hierarchy

### 1. Global Base Layout
- **Path**: `templates/base.html`
- **Extends**: `unfold/layouts/base.html` (from `django-unfold`)
- **Responsibility**: Provides the main application shell, sidebar navigation, Cairo font, and links to `global_ux.css`.

### 2. Feature-Specific Bases
- **Admin Layout**: `templates/admin/base_site.html` (Extends `unfold/layouts/base.html`)
- **Unfold Layout Override**: `templates/unfold/layouts/base.html` (Extends `unfold/layouts/base.html`)

### 3. Application Templates (Extending `base.html`)
These templates must follow strict tag ordering:
1. `{% extends "base.html" %}`
2. `{% load static %}`

- `core/templates/core/admin_panel.html`
- `core/templates/core/landing_page.html`
- `core/templates/core/profile.html`
- `core/templates/core/supervisor_dashboard.html`

## Validation Rules
- **Rule 1 (Inheritance)**: If a template uses inheritance, `{% extends %}` must be the very first line (Line 1).
- **Rule 2 (Static Assets)**: `{% load static %}` must be present if `{% static %}` is used, and should be placed immediately after `{% extends %}`.
- **Rule 3 (Global Styles)**: The `extrahead` block in `templates/base.html` must include the link to `css/global_ux.css`.
