# Phase 0: Research & Decisions

## Authentication Enforcement on Dashboard

- **Decision**: Decorate `supervisor_dashboard` with `@login_required(login_url='management_login')`.
- **Rationale**: Currently it uses `@login_required` without `login_url`, and `LOGIN_URL` is not globally defined in `settings.py`. Other views explicitly define `login_url` in the decorator. Following the codebase's existing pattern, applying `login_url='management_login'` properly directs anonymous users directly to the requested login page.
- **Alternatives considered**: Setting `LOGIN_URL` globally in `settings.py`. Rejected because it could break `plogin` and `chat_login` fallback flows.

## Authenticated User Redirect from Login

- **Decision**: Update `management_login` view to redirect authenticated users to `supervisor_dashboard`.
- **Rationale**: The specification requests that if `request.user.is_authenticated` is True, it should automatically return a redirect to `/dashboard/`. Currently, the `management_login` view redirects authenticated superusers and managers to `admin_panel` and others to `chat_logout`. Modifying it to uniformly redirect to `supervisor_dashboard` (which corresponds to `/dashboard/` path) fulfills the spec.
- **Alternatives considered**: Using `LoginView.as_view(redirect_authenticated_user=True)`. Rejected because `management_login` contains some specific view logic (for admins) that is currently functionally separated from standard Django class-based views.
