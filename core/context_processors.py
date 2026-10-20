# core/context_processors.py
from core.models import SchoolConfiguration, HeroBanner

try:
    from core.models import AcademicSession
except ImportError:
    from academics.models import AcademicSession


def academic_session_context(request):
    """Provides active academic session context."""
    active_session = AcademicSession.objects.filter(is_current=True).first()
    return {
        'has_active_session': bool(active_session),
        'active_session': active_session,
    }


def school_settings(request):
    """
    Context processor required by settings.py.
    Provides school_cfg and hero banners directly from the database.
    """
    cfg = SchoolConfiguration.load()

    return {
        'school_cfg': {
            'school_name': cfg.school_name,
            'short_name': cfg.short_name,
            'school_name_part_1': cfg.school_name_part_1,
            'school_name_part_2': cfg.school_name_part_2,
            'board_affiliation': cfg.board_affiliation,
            'subdomain_slug': cfg.subdomain_slug,
            'address': cfg.address,
            'primary_phone': cfg.primary_phone,
            'email': cfg.email,
            'office_hours': cfg.office_hours,
            'headmaster_contact_no': cfg.headmaster_contact_no,
            'clerk_contact_no': cfg.clerk_contact_no,
            'map_location_query': cfg.map_location_query,
            'map_coordinates': cfg.map_coordinates,
            'map_location_iframe': cfg.map_location_iframe,
            'headmaster': {
                'name': cfg.hm_name,
                'designation': cfg.hm_designation,
                'qualifications': cfg.hm_qualifications,
                'image_url': cfg.hm_image_url,
                'experience': cfg.hm_experience,
                'email': cfg.hm_email,
                'message_lead': cfg.hm_message_lead,
                'message_body': cfg.hm_message_body,
            },
        },
        'site_banners': HeroBanner.objects.filter(is_active=True).order_by('order'),
    }