from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('about/', views.about, name='about'),
    path('faculty/', views.faculty_view, name='faculty'),

    path('notices/', views.notices_view, name='notices'),
    path('notices/create/', views.notice_create, name='notice_create'),
    path('notices/<int:pk>/edit/', views.notice_update, name='notice_update'),
    path('notices/<int:pk>/delete/', views.notice_delete, name='notice_delete'),

    # path('gallery/', views.gallery_view, name='gallery'),

    # Downloads listing page
    path('downloads/', views.downloads_view, name='downloads'),
    # Add new download link
    path('downloads/add/', views.download_create, name='download_create'),
    # Edit download link
    path('downloads/<int:pk>/edit/', views.download_update, name='download_update'),
    # Delete download
    path('downloads/<int:pk>/delete/', views.download_delete, name='download_delete'),
    # Track download counter and redirect to Google Drive
    path('downloads/<int:pk>/track/', views.track_download_file, name='track_download_file'),
    
    path('contact/', views.contact_view, name='contact'),

    # Academic Structure Management
    path('academic-structure/', views.manage_academic_structure, name='manage_academic_structure'),
    path('academic-structure/section/<int:section_id>/edit/', views.edit_section, name='edit_section'),
    path('academic-structure/section/<int:section_id>/delete/', views.delete_section, name='delete_section'),
    path('academic-structure/stream/<int:stream_id>/edit/', views.edit_stream, name='edit_stream'),
    path('academic-structure/stream/<int:stream_id>/delete/', views.delete_stream, name='delete_stream'),

    path('academic-structure/', views.manage_academic_structure, name='manage_academic_structure'),
    path('staff-permissions/', views.manage_staff_permissions, name='manage_staff_permissions'),

    
    # Banner Management CRUD
    path('manage/banners/', views.banner_manage_list, name='banner_manage'),
    path('manage/banners/create/', views.banner_create, name='banner_create'),
    path('manage/banners/<int:pk>/edit/', views.banner_update, name='banner_update'),
    path('manage/banners/<int:pk>/toggle/', views.banner_toggle_status, name='banner_toggle_status'),
    path('manage/banners/<int:pk>/delete/', views.banner_delete, name='banner_delete'),
]