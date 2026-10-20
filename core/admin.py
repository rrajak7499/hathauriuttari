from django.contrib import admin
from .models import (
    AcademicSession,
    SchoolContactInfo, 
    OfficialNotice, 
    ProspectiveAdmissionApplication
)
from django.contrib import admin
from django.utils.html import format_html

# @admin.register(AcademicSession)
# class AcademicSessionAdmin(admin.ModelAdmin):
#     list_display = ('name', 'start_date_formatted', 'end_date_formatted', 'is_current','allow_modifications')
#     list_editable = ('is_current',)
#     list_filter = ('is_current','allow_modifications')
#     # Required for autocomplete_fields in academics and students admin
#     search_fields = ('name',)
#     ordering = ('-start_date',)
#     fields = ('name', 'start_date', 'end_date', 'is_current', 'allow_modifications')

#     @admin.display(description='Start Date')
#     def start_date_formatted(self, obj):
#         return obj.start_date.strftime('%d/%m/%Y') if obj.start_date else '-'

#     @admin.display(description='End Date')
#     def end_date_formatted(self, obj):
#         return obj.end_date.strftime('%d/%m/%Y') if obj.end_date else '-'

@admin.register(SchoolContactInfo)
class SchoolContactInfoAdmin(admin.ModelAdmin):
    list_display = ('school_name', 'primary_phone', 'email', 'office_hours')

    # Prevent creating duplicate records; keep a single editable configuration
    def has_add_permission(self, request):
        return not SchoolContactInfo.objects.exists()

# @admin.register(StaffProfile)
# class StaffProfileAdmin(admin.ModelAdmin):
#     list_display = (
#         'employee_code', 
#         'user', 
#         'role', 
#         'contact_phone', 
#         'is_active_faculty'
#     )
#     list_filter = ('role', 'is_active_faculty')
#     search_fields = (
#         'employee_code', 
#         'user__username', 
#         'user__first_name', 
#         'user__last_name', 
#         'contact_phone'
#     )
#     autocomplete_fields = ('user',)


@admin.register(OfficialNotice)
class OfficialNoticeAdmin(admin.ModelAdmin):
    list_display = ('title', 'audience', 'session', 'is_pinned', 'created_date_formatted')
    list_filter = ('audience', 'is_pinned', 'session')
    search_fields = ('title', 'content')
    autocomplete_fields = ('session',)
    ordering = ('-created_at',)

    @admin.display(description='Published Date')
    def created_date_formatted(self, obj):
        return obj.created_at.strftime('%d/%m/%Y') if obj.created_at else '-'


@admin.register(ProspectiveAdmissionApplication)
class ProspectiveAdmissionApplicationAdmin(admin.ModelAdmin):
    list_display = (
        'candidate_name', 
        'applying_for_class', 
        'intended_stream', 
        'guardian_phone', 
        'application_status', 
        'submission_date_formatted'
    )
    list_filter = ('application_status', 'applying_for_class', 'session')
    search_fields = ('candidate_name', 'guardian_name', 'guardian_phone')
    autocomplete_fields = ('session',)
    ordering = ('-submission_date',)

    @admin.display(description='Submission Date')
    def submission_date_formatted(self, obj):
        return obj.submission_date.strftime('%d/%m/%Y') if obj.submission_date else '-'
