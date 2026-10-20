from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone



class AcademicSession(models.Model):
    name = models.CharField(max_length=50, unique=True, help_text="e.g. 2025-2026")
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(
        default=False, 
        db_column='is_active',  # <--- Points to your existing database column
        help_text="Designates the active school session"
    )
    allow_modifications = models.BooleanField(
        default=True,
        help_text="Designates whether student records in this session can be added, updated, or deleted."
    )

    class Meta:
        ordering = ['-start_date']
        verbose_name = 'Academic Session'
        verbose_name_plural = 'Academic Sessions'

    def __str__(self):
        status = " (Active)" if self.is_current else ""
        return f"{self.name}{status}"

    @property
    def is_active(self):
        return self.is_current

    def save(self, *args, **kwargs):
        if self.is_current:
            AcademicSession.objects.exclude(pk=self.pk).update(is_current=False)
        super().save(*args, **kwargs)
           

# class StaffProfile(models.Model):
#     ROLE_CHOICES = [
#         ('principal', 'Principal / Head of Institution'),
#         ('academic_head', 'Academic Coordinator / Exam Head'),
#         ('teacher', 'Teacher / Faculty'),
#         ('clerk', 'Administrative Clerk'),
#     ]
#     user = models.OneToOneField(
#         User, 
#         on_delete=models.SET_NULL, 
#         null=True, 
#         blank=True, 
#         related_name='staff_profile'
#     )
#     employee_code = models.CharField(max_length=30, unique=True, db_index=True)
#     role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='teacher')
#     enployee_name = models.CharField(max_length=50, null=False, blank=False,)
    
#     # Optional picture field:
#     photo = models.ImageField(upload_to='staff_photos/', blank=True, null=True)
    
#     contact_phone = models.CharField(max_length=20)
#     qualification = models.CharField(max_length=120, blank=True, help_text="e.g. M.Sc. (Math), B.Ed.")
#     joining_date = models.DateField()
#     is_active_faculty = models.BooleanField(default=True)

#     class Meta:
#         ordering = ['employee_code']

#     def __str__(self):
#         if self.user:
#             display_name = self.user.get_full_name() or self.user.username
#         else:
#             # If no user account is linked, use employee_name or employee_code
#             display_name = getattr(self, 'employee_name', None) or getattr(self, 'enployee_name', None) or self.employee_code

#         return f"{display_name} ({self.get_role_display()})"

#     @property
#     def photo_url(self):
#         """Safely returns the photo URL if uploaded, otherwise returns None."""
#         if self.photo and hasattr(self.photo, 'url'):
#             return self.photo.url
#         return None

class OfficialNotice(models.Model):
    AUDIENCE_CHOICES = [
        ('all', 'General Public & Parents'),
        ('students', 'Students (Classes 9–12)'),
        ('staff', 'Faculty & Staff Only'),
    ]
    session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE, related_name='notices')
    title = models.CharField(max_length=255)
    audience = models.CharField(max_length=20, choices=AUDIENCE_CHOICES, default='all')
    content = models.TextField()
    attachment = models.FileField(upload_to='circulars/%Y/%m/', blank=True, null=True)
    is_pinned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        return f"[{self.audience.upper()}] {self.title}"


class ProspectiveAdmissionApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Under Review'),
        ('shortlisted', 'Shortlisted for Entrance/Interview'),
        ('approved', 'Approved for Enrollment'),
        ('rejected', 'Rejected'),
    ]
    session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE, related_name='applications')
    candidate_name = models.CharField(max_length=120)
    applying_for_class = models.CharField(
        max_length=30,
        choices=[
            ('Grade 9', 'Class IX'),
            ('Grade 10', 'Class X'),
            ('Grade 11', 'Class XI'),
            ('Grade 12', 'Class XII'),
        ]
    )
    intended_stream = models.CharField(max_length=50, blank=True)
    guardian_name = models.CharField(max_length=120)
    guardian_phone = models.CharField(max_length=20)
    guardian_email = models.EmailField(blank=True)
    application_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    submission_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submission_date']

    def __str__(self):
        return f"{self.candidate_name} ({self.applying_for_class})"
    
class SchoolContactInfo(models.Model):
    school_name = models.CharField(max_length=200)
    address = models.TextField()
    primary_phone = models.CharField(max_length=20)
    secondary_phone = models.CharField(max_length=20, blank=True, null=True)
    whatsapp_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField()
    office_hours = models.CharField(max_length=150, default="Monday – Saturday: 9:00 AM – 4:00 PM")
    map_location_query = models.CharField(
        max_length=255, 
        help_text="Location name, address, or coordinates for the Google Map."
    )

    class Meta:
        verbose_name = "School Contact Information"
        verbose_name_plural = "School Contact Information"

    def __str__(self):
        return f"{self.school_name} Contact Details"
    
# 1. Define GalleryCategory HERE in core
class GalleryCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, help_text="e.g. campus, labs, events")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = "Gallery Categories"

    def __str__(self):
        return self.name


# 2. Define GalleryImage right below it
class GalleryImage(models.Model):
    category = models.ForeignKey(
        GalleryCategory,
        on_delete=models.CASCADE,
        related_name='images'
    )
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='gallery/')
    caption = models.CharField(max_length=255, blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"{self.title} ({self.category.name})"



    