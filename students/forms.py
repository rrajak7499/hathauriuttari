# students/forms.py
from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction

# Single source of truth for all academic relations[cite: 7]:
from academics.models import Section, Subject, AcademicSession
from .models import Student, StudentEnrollment, StudentSubjectEnrollment

TW_INPUT = "w-full text-xs bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500"
TW_SELECT = "w-full text-xs font-medium bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500"
DATE_INPUT_FORMATS = ['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d']


class StudentEnrollmentForm(forms.ModelForm):
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
        widget=forms.TextInput(attrs={
            'class': f'{TW_INPUT} flatpickr-date',
            'placeholder': 'DD/MM/YYYY',
            'autocomplete': 'off',
        })
    )
    admission_date = forms.DateField(
        input_formats=DATE_INPUT_FORMATS,
        widget=forms.TextInput(attrs={
            'class': f'{TW_INPUT} flatpickr-date',
            'placeholder': 'DD/MM/YYYY',
            'autocomplete': 'off',
        })
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
            'aadhaar_number': forms.TextInput(attrs={'class': TW_INPUT, 'placeholder': '12-digit Number'}),
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
        if self.active_session:
            self.fields['section'].queryset = Section.objects.filter(
                session=self.active_session
            ).select_related('academic_class', 'stream')
        else:
            self.fields['section'].queryset = Section.objects.none()

    def clean_aadhaar_number(self):
        aadhaar = self.cleaned_data.get('aadhaar_number', '').strip()
        if aadhaar and (len(aadhaar) != 12 or not aadhaar.isdigit()):
            raise forms.ValidationError("Must be exactly 12 digits.")
        return aadhaar

    def clean(self):
        cleaned_data = super().clean()
        if not self.active_session:
            raise ValidationError("No active academic session found.")

        section = cleaned_data.get('section')
        roll_number = cleaned_data.get('roll_number')

        if section and roll_number:
            if StudentEnrollment.objects.filter(
                session=self.active_session,
                section=section,
                roll_number=roll_number
            ).exists():
                self.add_error('roll_number', f"Roll number {roll_number} is already taken in Section {section.name}.")

        return cleaned_data

    @transaction.atomic
    def save(self, commit=True):
        student = super().save(commit=commit)
        section = self.cleaned_data['section']
        roll_number = self.cleaned_data['roll_number']
        subjects = self.cleaned_data.get('selected_subjects', [])

        enrollment = StudentEnrollment.objects.create(
            student=student,
            session=self.active_session,
            section=section,
            roll_number=roll_number,
            status='active'
        )

        for subj in subjects:
            StudentSubjectEnrollment.objects.create(
                enrollment=enrollment,
                subject=subj,
                is_optional=(subj.subject_type in ['optional', 'vocational'])
            )

        return student