import re
from django.db import models
from django.db.models import Sum
from django.utils.html import format_html
from django.utils import timezone

from core.models import AcademicSession

class AcademicClass(models.Model):
    CLASS_CHOICES = [
        (9, 'Class IX (Secondary Foundation)'),
        (10, 'Class X (Secondary Board)'),
        (11, 'Class XI (Senior Secondary)'),
        (12, 'Class XII (Senior Secondary Terminal)'),
    ]

    numeric_level = models.PositiveSmallIntegerField(
        choices=CLASS_CHOICES,
        unique=True,
        help_text="Numeric standard level (9 to 12)"
    )
    name = models.CharField(max_length=100)
    is_intermediate = models.BooleanField(
        default=False, 
        help_text="Designates senior secondary (+2) classes (11th & 12th)"
    )

    class Meta:
        ordering = ['numeric_level']
        verbose_name = 'Academic Class'
        verbose_name_plural = 'Academic Classes'

    def __str__(self):
        return self.get_numeric_level_display()

    def save(self, *args, **kwargs):
        if self.numeric_level in [11, 12]:
            self.is_intermediate = True
        super().save(*args, **kwargs)

    @property
    def total_capacity(self):
        result = self.sections.aggregate(total=Sum('capacity'))
        return result['total'] or 0


class Stream(models.Model):
    FACULTY_CHOICES = [
        ('SCIENCE', 'Faculty of Science (I.Sc)'),
        ('ARTS', 'Faculty of Arts (I.A)'),
        ('COMMERCE', 'Faculty of Commerce (I.Com)'),
    ]

    faculty = models.CharField(max_length=20, choices=FACULTY_CHOICES, default='SCIENCE')
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=30, unique=True, help_text="e.g., ISC-MATH, IA-HIST")
    description = models.TextField(blank=True, default='')
    sanctioned_seats = models.PositiveIntegerField(default=60)

    class Meta:
        ordering = ['faculty', 'name']
        verbose_name = 'Academic Stream'
        verbose_name_plural = 'Academic Streams'

    def __str__(self):
        return f"{self.name} ({self.code})"

    @property
    def allocated_seats(self):
        result = self.sections.aggregate(total=Sum('capacity'))
        return result['total'] or 0


class Section(models.Model):
    session = models.ForeignKey(
        AcademicSession,
        on_delete=models.CASCADE,
        related_name='sections',
        null=True,
        blank=True,
        help_text="Academic session this section belongs to"
    )
    academic_class = models.ForeignKey(
        AcademicClass, 
        on_delete=models.CASCADE, 
        related_name='sections',
        db_column='school_class_id'
    )
    stream = models.ForeignKey(
        Stream, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='sections',
        help_text="Required for intermediate classes (+2)"
    )
    name = models.CharField(max_length=30, help_text="Section name/label, e.g., 'A', 'B'")
    room_number = models.CharField(max_length=60, blank=True, default='')
    capacity = models.PositiveIntegerField(default=40)

    class Meta:
        ordering = ['academic_class__numeric_level', 'name']
        verbose_name = 'Class Section'
        verbose_name_plural = 'Class Sections'
        constraints = [
            models.UniqueConstraint(
                fields=['session', 'academic_class', 'name', 'stream'],
                name='unique_section_per_session_class_stream'
            ),
            models.UniqueConstraint(
                fields=['session', 'academic_class', 'name'],
                condition=models.Q(stream__isnull=True),
                name='unique_section_without_stream'
            )
        ]

    def __str__(self):
        stream_str = f" [{self.stream.code}]" if self.stream else ""
        session_prefix = f"({self.session.name}) " if self.session else ""
        return f"{session_prefix}{self.academic_class.name} - Sec {self.name}{stream_str}"


class FacultyMember(models.Model):
    DESIGNATION_CHOICES = [
        ('HM', 'Headmaster / Principal In-Charge'),
        ('PGT', 'PGT (+2 Senior Secondary Teacher)'),
        ('TGT', 'TGT (High School Teacher)'),
        ('STAFF', 'Administrative / Support Staff'),
    ]
    CATEGORY_CHOICES = [
        ('science', 'Science (+2)'),
        ('arts', 'Arts (+2)'),
        ('secondary', 'Secondary (9th-10th)'),
        ('general', 'Administration & General'),
    ]

    name = models.CharField(max_length=150)
    designation = models.CharField(max_length=20, choices=DESIGNATION_CHOICES, default='TGT')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='secondary')
    qualification = models.CharField(max_length=120, default='B.Ed')
    photo = models.ImageField(upload_to='faculty/', blank=True, null=True)
    photo_url = models.URLField(blank=True, default='', help_text="Fallback external URL if no uploaded photo")
    message = models.TextField(blank=True, default='', help_text="Principal/HM desk message")
    order = models.PositiveIntegerField(default=0, help_text="Display priority order")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Faculty Member'
        verbose_name_plural = 'Faculty Members'

    def __str__(self):
        return f"{self.name} ({self.get_designation_display()})"

