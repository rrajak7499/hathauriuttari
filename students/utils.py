def mask_contact(phone):
    """
    Masks the phone number for visitors/unauthorized users,
    revealing only the last 4 digits (e.g., ••••••••1234).
    """
    if not phone:
        return "N/A"
    clean = str(phone).strip()
    return "••••••••" + clean[-4:] if len(clean) >= 4 else "••••••••"


def is_teacher_or_staff(user):
    """
    Checks if the user is authenticated and authorized as staff/teacher.
    """
    return user.is_authenticated and (
        user.is_superuser or 
        user.is_staff or 
        hasattr(user, 'teacher_profile')
    )