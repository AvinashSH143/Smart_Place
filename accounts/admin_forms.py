from django import forms
from companies.models import Company, PlacementDrive

# Import existing form classes from their respective apps
# These modules should already define the required forms.
try:
    from academics.forms import AcademicEvaluationForm
except ImportError:
    AcademicEvaluationForm = None  # fallback stub if module missing

from .forms import CompanyForm

try:
    from discipline.forms import DisciplineRecordForm
except ImportError:
    DisciplineRecordForm = None

try:
    from students.forms import DebarmentForm
except ImportError:
    DebarmentForm = None

try:
    from discipline.forms import AppealReviewForm
except ImportError:
    AppealReviewForm = None

# Note: AppealReviewForm is defined in discipline/forms.py, not students/forms.py

class PlacementDriveForm(forms.ModelForm):
    """Form for creating/editing a PlacementDrive.
    The "Recruiting Company" field is a plain text input that accepts any
    company name. On save we look up (or create) the corresponding Company
    instance and assign it to the model.
    """
    company = forms.CharField(
        required=True,
        label='Recruiting Company',
        widget=forms.TextInput(
            attrs={
                'class': 'w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm',
                'placeholder': 'Enter company name',
            }
        ),
    )

    class Meta:
        model = PlacementDrive
        fields = [
            'company', 'job_title', 'job_role', 'job_description',
            'required_skills', 'min_cgpa', 'allowed_branches',
            'max_backlogs', 'required_academic_score',
            'application_deadline', 'drive_date', 'salary_package',
            'additional_requirements', 'is_published', 'status',
        ]
        widgets = {
            'job_title': forms.TextInput(attrs={'class': 'w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm', 'placeholder': 'e.g. Graduate Software Engineer - Backend'}),
            'job_role': forms.TextInput(attrs={'class': 'w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm', 'placeholder': 'e.g. Software Development Engineer'}),
            'job_description': forms.Textarea(attrs={'class': 'w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm', 'rows': 4}),
            'required_skills': forms.SelectMultiple(attrs={'class': 'w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm h-36'}),
            'min_cgpa': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm', 'step': '0.01', 'min': '0.00', 'max': '10.00'}),
            'allowed_branches': forms.Textarea(attrs={'class': 'w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm', 'rows': 2, 'placeholder': 'Computer Science & Engineering, Information Technology, AI & Machine Learning'}),
            'max_backlogs': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm', 'min': '0'}),
            'required_academic_score': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm', 'step': '0.1', 'min': '0.0', 'max': '100.0'}),
            'application_deadline': forms.DateInput(attrs={'class': 'w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm', 'type': 'date'}),
            'drive_date': forms.DateInput(attrs={'class': 'w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm', 'type': 'date'}),
            'salary_package': forms.TextInput(attrs={'class': 'w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm', 'placeholder': 'e.g. 14.5 LPA (CTC)'}),
            'additional_requirements': forms.Textarea(attrs={'class': 'w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm', 'rows': 2, 'placeholder': 'Any specific bonds, shift requirements, or eligibility waivers...'}),
            'status': forms.Select(attrs={'class': 'w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'w-4 h-4 rounded text-indigo-600 focus:ring-indigo-500 bg-slate-900 border-slate-700'}),
        }

    def clean(self):
        cleaned = super().clean()
        company_name = cleaned.get('company')
        if not company_name:
            raise forms.ValidationError('Company name is required.')
        company_obj, _ = Company.objects.get_or_create(name=company_name)
        cleaned['company'] = company_obj
        return cleaned
