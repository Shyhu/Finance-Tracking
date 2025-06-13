from django.contrib import admin
from app1.models import Project,Transaction,Category,Loan
# Register your models here.
admin.site.register(Project)
admin.site.register(Transaction)
admin.site.register(Category)
admin.site.register(Loan)