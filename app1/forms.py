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



# forms.py
from django import forms
from .models import Transaction

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['transaction_id', 'project', 'type', 'amount', 'vendor', 'status', 'category', 'description']



from django import forms
from .models import Staff,Loan

class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['staff_id', 'name', 'photo', 'designation', 'department', 'project', 'salary', 'date_of_join']



class LoanForm(forms.ModelForm):
    class Meta:
        model = Loan
        fields = '__all__'
        exlude = ('created_at' , 'updated_at')
