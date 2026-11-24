from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from accounts.models import UserProfile


class Command(BaseCommand):
    help = "Initializes or updates the single authorized platform administrator account."

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, default='admin', help='Administrator username')
        parser.add_argument('--email', type=str, default='admin@placement.edu', help='Administrator email')
        parser.add_argument('--password', type=str, default='AdminPass123!', help='Administrator password')
        parser.add_argument('--force-update', action='store_true', help='Force update password if admin already exists')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']
        force_update = options['force_update']

        existing_admin_profile = UserProfile.objects.filter(role=UserProfile.ROLE_ADMIN).first()

        if existing_admin_profile:
            existing_user = existing_admin_profile.user
            if force_update:
                existing_user.set_password(password)
                existing_user.email = email
                existing_user.is_staff = True
                existing_user.is_superuser = True
                existing_user.save()
                self.stdout.write(self.style.SUCCESS(
                    f"Successfully updated single Administrator account '{existing_user.username}' ({existing_user.email})."
                ))
            else:
                self.stdout.write(self.style.WARNING(
                    f"Single administrator account already exists: '{existing_user.username}' ({existing_user.email}). "
                    f"Use --force-update to update credentials."
                ))
            return

        # No admin profile exists yet. Create the single authorized admin.
        with transaction.atomic():
            user, created = User.objects.get_or_create(username=username, defaults={'email': email})
            user.set_password(password)
            user.email = email
            user.first_name = "Placement"
            user.last_name = "Director"
            user.is_staff = True
            user.is_superuser = True
            user.save()

            UserProfile.objects.update_or_create(
                user=user,
                defaults={'role': UserProfile.ROLE_ADMIN}
            )

        self.stdout.write(self.style.SUCCESS(
            f"Successfully created single authorized Administrator account:\n"
            f"  Username: {username}\n"
            f"  Email:    {email}\n"
            f"  Password: {password}\n"
            f"Role: {UserProfile.ROLE_ADMIN} (Superuser & Platform Admin)"
        ))
