from . import dashboard

def unfold_dashboard(request):
    """Call the dashboard callback and return its context for templates.

    This makes the `kpi` data available to admin templates (and others).
    """
    try:
        context = dashboard.dashboard_callback(request, {}) or {}
    except Exception:
        # Fail safe: don't break page rendering if dashboard has an error
        context = {}
    return context
