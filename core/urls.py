from django.urls import path
from django.contrib.auth import views as auth_views


from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from core import views as core_views
from academics import views as academics_view
# from academics import views as academics_views
from core.forms import (
    CustomLoginForm, 
    CustomPasswordResetForm, 
    CustomSetPasswordForm
)
from . import views

urlpatterns = [
    path('', academics_view.home_view, name='home'),
    # path('notices/', views.notices, name='notices'),
    path('admissions/apply/', views.apply_admission_view, name='apply_admission'),
    path('login/', auth_views.LoginView.as_view(template_name='authentication/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # path('notices/', views.notice_board_view, name='notice_board'),
    # path('downloads/', views.forms_downloads_view, name='forms_downloads'),
    path('gallery/', academics_view.gallery_view, name='gallery'),
    path('portal/', views.portal_home_view, name='portal_home'),

    
    # -------------------------------------------------------------
    # Authentication & Password Recovery Routes
    # -------------------------------------------------------------
    path('login/', auth_views.LoginView.as_view(
        template_name='registration/login.html',
        authentication_form=CustomLoginForm
    ), name='login'),

    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', core_views.signup_view, name='signup'),

    # Forget / Reset Password Flow
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html',
        form_class=CustomPasswordResetForm,
        email_template_name='registration/password_reset_email.html',
        subject_template_name='registration/password_reset_subject.txt',
    ), name='password_reset'),

    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ), name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html',
        form_class=CustomSetPasswordForm
    ), name='password_reset_confirm'),

    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),

]