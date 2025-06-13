from django.db import models

# Create your models here.

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
    created_at = models.DateTimeField(auto_now_add=True,null=True)

    def __str__(self):
        return f"{self.transaction_id} - {self.project.name}"

class BillProof(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='bill_proofs')
    file = models.FileField(upload_to='bill_proofs/')

class PaymentProof(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='payment_proofs')
    file = models.FileField(upload_to='payment_proofs/')




class Staff(models.Model):
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
    loan_id = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
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

