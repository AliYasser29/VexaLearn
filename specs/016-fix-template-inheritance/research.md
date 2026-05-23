# Research: Fix Template Inheritance and Missing CSS

## Overview
The goal is to fix broken template inheritance and restore global CSS by enforcing correct tag ordering and verifying static file inclusion in the base template.

## Findings

### 1. Template Tag Ordering
- **Observation**: A scan of `core/templates/` and `quiz/templates/` shows that most templates using inheritance currently have `{% extends %}` on Line 1. However, some templates might have been broken in previous refactors or might have leading whitespace/comments that disrupt inheritance.
- **Enforcement**: We will implement a script/process to ensure that if a template uses `{% extends %}`, it is the absolute first line.

### 2. Static File Loading
- **Observation**: `{% load static %}` should always follow `{% extends %}`.
- **Action**: Any misplaced `{% load static %}` tags will be moved to the line immediately following `{% extends %}`.

### 3. Global CSS Inclusion
- **Observation**: `templates/base.html` is currently missing the link to the core stylesheet `css/global_ux.css`. This is likely the primary cause of the "missing CSS" issue globally.
- **Action**: Add `<link rel="stylesheet" href="{% static 'css/global_ux.css' %}">` to the `extrahead` block in `templates/base.html`.

### 4. Base Template Inheritance Recursion
- **Observation**: `templates/unfold/layouts/base.html` extends `unfold/layouts/base.html`, which might cause issues if not handled carefully by Django's template loader.
- **Action**: We will verify if this causes issues and rename or adjust inheritance if necessary to ensure the parent from the `unfold` package is loaded correctly.

## Decisions
- **Decision**: Scan all `.html` files recursively in the specified directories.
- **Decision**: Automate the fix for tag ordering to ensure consistency.
- **Decision**: Manually verify and update the primary `base.html` to restore global styling.
- **Rationale**: Strict adherence to Django's template rules is necessary for reliable inheritance and static asset resolution.
