from django import forms
from .models import Submission

class SkillForm(forms.Form):
    skills = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows':3, 'placeholder':'e.g., Python, Django, SQL'}),
        label='Skills (optional)'
    )
    resume = forms.FileField(required=False, label='Resume (optional)')

class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['name', 'email', 'skills', 'resume']
from .models import ResumeSubmission

class ResumeSubmissionForm(forms.ModelForm):
    class Meta:
        model = ResumeSubmission
        fields = ['name', 'email','resume']

from .models import ContactMessage

class ContactMessageForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        