class Subject(models.Model):
    SUBJECT_TYPE_CHOICES = [
        ('compulsory', 'Compulsory / Main'),
        ('elective', 'Elective'),
        ('optional', 'Additional / Optional'),
        ('vocational', 'Vocational'),
    ]

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, blank=True)
    subject_type = models.CharField(max_length=20, choices=SUBJECT_TYPE_CHOICES, default='compulsory')
    academic_class = models.ForeignKey(
        'academics.AcademicClass', 
        on_delete=models.CASCADE, 
        related_name='subjects'
    )
    stream = models.ForeignKey(
        'academics.Stream', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='subjects'
    )

    class Meta:
        ordering = ['academic_class', 'subject_type', 'code', 'name']

    def __str__(self):
        code_str = f" ({self.code})" if self.code else ""
        stream_str = f" [{self.stream.code}]" if self.stream else ""
        return f"{self.academic_class.name}{stream_str} - {self.name}{code_str}"
    

class SubjectTeacherAllocation(models.Model):
    teacher = models.ForeignKey(
        FacultyMember, 
        on_delete=models.CASCADE, 
        related_name='subject_allocations'
    )
    subject = models.ForeignKey(
        Subject, 
        on_delete=models.CASCADE, 
        related_name='teacher_allocations'
    )
    section = models.ForeignKey(
        Section, 
        on_delete=models.CASCADE, 
        related_name='teacher_allocations'
    )

    class Meta:
        verbose_name = 'Subject Teacher Allocation'
        verbose_name_plural = 'Subject Teacher Allocations'
        constraints = [
            models.UniqueConstraint(
                fields=['teacher', 'subject', 'section'],
                name='unique_teacher_subject_section'
            )
        ]

    def __str__(self):
        return f"{self.teacher.name} -> {self.subject.code} ({self.section})"

class Banner(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=255, blank=True, null=True)
    button_text = models.CharField(max_length=50, blank=True, null=True)
    action_url = models.URLField(max_length=500, blank=True, null=True)
    image_url = models.URLField(max_length=500, help_text="ImageKit CDN URL")
    imagekit_file_id = models.CharField(max_length=100, blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title

def get_drive_file_id(url):
    """Extracts the Google Drive file ID from standard share links."""
    if not url:
        return None
    # Matches patterns like /file/d/<id>/ or ?id=<id>
    match = re.search(r'/d/([a-zA-Z0-9_-]+)', url) or re.search(r'id=([a-zA-Z0-9_-]+)', url)
    return match.group(1) if match else None


class Notice(models.Model):
    PRIORITY_CHOICES = [
        ('normal', 'Standard Notice'),
        ('important', 'Important Announcement'),
        ('urgent', 'Urgent / Flash Update'),
    ]

    title = models.CharField(max_length=255)
    content = models.TextField(blank=True, help_text="Optional detailed description or message", null=True)
    priority = models.CharField(max_length=15, choices=PRIORITY_CHOICES, default='normal')
    
    # Google Drive Link instead of FileField
    drive_link = models.URLField(
        max_length=500, 
        blank=True, 
        null=True, 
        help_text="Paste Google Drive shareable link (Ensure access is set to 'Anyone with the link')"
    )
    
    publish_date = models.DateField(default=timezone.now)
    expires_at = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-publish_date', '-created_at']

    def __str__(self):
        return self.title

    @property
    def direct_download_url(self):
        """Generates direct download link from Google Drive."""
        file_id = get_drive_file_id(self.drive_link)
        if file_id:
            return f"https://drive.google.com/uc?export=download&id={file_id}"
        return self.drive_link

    @property
    def preview_url(self):
        """Generates preview link for embedding in iframe or viewing in browser."""
        file_id = get_drive_file_id(self.drive_link)
        if file_id:
            return f"https://drive.google.com/file/d/{file_id}/preview"
        return self.drive_link

class FormDownload(models.Model):
    CATEGORY_CHOICES = [
        ('admission', 'Admission Forms'),
        ('academic', 'Academic / Syllabus'),
        ('examination', 'Exam Forms & Schedules'),
        ('administrative', 'TC, Leaves & Admin Requests'),
    ]

    title = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='admission')
    drive_link = models.URLField(
        max_length=500,
        help_text="Paste Google Drive shareable link (Ensure access is set to 'Anyone with the link')"
    )
    description = models.TextField(blank=True)
    download_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category', 'title']

    def __str__(self):
        return f"[{self.get_category_display()}] {self.title}"

    @property
    def direct_download_url(self):
        file_id = get_drive_file_id(self.drive_link)
        if file_id:
            return f"https://drive.google.com/uc?export=download&id={file_id}"
        return self.drive_link

    @property
    def preview_url(self):
        file_id = get_drive_file_id(self.drive_link)
        if file_id:
            return f"https://drive.google.com/file/d/{file_id}/preview"
        return self.drive_link
    

class GalleryCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = "Gallery Categories"

    def __str__(self):
        return self.name


class GalleryImage(models.Model):
    category = models.ForeignKey(
        GalleryCategory,
        on_delete=models.CASCADE,
        related_name='images'
    )
    title = models.CharField(max_length=200)
    image_url = models.URLField(max_length=500, help_text="ImageKit CDN URL")
    imagekit_file_id = models.CharField(max_length=100, blank=True, null=True)
    caption = models.CharField(max_length=255, blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.category.name})"
    


class CustomCampusFeature(models.Model):
    # Free-text fields so you aren't restricted to pre-defined dropdowns
    title = models.CharField(
        max_length=150, 
        help_text="Custom title (e.g., 'Robotics & AI Innovation Lab')"
    )
    custom_badge = models.CharField(
        max_length=80, 
        blank=True, 
        help_text="Custom tag (e.g., 'STEM Center', 'Grade 9-12', 'New Addition')"
    )
    category_label = models.CharField(
        max_length=80, 
        blank=True, 
        help_text="Custom group name (e.g., 'Research', 'Athletics', 'Digital Hub')"
    )
    description = models.TextField(
        help_text="Your own custom description and highlights"
    )
    image = models.URLField(
        max_length=500, 
        blank=True, 
        help_text="Direct ImageKit URL (or upload below in Admin)"
    )
    
    # Custom appearance controls
    custom_icon = models.CharField(
        max_length=60, 
        default='bi-star-fill', 
        help_text="Any Bootstrap/Lucide icon class (e.g., 'bi-cpu', 'bi-trophy', 'bi-palette')"
    )
    theme_color = models.CharField(
        max_length=30, 
        default='indigo', 
        help_text="Tailwind base color name: 'indigo', 'emerald', 'amber', 'rose', 'sky', 'purple'"
    )
    
    # Custom tags & highlights (comma-separated, typed freely)
    custom_tags = models.CharField(
        max_length=255, 
        blank=True, 
        help_text="Comma-separated items (e.g., '3D Printers, Drone Kits, Arduino Boards')"
    )
    
    # Custom statistics / highlight metrics
    metric_value = models.CharField(
        max_length=30, 
        blank=True, 
        help_text="Optional stat (e.g., '50+ Kits', '24/7 Access', '1,200 Sq.Ft')"
    )
    metric_label = models.CharField(
        max_length=60, 
        blank=True, 
        help_text="Stat description (e.g., 'Total Capacity', 'Setup Area')"
    )

    action_url = models.CharField(
        max_length=255, 
        blank=True, 
        help_text="Optional custom link or anchor"
    )
    action_button_text = models.CharField(
        max_length=50, 
        blank=True, 
        default="Explore More"
    )

    order = models.PositiveIntegerField(
        default=0, 
        help_text="Display order (0 shows first)"
    )
    is_active = models.BooleanField(
        default=True, 
        help_text="Toggle visible / hidden"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = 'Custom Feature'
        verbose_name_plural = 'Custom Features'

    def __str__(self):
        return self.title

    @property
    def parsed_tags(self):
        """Splits free-form comma-separated tags into a clean list."""
        if not self.custom_tags:
            return []
        return [tag.strip() for tag in self.custom_tags.split(',') if tag.strip()]





# Backward-compatibility aliases for other apps and legacy views
SchoolClass = AcademicClass
ClassSection = Section
AcademicStream = Stream
NewSubjectTeacherAllocation = SubjectTeacherAllocation

__all__ = [
    'AcademicClass',
    'Stream',
    'Section',
    'FacultyMember',
    'Notice',
    'Subject',
    'SubjectTeacherAllocation',
    'SchoolClass',
    'ClassSection',
    'AcademicStream',
    'NewSubjectTeacherAllocation',
]