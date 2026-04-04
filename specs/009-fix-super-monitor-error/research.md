# Research: Fix Super Monitor Error

## Overview

This document summarizes the findings related to the `TemplateSyntaxError` at the `/super-monitor/` endpoint.

## Findings

### Django Template Syntax for Comparisons

- **Decision**: Update all instances of `==` in Django `{% if ... %}` blocks to include spaces, i.e., ` == `.
- **Rationale**: The Django template language requires spaces around operators in variable tags and control statements. A lack of spaces (e.g., `user1_id==u.id`) results in a parsing error because the Django template lexer cannot distinguish the variables from the operator.
- **Alternatives considered**:
  - Updating the logic in the view instead of the template. *Rejected*: Passing the `selected` attribute directly from the view would violate the Separation of Concerns principle ("Fat Models, Thin Views"). The template is the correct place to handle conditional display formatting based on standard data given by the view.
  - Using a custom template tag to perform the comparison. *Rejected*: This adds unnecessary overhead when the built-in `{% if %}` tag works perfectly once the syntax error is corrected.

## Resolution

The path forward is clear: modifying lines 352 and 366 (or anywhere similar) in `core/templates/core/universal_chat_monitor.html` to add spaces around the comparison operators will resolve the 500 error and restore functionality.