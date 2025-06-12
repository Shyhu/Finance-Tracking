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
