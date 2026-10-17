from django.contrib import admin
from django.utils.html import format_html
from .models import (
    AcademicClass,
    Stream,
    Section,
    FacultyMember,
    Notice,
    Subject,
    SubjectTeacherAllocation,
)
from .models import Banner, Notice, FormDownload, GalleryCategory, GalleryImage, CustomCampusFeature
from .models import Banner
from .forms import BannerForm
from academics.imagekit_client import upload_to_imagekit, delete_from_imagekit

class SectionInline(admin.TabularInline):
    model = Section
    extra = 1
    fields = ('session', 'name', 'stream', 'room_number', 'capacity')
    autocomplete_fields = ('session', 'stream')


class SubjectTeacherAllocationInline(admin.TabularInline):
    model = SubjectTeacherAllocation
    extra = 1
    autocomplete_fields = ('teacher', 'subject')


@admin.register(AcademicClass)
class AcademicClassAdmin(admin.ModelAdmin):
    list_display = ('numeric_level', 'name', 'is_intermediate', 'get_total_capacity')
    list_filter = ('is_intermediate',)
    search_fields = ('name',)
    ordering = ('numeric_level',)
    inlines = [SectionInline]

    @admin.display(description='Total Capacity')
    def get_total_capacity(self, obj):
        return obj.total_capacity


@admin.register(Stream)
class StreamAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'faculty', 'sanctioned_seats', 'get_allocated_seats')
    list_filter = ('faculty',)
    search_fields = ('name', 'code')
    ordering = ('faculty', 'name')

    @admin.display(description='Allocated Seats')
    def get_allocated_seats(self, obj):
        return obj.allocated_seats


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'session', 'academic_class', 'name', 'stream', 'room_number', 'capacity')
    list_filter = ('session', 'academic_class', 'stream')
    search_fields = ('name', 'room_number', 'academic_class__name', 'stream__name')
    autocomplete_fields = ('session', 'academic_class', 'stream')
    inlines = [SubjectTeacherAllocationInline]


@admin.register(FacultyMember)
class FacultyMemberAdmin(admin.ModelAdmin):
    list_display = ('avatar_preview', 'name', 'designation', 'category', 'qualification', 'order', 'is_active')
    list_filter = ('designation', 'category', 'is_active')
    search_fields = ('name', 'qualification')
    list_editable = ('order', 'is_active')
    ordering = ('order', 'name')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'designation', 'category', 'qualification', 'is_active', 'order')
        }),
        ('Photo & Media', {
            'fields': ('photo', 'photo_url')
        }),
        ('Principal Desk', {
            'fields': ('message',),
            'classes': ('collapse',),
            'description': 'Applicable primarily for Headmaster / Principal desk messages.'
        }),
    )

    @admin.display(description='Photo')
    def avatar_preview(self, obj):
        img_url = obj.photo.url if obj.photo else obj.photo_url
        if img_url:
            return format_html(
                '<img src="{}" style="width: 38px; height: 38px; border-radius: 50%; object-fit: cover;" />',
                img_url
            )
        return "—"


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    # Fixed: Replaced 'is_elective' with 'subject_type', added class and stream lookups
    list_display = ('code', 'name', 'subject_type', 'academic_class', 'stream')
    list_filter = ('subject_type', 'academic_class', 'stream')
    search_fields = ('name', 'code')
    autocomplete_fields = ('academic_class', 'stream')
    ordering = ('code',)


@admin.register(SubjectTeacherAllocation)
class SubjectTeacherAllocationAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'subject', 'section')
    list_filter = ('subject', 'section__academic_class', 'section__session')
    search_fields = ('teacher__name', 'subject__name', 'section__name')
    autocomplete_fields = ('teacher', 'subject', 'section')

@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    # Use existing fields on academics.Notice
    list_display = (
        'title',
        'priority',
        'publish_date',
        'expires_at',
        'is_active',
        'has_attachment',
    )
    list_filter = ('priority', 'is_active', 'publish_date')
    search_fields = ('title', 'content')
    list_editable = ('priority', 'is_active')
    ordering = ('-publish_date', '-created_at')
    date_hierarchy = 'publish_date'

    def has_attachment(self, obj):
        return bool(obj.attachment)

    has_attachment.boolean = True
    has_attachment.short_description = "Attachment"
    
    



@admin.register(FormDownload)
class FormDownloadAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'download_count', 'is_active', 'uploaded_at')
    list_filter = ('category', 'is_active', 'uploaded_at')
    search_fields = ('title', 'description')
    list_editable = ('is_active',)


# @admin.register(GalleryCategory)
# class GalleryCategoryAdmin(admin.ModelAdmin):
#     list_display = ('name', 'slug', 'image_count')
#     prepopulated_fields = {'slug': ('name',)}
#     search_fields = ('name',)

