import setup_config
from .models import AcademicSession


def academic_session_context(request):
    active_session = AcademicSession.objects.filter(is_current=True).first()
    return {
        'has_active_session': bool(active_session),
        'active_session': active_session,
        # Injects setup_config everywhere alongside the session
        'school_cfg': getattr(setup_config, 'SCHOOL_CONFIG', {}),
    }