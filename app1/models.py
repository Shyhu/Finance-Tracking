from django.db import models

# Create your models here.
from django.contrib.auth.models import User

from django.db import models

class Project(models.Model):
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    total_budget = models.DecimalField(max_digits=12, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name



class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('Income', 'Income'),
        ('Expense', 'Expense'),
    )

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=50)
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    vendor = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=50, default="Approved")
    category = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True,null=True)

    def __str__(self):
        return f"{self.transaction_id} - {self.project.name}"

class BillProof(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='bill_proofs')
    file = models.FileField(upload_to='bill_proofs/')

class PaymentProof(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='payment_proofs')
    file = models.FileField(upload_to='payment_proofs/')




class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,null=True, blank=True)
    staff_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='staff_photos/', blank=True, null=True)
    designation = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    date_of_join = models.DateField()

    def __str__(self):
        return self.name
    


class Loan(models.Model):

    
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    loan_id = models.CharField(max_length=50,unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_proof = models.FileField(upload_to='loan_payment_proofs/', null=True, blank=True)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, help_text='annual Interest in %')
    loan_purpose = models.CharField(max_length=100)
    start_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.loan_id} - {self.project.name}"
    
    class Meta:
        verbose_name = 'Loan'
        verbose_name_plural = 'Loans'
        ordering = ['-start_date']



# models.py
from decimal import Decimal
from django.db import models

class Repayment(models.Model):
    loan = models.ForeignKey('Loan', on_delete=models.CASCADE, related_name='repayments')
    date = models.DateField()
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    interest_calculated = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    interest_paid = models.DecimalField(max_digits=10, decimal_places=2)
    principal_paid = models.DecimalField(max_digits=10, decimal_places=2)
    balance_after_repayment = models.DecimalField(max_digits=10, decimal_places=2)
    photo_proof = models.ImageField(upload_to='repayment_proofs/', null=True, blank=True)

    def __str__(self):
        return f"{self.loan.project.name} - {self.date} - ₹{self.amount_paid}"





from django.db import models

class Task(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]

    task_id = models.CharField(max_length=50, unique=True)
    date = models.DateField()
    due_date = models.DateField(null=True, blank=True)  # ✅ New
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')  # ✅ New
    staff = models.ForeignKey('Staff', on_delete=models.CASCADE)
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    description = models.TextField()
    voice_memo = models.FileField(upload_to='voice_memos/', blank=True, null=True)

    def __str__(self):
        return self.task_id


class TaskFile(models.Model):
    task = models.ForeignKey(Task, related_name='files', on_delete=models.CASCADE)
    file = models.FileField(upload_to='task_files/')


# models.py

class StaffMessage(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.staff.name}"
    



from django.db import models
from django.contrib.auth import get_user_model
from app1.models import Staff, Project

User = get_user_model()

class Target(models.Model):
    date = models.DateField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.staff.name} - {self.date}"
    

