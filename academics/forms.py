from django import forms
from .models import AcademicSubmission, AcademicEvaluation
from students.models import Skill

class AcademicSubmissionForm(forms.ModelForm):
    class Meta:
        model = AcademicSubmission
        fields = ['title', 'category', 'description', 'file', 'related_skill']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-slate-900 placeholder-slate-400 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm transition',
                'placeholder': 'e.g. Distributed Key-Value Store Project or AWS Solutions Architect Certificate',
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-3 bg-slate-900 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm transition',
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 bg-slate-900 placeholder-slate-400 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm transition',
                'rows': 4,
                'placeholder': 'Explain the project scope, technical stack, your contributions, or certification syllabus...',
            }),
            'file': forms.FileInput(attrs={
                'class': 'w-full text-sm text-slate-400 file:mr-4 file:py-2.5 file:px-4 file:rounded-xl file:border-0 file:text-sm file:font-medium file:bg-indigo-600 file:text-white hover:file:bg-indigo-500 cursor-pointer',
            }),
            'related_skill': forms.Select(attrs={
                'class': 'w-full px-4 py-3 bg-slate-900 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm transition',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['related_skill'].required = False
        self.fields['related_skill'].empty_label = "-- Select Related Skill (Optional) --"

from .models import AcademicSubmission

class AcademicEvaluationForm(forms.ModelForm):
    # Status field to update the parent submission's status
    STATUS_CHOICES = AcademicSubmission.STATUS_CHOICES
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        label='Submission Status',
        widget=forms.Select(
            attrs={
                'class': 'w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm'
            }
        )
    )
    # Optional checkbox to auto‑verify the related skill when approving
    verify_related_skill = forms.BooleanField(
        required=False,
        label='Mark related skill as verified',
        widget=forms.CheckboxInput(
            attrs={
                'class': 'w-4 h-4 rounded text-indigo-600 focus:ring-indigo-500 bg-slate-900 border-slate-700'
            }
        )
    )
    class Meta:
        model = AcademicEvaluation
        fields = [
            'marks_relevance', 'marks_quality', 'marks_practical',
            'marks_originality', 'feedback'
        ]
        widgets = {
            'marks_relevance': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm', 'min': 0, 'max': 20}),
            'marks_quality': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm', 'min': 0, 'max': 30}),
            'marks_practical': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm', 'min': 0, 'max': 25}),
            'marks_originality': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm', 'min': 0, 'max': 25}),
            'feedback': forms.Textarea(attrs={'class': 'w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm', 'rows': 4}),
        }
