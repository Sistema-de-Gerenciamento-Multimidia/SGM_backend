# images/management/commands/createsu.py

from users.models import CustomUser
from django.core.management.base import BaseCommand

# Create superuser before deploy
class Command(BaseCommand):
    help = 'Creates a superuser.'

    def handle(self, *args, **options):
        if not CustomUser.objects.filter(username='admin').exists():
            CustomUser.objects.create_superuser(
                username='admin',
                password='abc12345678',
                email="admin@email.com",
                name="Admin User"
            )
        print('Superuser has been created.')
