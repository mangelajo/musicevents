import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()


class Command(BaseCommand):
    help = 'Ensures that an admin user exists with the specified credentials'

    def handle(self, *args, **options):
        username = os.environ.get('ADMIN_USERNAME')
        password = os.environ.get('ADMIN_PASSWORD')
        email = os.environ.get('ADMIN_EMAIL', f'{username}@example.com')

        if not username or not password:
            self.stdout.write(
                self.style.WARNING(
                    'Admin user not created: ADMIN_USERNAME and/or ADMIN_PASSWORD environment variables not set'
                )
            )
            return

        try:
            admin_user = User.objects.get(username=username)
            # Ensure the user has admin privileges, but don't change the password
            if not admin_user.is_staff or not admin_user.is_superuser:
                admin_user.is_staff = True
                admin_user.is_superuser = True
                admin_user.save()
                self.stdout.write(
                    self.style.SUCCESS(f'Admin user "{username}" updated with admin privileges')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f'Admin user "{username}" already exists')
                )
        except User.DoesNotExist:
            try:
                User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Admin user "{username}" created successfully')
                )
            except IntegrityError:
                self.stdout.write(
                    self.style.ERROR(f'Could not create admin user "{username}" - username or email already exists')
                )