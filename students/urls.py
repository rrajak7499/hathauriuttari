from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.student_list_view, name='student_list'),
    
    # Support both 'add_student' and 'student_create'
    path('add/', views.student_create, name='student_create'),
    path('add-student/', views.student_create, name='add_student'),

    # Add these export routes:
    path('export/excel/', views.export_students_excel, name='export_students_excel'),
    path('export/pdf/', views.export_students_pdf, name='export_students_pdf'),
    path('<int:pk>/export/excel/', views.export_single_student_excel, name='export_single_student_excel'),
    path('<int:pk>/export/pdf/', views.export_single_student_pdf, name='export_single_student_pdf'),

    path('<int:pk>/edit/', views.student_update, name='student_update'),
    path('<int:pk>/delete/', views.student_delete, name='student_delete'),  # <--- Added
    path('<int:pk>/', views.student_detail, name='student_detail'),
    path('promote/', views.promote_session, name='promote_session'),

    # Academic Structure endpoints
    path('academics/structure/', views.manage_academic_structure, name='manage_academic_structure'),
    path('academics/sections/<int:pk>/edit/', views.edit_section_view, name='edit_section'),
    path('academics/sections/<int:pk>/delete/', views.delete_section_view, name='delete_section'),
    path('academics/streams/<int:pk>/edit/', views.edit_stream_view, name='edit_stream'),
    path('academics/streams/<int:pk>/delete/', views.delete_stream_view, name='delete_stream'),

    path('api/subjects-by-section/', views.get_subjects_by_section, name='api_subjects_by_section'),
    path('enrollment/<int:enrollment_id>/toggle-informed/', views.toggle_student_informed, name='toggle_student_informed'),
    path('section/<int:section_id>/clear-informed/', views.clear_section_informed, name='clear_section_informed'),
    path('session/toggle-flags/', views.toggle_session_flags, name='toggle_session_flags'),

]