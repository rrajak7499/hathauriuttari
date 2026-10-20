from django.db import models
from django.shortcuts import render, redirect
from django.contrib import messages

from core.forms import StaffSignUpForm

from .models import  ProspectiveAdmissionApplication as AdmissionApplication, SchoolContactInfo
from students.models import AcademicSession, StudentEnrollment
# from .forms import StaffSignUpForm
from django.contrib.auth import login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import JsonResponse
# IMPORT FROM ACADEMICS APP HERE:
from academics.models import GalleryCategory, GalleryImage
from .models import HeroBanner


def apply_admission_view(request):
    if request.method == 'POST':
        AdmissionApplication.objects.create(
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            applying_for_grade=request.POST.get('applying_for_grade'),
            date_of_birth=request.POST.get('date_of_birth'),
            parent_name=request.POST.get('parent_name'),
            parent_phone=request.POST.get('parent_phone'),
            parent_email=request.POST.get('parent_email'),
            previous_school=request.POST.get('previous_school', ''),
            documents=request.FILES.get('documents')
        )
        messages.success(request, "Your application has been received. The admissions office will contact you soon.")
        return redirect('home')
    return render(request, 'apply_admission.html')

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = StaffSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome {user.first_name}! Your staff account has been registered.")
            return redirect('home')
        else:
            messages.error(request, "Please correct the registration errors below.")
    else:
        form = StaffSignUpForm()

    return render(request, 'registration/signup.html', {'form': form})

def about(request):
    return render(request, 'about.html')


def contact(request):
    contact = SchoolContactInfo.objects.first()
    return render(request, 'contact.html', {'contact': contact})

def portal_home_view(request):
    return render(request, 'home.html')










