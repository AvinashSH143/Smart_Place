from django import forms
from .models import DisciplineRecord, DisciplineAppeal


class DisciplineRecordForm(forms.ModelForm):
    """Form for creating a new DisciplineRecord.
    """
    class Meta:
        model = DisciplineRecord
        fields = [
            "student",
            "incident_category",
            "incident_date",
            "description",
            "supporting_evidence",
        ]
        widgets = {
            "student": forms.Select(attrs={
                "class": "w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm",
            }),
            "incident_category": forms.Select(attrs={
                "class": "w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm",
            }),
            "incident_date": forms.DateInput(attrs={
                "class": "w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm",
                "type": "date",
            }),
            "description": forms.Textarea(attrs={
                "class": "w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm",
                "rows": 4,
            }),
            "supporting_evidence": forms.FileInput(attrs={
                "class": "w-full text-sm text-slate-400 file:mr-4 file:py-2.5 file:px-4 file:rounded-xl file:border-0 file:text-sm file:font-medium file:bg-indigo-600 file:text-white hover:file:bg-indigo-500 cursor-pointer",
            }),
        }

# ----- Appeal Review Form -----

class AppealReviewForm(forms.Form):
    """Form used by admins to review a disciplinary appeal.
    * ``decision`` – approve or reject.
    * ``admin_response`` – optional notes.
    """
    DECISION_APPROVE = 'APPROVE'
    DECISION_REJECT = 'REJECT'

    decision = forms.ChoiceField(
        choices=[
            (DECISION_APPROVE, 'Approve Appeal (Reinstate student)'),
            (DECISION_REJECT, 'Reject Appeal (Maintain penalty)')
        ],
        widget=forms.RadioSelect(attrs={'class': 'text-white'})
    )
    admin_response = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm',
            'rows': 4,
            'placeholder': 'Add any remarks or justification for this decision...'
        })
    )


class DisciplineAppealForm(forms.ModelForm):
    class Meta:
        model = DisciplineAppeal
        fields = ["appeal_statement", "supporting_document"]
        widgets = {
            "appeal_statement": forms.Textarea(
                attrs={
                    "class": "w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm transition",
                    "rows": 5,
                    "placeholder": "Provide a detailed, respectful explanation detailing any mitigating circumstances, evidence, or points of appeal for the Disciplinary Board review...",
                }
            ),
            "supporting_document": forms.FileInput(
                attrs={
                    "class": "w-full text-sm text-slate-400 file:mr-4 file:py-2.5 file:px-4 file:rounded-xl file:border-0 file:text-sm file:font-medium file:bg-indigo-600 file:text-white hover:file:bg-indigo-500 cursor-pointer",
                }
            ),
        }
