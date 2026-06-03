import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = "Create or update the production admin user from environment variables."

    def handle(self, *args, **options):
        email = os.environ.get("ADMIN_EMAIL", "").strip().lower()
        password = os.environ.get("ADMIN_PASSWORD", "").strip()
        username = os.environ.get("ADMIN_USERNAME", "").strip()

        if not email or not password:
            return

        if not username:
            username = email.split("@")[0]

        user = User.objects.filter(email__iexact=email).first()
        created = user is None

        if created:
            user = User(
                username=username,
                email=email,
                role=User.ROLE_ADMIN,
                is_staff=True,
                is_superuser=True,
            )
        else:
            user.username = username
            user.role = User.ROLE_ADMIN
            user.is_staff = True
            user.is_superuser = True

        user.set_password(password)
        user.save()

        if created:
            self.stdout.write(self.style.SUCCESS(f"Admin created: {email}"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Admin updated: {email}"))
