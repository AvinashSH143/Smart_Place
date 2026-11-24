from django import forms

# Import DisciplineRecord for DebarmentForm
from discipline.models import DisciplineRecord
from .models import StudentProfile, StudentSkill, Skill


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = [
            'full_name',
            'branch',
            'year_of_study',
            'cgpa',
            'contact_phone',
            'bio',
            'profile_picture',
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm transition',
            }),
            'branch': forms.Select(attrs={
                'class': 'w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm transition',
            }),
            'year_of_study': forms.Select(attrs={
                'class': 'w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm transition',
            }),
            'cgpa': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm transition',
                'step': '0.01',
                'min': '0.00',
                'max': '10.00',
            }),
            'contact_phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm transition',
                'placeholder': '+1 (555) 000-0000',
            }),
            'bio': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm transition',
                'rows': 3,
                'placeholder': 'Brief summary of your academic focus and career aspirations...',
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'w-full text-sm text-slate-400 file:mr-4 file:py-2.5 file:px-4 file:rounded-xl file:border-0 file:text-sm file:font-medium file:bg-indigo-600 file:text-white hover:file:bg-indigo-500 cursor-pointer',
            }),
        }

# ----- New Form for Appeal Review -----

class DebarmentForm(forms.ModelForm):
    """Form for admin to set debarment details on a DisciplineRecord.
    Includes fields for debarred status, start/end dates, placement restrictions,
    and admin decision notes.
    """
    class Meta:
        model = DisciplineRecord
        fields = [
            'is_debarred',
            'debarment_start',
            'debarment_end',
            'placement_restrictions',
            'admin_decision_notes',
        ]
        widgets = {
            'is_debarred': forms.CheckboxInput(attrs={'class': 'w-4 h-4 rounded text-indigo-600 focus:ring-indigo-500 bg-slate-900 border-slate-700'}),
            'debarment_start': forms.DateInput(attrs={'class': 'w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm', 'type': 'date'}),
            'debarment_end': forms.DateInput(attrs={'class': 'w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm', 'type': 'date'}),
            'placement_restrictions': forms.Textarea(attrs={'class': 'w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm', 'rows': 3, 'placeholder': 'Enter placement restrictions...'}),
            'admin_decision_notes': forms.Textarea(attrs={'class': 'w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm', 'rows': 4, 'placeholder': 'Admin decision notes...'}),
        }

class AppealReviewForm(forms.Form):
    """Form used by admins to review a disciplinary appeal.

    * ``decision`` – choose to approve or reject the appeal.
    * ``admin_response`` – optional free‑text notes for the student and record.
    """

    DECISION_APPROVE = 'APPROVE'
    DECISION_REJECT = 'REJECT'

    decision = forms.ChoiceField(
        choices=[
            (DECISION_APPROVE, 'Approve Appeal (Reinstate student)') ,
            (DECISION_REJECT, 'Reject Appeal (Maintain penalty)')
        ],
        widget=forms.RadioSelect(attrs={
            'class': 'text-white',
        })
    )
    admin_response = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm',
            'rows': 4,
            'placeholder': 'Add any remarks or justification for this decision...'
        })
    )


class AddStudentSkillForm(forms.ModelForm):
    class Meta:
        model = StudentSkill
        fields = ['skill', 'proficiency']
        widgets = {
            'skill': forms.Select(attrs={
                'class': 'w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm transition',
            }),
            'proficiency': forms.Select(attrs={
                'class': 'w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm transition',
            }),
        }
