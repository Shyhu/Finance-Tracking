from django import forms
from .models import Project

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = '__all__'
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

from django import forms
from .models import Transaction

class MultiFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['transaction_id', 'project', 'type', 'amount', 'vendor', 'status', 'category', 'description']

class FileUploadForm(forms.Form):
    bill_proofs = forms.FileField(widget=MultiFileInput(attrs={'multiple': True}), required=False)
    payment_proofs = forms.FileField(widget=MultiFileInput(attrs={'multiple': True}), required=False)