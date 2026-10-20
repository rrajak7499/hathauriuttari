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


class SingletonModel(models.Model):
    """Abstract singleton model ensuring only one active config record exists in DB."""
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass  # Prevent accidental deletion

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class SchoolConfiguration(SingletonModel):
    # School Identity & Contact Info
    school_name = models.CharField(max_length=200, default="Uchcha Madhyamic Vidyalaya Hathauri Uttari")
    short_name = models.CharField(max_length=100, default="U.M.V. Hathauri Uttari")
    school_name_part_1 = models.CharField(max_length=100, default="Uchcha Madhyamic Vidyalaya")
    school_name_part_2 = models.CharField(max_length=100, default="Hathauri Uttari")
    board_affiliation = models.CharField(max_length=100, default="BSEB Patna")
    subdomain_slug = models.SlugField(max_length=100, default="hathauri-uttari")
    address = models.TextField(default="Uchcha Madhyamic Vidyalaya Hathauri Uttari, Kothra, Baheri, Darbhanga, Bihar - 847105")
    primary_phone = models.CharField(max_length=20, default="+91 9110962641")
    email = models.EmailField(default="principal@umvhathauri.edu.in")
    office_hours = models.CharField(max_length=120, default="Monday – Saturday: 9:00 AM – 4:00 PM")

    # Specific Contacts
    headmaster_contact_no = models.CharField(max_length=20, default="+91-9110962641")
    clerk_contact_no = models.CharField(max_length=20, default="+91-7079192999")

    # Map Settings
    map_location_query = models.CharField(max_length=255, default="Uchcha Madhyamic Vidyalaya Hathauri Uttari Baheri Darbhanga")
    map_coordinates = models.CharField(max_length=100, default="25.97133354435404, 85.9963287249768")
    map_location_iframe = models.TextField(blank=True, default="")

    # Headmaster's Profile & Welcome Message
    hm_name = models.CharField(max_length=150, default="Raman Jee Ray")
    hm_designation = models.CharField(max_length=100, default="Headmaster")
    hm_qualifications = models.CharField(max_length=150, default="M.Sc. (Physics), M.Ed, Ph.D.")
    hm_image_url = models.URLField(max_length=500, blank=True, default="https://i.postimg.cc/L5BS9BLw/hm.png")
    hm_experience = models.CharField(max_length=150, default="7+ Years in Educational Administration")
    hm_email = models.EmailField(default="principal@umvhathauri.edu.in")
    hm_message_lead = models.CharField(max_length=255, default="Guiding young minds through holistic education, academic discipline, and values.")
    hm_message_body = models.TextField(default="At Uchcha Madhyamic Vidyalaya Hathauri Uttari, we believe that true education transcends beyond the boundaries of textbooks...")

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "School Portal Configuration"
        verbose_name_plural = "School Portal Configuration"

    def __str__(self):
        return f"{self.school_name} (Global Settings)"


class HeroBanner(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=255, blank=True, default="")
    image_url = models.URLField(max_length=500)
    order = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        verbose_name = "Hero Banner"
        verbose_name_plural = "Hero Banners"

    def __str__(self):
        return self.title





    