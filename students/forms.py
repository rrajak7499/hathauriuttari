from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction
from .models import Student, StudentEnrollment, StudentSubjectEnrollment
from core.models import AcademicSession
from academics.models import Section, Subject

TW_INPUT = "w-full text-xs bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500"
TW_SELECT = "w-full text-xs font-medium bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500"
DATE_INPUT_FORMATS = ['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d']


class StudentEnrollmentForm(forms.ModelForm):
    # Class & Section Selection
    section = forms.ModelChoiceField(
        queryset=Section.objects.none(),
        widget=forms.Select(attrs={'class': TW_SELECT})
    )
    roll_number = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': TW_INPUT, 'placeholder': 'e.g. 101'})
    )
    selected_subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'rounded border-slate-300 text-indigo-600 focus:ring-indigo-500'})
    )

    date_of_birth = forms.DateField(
        input_formats=DATE_INPUT_FORMATS,
        widget=forms.TextInput(attrs={'class': f'{TW_INPUT} flatpickr-date', 'placeholder': 'DD/MM/YYYY', 'autocomplete': 'off'})
    )
    admission_date = forms.DateField(
        input_formats=DATE_INPUT_FORMATS,
        widget=forms.TextInput(attrs={'class': f'{TW_INPUT} flatpickr-date', 'placeholder': 'DD/MM/YYYY', 'autocomplete': 'off'})
    )

    class Meta:
        model = Student
        fields = [
            'admission_number', 'admission_date', 'student_name', 'father_name',
            'mother_name', 'date_of_birth', 'gender', 'caste_category',
            'mobile_number', 'aadhaar_number', 'address', 'profile_picture',
            'bank_name', 'bank_branch', 'account_number', 'ifsc_code'
        ]
        widgets = {
            'admission_number': forms.TextInput(attrs={'class': TW_INPUT, 'placeholder': 'Adm. No.'}),
            'student_name': forms.TextInput(attrs={'class': TW_INPUT, 'placeholder': 'Full Name'}),
            'father_name': forms.TextInput(attrs={'class': TW_INPUT, 'placeholder': "Father's Name"}),
            'mother_name': forms.TextInput(attrs={'class': TW_INPUT, 'placeholder': "Mother's Name"}),
            'gender': forms.Select(attrs={'class': TW_SELECT}),
            'caste_category': forms.Select(attrs={'class': TW_SELECT}),
            'mobile_number': forms.TextInput(attrs={'class': TW_INPUT, 'placeholder': '10-digit Mobile'}),
            'aadhaar_number': forms.TextInput(attrs={'class': TW_INPUT, 'placeholder': '12-digit ID'}),
            'address': forms.Textarea(attrs={'rows': 2, 'class': TW_INPUT, 'placeholder': 'Full address'}),
            'profile_picture': forms.FileInput(attrs={'class': TW_INPUT}),
            'bank_name': forms.TextInput(attrs={'class': TW_INPUT, 'placeholder': 'Bank Name'}),
            'bank_branch': forms.TextInput(attrs={'class': TW_INPUT, 'placeholder': 'Branch'}),
            'account_number': forms.TextInput(attrs={'class': TW_INPUT, 'placeholder': 'Account No.'}),
            'ifsc_code': forms.TextInput(attrs={'class': TW_INPUT, 'placeholder': 'IFSC Code'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.active_session = AcademicSession.objects.filter(is_current=True).first()
        self.current_enrollment = None
        self.enrolled_subject_ids = []  # <--- Store for JS / Template use
        
        if self.active_session:
            self.fields['section'].queryset = Section.objects.filter(
                session=self.active_session
            ).select_related('academic_class', 'stream')
        else:
            self.fields['section'].queryset = Section.objects.all().select_related('academic_class', 'stream')

        # PRE-FETCH EXISTING ENROLLMENT DATA ON EDIT
        if self.instance and self.instance.pk:
            enrollment_qs = self.instance.enrollments.select_related('section', 'session')
            if self.active_session:
                self.current_enrollment = enrollment_qs.filter(session=self.active_session).first()
            if not self.current_enrollment:
                self.current_enrollment = enrollment_qs.first()

            if self.current_enrollment:
                if self.current_enrollment.section:
                    self.fields['section'].queryset = (
                        self.fields['section'].queryset | 
                        Section.objects.filter(pk=self.current_enrollment.section_id)
                    ).distinct()

                self.fields['section'].initial = self.current_enrollment.section_id
                self.fields['roll_number'].initial = self.current_enrollment.roll_number
                
                # Fetch exact subject IDs as a list of integers
                self.enrolled_subject_ids = list(
                    self.current_enrollment.enrolled_subjects.values_list('subject_id', flat=True)
                )
                self.fields['selected_subjects'].initial = self.enrolled_subject_ids
                
    def clean(self):
        cleaned_data = super().clean()
        target_session = self.active_session or (self.current_enrollment.session if self.current_enrollment else None)
        if not target_session:
            raise ValidationError("Cannot enroll student: No active academic session found in the system.")

        section = cleaned_data.get('section')
        roll_number = cleaned_data.get('roll_number')

        if section and roll_number:
            qs = StudentEnrollment.objects.filter(session=target_session, section=section, roll_number=roll_number)
            # Exclude this student's own record when validating roll number uniqueness
            if self.current_enrollment:
                qs = qs.exclude(pk=self.current_enrollment.pk)

            if qs.exists():
                self.add_error('roll_number', f"Roll number {roll_number} is already assigned in Section {section.name}.")

        return cleaned_data

    @transaction.atomic
    def save(self, commit=True):
        student = super().save(commit=commit)
        section = self.cleaned_data['section']
        roll_number = self.cleaned_data['roll_number']
        subjects = self.cleaned_data.get('selected_subjects', [])
        target_session = self.active_session or (self.current_enrollment.session if self.current_enrollment else None)

        if self.current_enrollment:
            enrollment = self.current_enrollment
            enrollment.section = section
            enrollment.roll_number = roll_number
            if target_session:
                enrollment.session = target_session
            enrollment.save()
            # Clear old mappings before saving updated subjects
            enrollment.enrolled_subjects.all().delete()
        else:
            enrollment = StudentEnrollment.objects.create(
                student=student,
                session=target_session,
                section=section,
                roll_number=roll_number,
                status='active'
            )

        # Re-attach selected subjects
        for subj in subjects:
            StudentSubjectEnrollment.objects.create(
                enrollment=enrollment,
                subject=subj,
                is_optional=(subj.subject_type in ['optional', 'vocational'])
            )

        return student  