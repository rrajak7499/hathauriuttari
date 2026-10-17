from .models import AcademicSession

def academic_session_context(request):
    active_session = AcademicSession.objects.filter(is_active=True).first()
    return {
        'has_active_session': bool(active_session),
        'active_session': active_session,
    }