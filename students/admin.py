from django.contrib import admin
from .models import AcademicSession, Student, StudentEnrollment, StudentSubjectEnrollment


class StudentSubjectEnrollmentInline(admin.TabularInline):
    model = StudentSubjectEnrollment
    extra = 1
    # autocomplete_fields = ('subject',)


class StudentEnrollmentInline(admin.TabularInline):
    model = StudentEnrollment
    extra = 0
    autocomplete_fields = ('session', 'section')

@admin.register(AcademicSession)
class AcademicSessionAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_current', 'allow_modifications')
    search_fields = ('name',)
    list_filter = ('is_current', 'allow_modifications')

    # If you have 'fields' defined, include allow_modifications:
    fields = ('name', 'start_date', 'end_date', 'is_current', 'allow_modifications')
    

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        'admission_number',
        'student_name',
        'father_name',
        'mother_name',
        'mobile_number',
        'admission_date_formatted',
        'dob_formatted',
        'caste_category',
        'gender',
    )
    search_fields = (
        'admission_number',
        'student_name',
        'father_name',
        'mother_name',
        'mobile_number',
        'aadhaar_number',
        'account_number',
    )
    list_filter = ('gender', 'caste_category', 'admission_date')
    inlines = [StudentEnrollmentInline]
    ordering = ('admission_number',)

    fieldsets = (
        ('Basic & Admission Info', {
            'fields': (
                ('admission_number', 'admission_date'),
                'student_name',
                'profile_picture',
            )
        }),
        ('Parentage & Demographics', {
            'fields': (
                ('father_name', 'mother_name'),
                ('date_of_birth', 'gender', 'caste_category'),
            )
        }),
        ('Contact & Verification', {
            'fields': (
                ('mobile_number', 'aadhaar_number'),
                'address',
            )
        }),
        ('Banking Details (DBT / Scholarship)', {
            'fields': (
                ('bank_name', 'bank_branch'),
                ('account_number', 'ifsc_code'),
            ),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Adm Date')
    def admission_date_formatted(self, obj):
        return obj.admission_date.strftime('%d/%m/%Y') if obj.admission_date else '-'

    @admin.display(description='DOB')
    def dob_formatted(self, obj):
        return obj.date_of_birth.strftime('%d/%m/%Y') if obj.date_of_birth else '-'


@admin.register(StudentEnrollment)
class StudentEnrollmentAdmin(admin.ModelAdmin):
    list_display = (
        'roll_number',
        'student',
        'get_academic_class',
        'section',
        'session',
        'status',
        'enrolled_date_formatted',
    )
    list_filter = ('session', 'section__academic_class', 'section', 'status')
    search_fields = (
        'student__student_name',
        'student__admission_number',
        'student__mobile_number',
        'roll_number',
    )
    autocomplete_fields = ('student', 'session', 'section')
    inlines = [StudentSubjectEnrollmentInline]
    ordering = ('section', 'roll_number')

    @admin.display(description='Class')
    def get_academic_class(self, obj):
        return obj.section.academic_class.name if obj.section and obj.section.academic_class else '-'

    @admin.display(description='Enrolled Date')
    def enrolled_date_formatted(self, obj):
        return obj.enrolled_at.strftime('%d/%m/%Y') if obj.enrolled_at else '-'


@admin.register(StudentSubjectEnrollment)
class StudentSubjectEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'subject', 'is_optional')
    list_filter = ('is_optional', 'subject')
    search_fields = (
        'enrollment__student__student_name',
        'enrollment__student__admission_number',
        'subject__name',
        'subject__code',
    )
    # autocomplete_fields = ('enrollment', 'subject')