#     def image_count(self, obj):
#         return obj.images.count()
#     image_count.short_description = "Total Photos"


# @admin.register(GalleryImage)
# class GalleryImageAdmin(admin.ModelAdmin):
#     list_display = ('title', 'category', 'preview_thumbnail', 'is_featured', 'uploaded_at')
#     list_filter = ('category', 'is_featured', 'uploaded_at')
#     search_fields = ('title', 'caption')
#     list_editable = ('is_featured',)

#     def preview_thumbnail(self, obj):
#         if obj.image:
#             return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 6px;" />', obj.image.url)
#         return "-"
#     preview_thumbnail.short_description = "Preview"



@admin.register(CustomCampusFeature)
class CustomCampusFeatureAdmin(admin.ModelAdmin):
    list_display = ('title', 'preview_thumb', 'category_label', 'custom_badge', 'theme_color', 'order', 'is_active')
    list_filter = ('is_active', 'theme_color', 'category_label')
    search_fields = ('title', 'description', 'custom_tags', 'category_label')
    list_editable = ('order', 'is_active')

    fieldsets = (
        ("Basic Information", {
            'fields': ('title', 'custom_badge', 'category_label', 'description', 'image')
        }),
        ("Custom Branding & Icons", {
            'fields': ('custom_icon', 'theme_color')
        }),
        ("Custom Metrics & Highlights", {
            'fields': ('custom_tags', 'metric_value', 'metric_label')
        }),
        ("Link & Visibility", {
            'fields': ('action_url', 'action_button_text', 'order', 'is_active')
        }),
    )

    def preview_thumb(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 70px; height: 42px; object-fit: cover; border-radius: 6px;" />', 
                obj.image.url
            )
        return "-"
    preview_thumb.short_description = "Image"



class GalleryImageInline(admin.TabularInline):
    model = GalleryImage
    extra = 1
    fields = ('thumbnail', 'title', 'image', 'is_featured')
    readonly_fields = ('thumbnail',)

    def thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 55px; height: 40px; object-fit: cover; border-radius: 6px;" />',
                obj.image.url
            )
        return "—"


@admin.register(GalleryCategory)
class GalleryCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'image_count')
    prepopulated_fields = {'slug': ('name',)}

    def image_count(self, obj):
        return obj.images.count()
    image_count.short_description = "Photos"


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ('preview_thumb', 'title', 'category', 'is_featured', 'created_at')
    list_filter = ('category', 'is_featured')
    search_fields = ('title', 'caption')
    readonly_fields = ('preview_thumb', 'image_url', 'imagekit_file_id', 'created_at')

    def preview_thumb(self, obj):
        if obj.image_url:
            return format_html(
                '<img src="{}" style="width: 60px; height: 45px; object-fit: cover; border-radius: 6px;" />',
                obj.image_url
            )
        return "No Image"
    preview_thumb.short_description = "Preview"

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    form = BannerForm  # Connects the form containing the Image upload field
    list_display = ('preview_thumb', 'title', 'order', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('title',)
    list_editable = ('order', 'is_active')
    readonly_fields = ('preview_thumb', 'image_url', 'imagekit_file_id')

    fieldsets = (
        ('Banner Details', {
            'fields': ('title', 'order', 'is_active')
        }),
        ('ImageKit Media Upload', {
            'fields': ('image', 'preview_thumb', 'image_url', 'imagekit_file_id'),
            'description': 'Select an image file. It will upload automatically to ImageKit.io CDN.'
        }),
    )

    def preview_thumb(self, obj):
        if obj.image_url:
            return format_html(
                '<img src="{}?tr=w-120,h-50,fo-auto" style="width: 120px; height: 50px; object-fit: cover; border-radius: 6px; border: 1px solid #e2e8f0;" />',
                obj.image_url
            )
        return "No Image"
    preview_thumb.short_description = "Banner Preview"

    def save_model(self, request, obj, form, change):
        """
        Intercepts admin save to upload image files to ImageKit.io.
        """
        image_file = form.cleaned_data.get('image')

        # If a new image was chosen (new banner or replacing existing)
        if 'image_file' in request.FILES:
            uploaded_file = request.FILES['image_file']
            res = upload_to_imagekit(uploaded_file, uploaded_file.name, folder="campus_features")
            obj.image_url = res.url
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        """
        Deletes the file from ImageKit when a single banner is deleted in admin.
        """
        if obj.imagekit_file_id:
            delete_from_imagekit(obj.imagekit_file_id)
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        """
        Deletes files from ImageKit when multiple banners are deleted via admin action.
        """
        for banner in queryset:
            if banner.imagekit_file_id:
                delete_from_imagekit(banner.imagekit_file_id)
        super().delete_queryset(request, queryset)



