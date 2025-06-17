from django.contrib import admin
from app1.models import Project,Transaction,Category,Loan,Repayment,Staff,Task,StaffMessage,Target
# Register your models here.
admin.site.register(Project)
admin.site.register(Transaction)
admin.site.register(Category)
admin.site.register(Loan)
admin.site.register(Repayment)
admin.site.register(Staff)
admin.site.register(Task)
admin.site.register(Target)




class StaffMessageAdmin(admin.ModelAdmin):
    list_display = ('staff', 'timestamp', 'message', 'is_read')

admin.site.register(StaffMessage, StaffMessageAdmin)
