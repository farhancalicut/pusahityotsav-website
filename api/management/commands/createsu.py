# In api/management/commands/createsu.py

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Creates a superuser'

    def handle(self, *args, **options):
        User = get_user_model()

        # --- IMPORTANT: FILL IN YOUR DETAILS HERE ---
        username = "admin"
        email = "muhammedfarhant6@gmail.com"
        password = "adminpu12"
        # -----------------------------------------

        if not User.objects.filter(username=username).exists():
            self.stdout.write(f'Creating account for {username} ({email})')
            User.objects.create_superuser(email=email, username=username, password=password)
        else:
            self.stdout.write(f'Superuser with username "{username}" already exists.')