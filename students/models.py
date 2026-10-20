# students/models.py
from django.db import models
from django.utils import timezone
from academics.models import Section, Subject, AcademicSession  # Single source of truth[cite: 7]


class Student(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    CATEGORY_CHOICES = [
        ('GEN', 'General'),
        ('OBC', 'OBC'),
        ('BC', 'BC / Backward Class'),
        ('EBC', 'EBC / Extremely Backward Class'),
        ('SC', 'SC / Scheduled Caste'),
        ('ST', 'ST / Scheduled Tribe'),
        ('EWS', 'EWS'),
    ]

    # Admission & Basic Info
    admission_number = models.CharField(max_length=50, unique=True, db_index=True)
    admission_date = models.DateField(default=timezone.now)
    student_name = models.CharField(max_length=150, default='')
    father_name = models.CharField(max_length=150, default='')
    mother_name = models.CharField(max_length=150, default='')
    date_of_birth = models.DateField(default=timezone.now)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='M')
    caste_category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='GEN')
    
    # Contact & Identity
    mobile_number = models.CharField(max_length=15)
    aadhaar_number = models.CharField(max_length=12, blank=True, default='')
    address = models.TextField(blank=True, default='')
    profile_picture = models.ImageField(upload_to='students/avatars/', blank=True, null=True)

    # Banking Details (Direct Benefit Transfer / Scholarships)
    bank_name = models.CharField(max_length=120, blank=True, default='')
    bank_branch = models.CharField(max_length=120, blank=True, default='')
    account_number = models.CharField(max_length=30, blank=True, default='')
    ifsc_code = models.CharField(max_length=20, blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['admission_number']
        verbose_name = 'Student'
        verbose_name_plural = 'Students'

    def __str__(self):
        return f"{self.student_name} ({self.admission_number})"


class StudentEnrollment(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active & Enrolled'),
        ('promoted', 'Promoted'),
        ('graduated', 'Graduated'),
        ('dropped', 'Dropped / TC Issued'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    # Refers to the AcademicSession imported from academics.models[cite: 7]
    session = models.ForeignKey(AcademicSession, on_delete=models.PROTECT, related_name='enrollments')
    section = models.ForeignKey(Section, on_delete=models.PROTECT, related_name='enrollments')
    roll_number = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    is_informed = models.BooleanField(default=False)
    informed_at = models.DateTimeField(null=True, blank=True)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['section', 'roll_number']
        constraints = [
            models.UniqueConstraint(
                fields=['session', 'section', 'roll_number'],
                name='unique_roll_per_section_session'
            ),
            models.UniqueConstraint(
                fields=['student', 'session'],
                name='unique_student_session_enrollment'
            ),
        ]

    def __str__(self):
        return f"Roll #{self.roll_number}: {self.student.student_name} ({self.section})"


class StudentSubjectEnrollment(models.Model):
    enrollment = models.ForeignKey(StudentEnrollment, on_delete=models.CASCADE, related_name='enrolled_subjects')
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT)
    is_optional = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['enrollment', 'subject'],
                name='unique_enrollment_subject'
            )
        ]

    def __str__(self):
        return f"{self.enrollment.student.student_name} -> {self.subject.code}"