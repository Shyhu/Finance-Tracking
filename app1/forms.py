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
from django import forms
from .models import Staff

class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['staff_id', 'name', 'photo', 'designation', 'department', 'project', 'salary', 'date_of_join']
        labels = {
            'staff_id': 'Staff ID',
            'name': 'Full Name',
            'photo': 'Photo',
            'designation': 'Designation',
            'department': 'Department',
            'project': 'Project Assigned',
            'salary': 'Monthly Salary',
            'date_of_join': 'Date of Joining',
        }
        widgets = {
            'staff_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter unique staff ID'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter full name'
            }),
            'photo': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
            'designation': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter designation (e.g., Manager)'
            }),
            'department': forms.Select(attrs={
                'class': 'form-select'
            }),
            'project': forms.Select(attrs={
                'class': 'form-select'
            }),
            'salary': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter salary amount'
            }),
            'date_of_join': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
        }

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
from django import forms
from .models import Repayment

class RepaymentForm(forms.ModelForm):
    class Meta:
        model = Repayment
        fields = ['date', 'amount_paid']
        labels = {
            'date': 'Repayment Date',
            'amount_paid': 'Amount Paid (₹)',
        }
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'placeholder': 'Select repayment date'
            }),
            'amount_paid': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter amount paid'
            }),
        }




from django import forms
from .models import Task
from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['task_id', 'date', 'staff', 'project', 'description']
        labels = {
            'task_id': 'Task ID',
            'date': 'Task Date',
            'staff': 'Assigned Staff',
            'project': 'Related Project',
            'description': 'Task Description',
        }
        widgets = {
            'task_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter unique task ID'
            }),
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'staff': forms.Select(attrs={
                'class': 'form-select'
            }),
            'project': forms.Select(attrs={
                'class': 'form-select'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter task details or instructions'
            }),
        }

# Just use a plain file input in HTML instead of this:
# class TaskFileForm(forms.ModelForm):
#     class Meta:
#         model = TaskFile
#         fields = ['file']
