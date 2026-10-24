def assistant(request):
    """The assistant widget's settings for base.html (skipped on the dashboard)."""
    if request.path.startswith(('/admin-dashboard/', '/admin/', '/accounts/')):
        return {}
    from .models import AssistantSettings
    try:
        cfg = AssistantSettings.get()
    except Exception:  # table not migrated yet
        return {}
    return {'assistant_cfg': cfg if cfg.enabled else None}
