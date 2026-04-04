# Phase 0: Research & Decisions

## Admin Panel (Django Unfold) Customization
- **Decision**: Extend the `UNFOLD` dictionary inside `academy_project/settings.py` to overwrite the color palettes, optimize the sidebar grouping, and enhance table spacing parameters natively provided by `django-unfold`.
- **Rationale**: Utilizing Unfold's native configuration parameters prevents the need for overly complex custom CSS overrides and maintains upgrade compatibility.
- **Alternatives**: Custom CSS overrides injected into `admin.py`. Rejected due to maintainability issues.

## Auth & Dashboard Templates Design Framework
- **Decision**: Implement a custom global CSS file (`core/static/css/global_ux.css`) utilizing CSS Variables (Custom Properties) for colors, spacing, and typography.
- **Rationale**: CSS Variables ensure consistency and make a future dark-mode toggle or theme swap trivial. It also avoids introducing external heavyweight dependencies like Bootstrap/Tailwind at this stage of the project.
- **Alternatives**: Introducing TailwindCSS via CDN or Node build block. Rejected based on constraints heavily relying on vanilla setups rather than modifying the build pipeline drastically.

## Global Micro-interactions & Toast
- **Decision**: Build a vanilla JS skeleton loading script attached to AJAX calls and a unified CSS-based Toast Notification absolute element controlled via Javascript.
- **Rationale**: Minimal JS bundled within Django blocks ensures lightning-fast performance and no framework overhead while fulfilling all interactive requirements.
- **Alternatives**: Importing SweetAlert or similar heavy alert libraries. Rejected to keep asset weight down.
