from django import forms
from .models import ContactMessage


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm transition',
                'placeholder': 'Your Full Name',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm transition',
                'placeholder': 'you@domain.edu',
            }),
            'subject': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm transition',
                'placeholder': 'Inquiry or Support Topic',
            }),
            'message': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm transition',
                'rows': 4,
                'placeholder': 'Write your message here...',
            }),
        }
