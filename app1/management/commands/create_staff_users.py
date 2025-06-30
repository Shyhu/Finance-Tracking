from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from app1.models import Staff

class Command(BaseCommand):
    help = 'Create Django users for all staff members'

    def handle(self, *args, **kwargs):
        for staff in Staff.objects.filter(user__isnull=True):
            username = staff.name.lower().replace(" ", "") + str(staff.id)
            password = "staff1234"
            user = User.objects.create_user(username=username, password=password)
            staff.user = user
            staff.save()
            self.stdout.write(self.style.SUCCESS(f'Created user for: {staff.name} -> {username}'))
