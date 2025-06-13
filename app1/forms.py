from django import forms
from .models import Project

# class ProjectForm(forms.ModelForm):
#     class Meta:
#         model = Project
#         fields = '__all__'
#         widgets = {
#             'start_date': forms.DateInput(attrs={'type': 'date'}),
#             'end_date': forms.DateInput(attrs={'type': 'date'}),
#         }
from django import forms
from .models import Project

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['code', 'name', 'location', 'total_budget', 'start_date', 'end_date', 'notes']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'total_budget': forms.NumberInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
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


from django import forms
from .models import Loan

class LoanForm(forms.ModelForm):
    class Meta:
        model = Loan
        exclude = ('created_at', 'updated_at')  # fixed spelling
        widgets = {
            'loan_id': forms.TextInput(attrs={'class': 'form-control'}),
            'project': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'interest_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'purpose': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'repayment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


# forms.py
from django import forms
from .models import Repayment

class RepaymentForm(forms.ModelForm):
    class Meta:
        model = Repayment
        fields = ['date', 'amount_paid']



from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['task_id', 'date', 'staff', 'project', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

# Just use a plain file input in HTML instead of this:
# class TaskFileForm(forms.ModelForm):
#     class Meta:
#         model = TaskFile
#         fields = ['file']
