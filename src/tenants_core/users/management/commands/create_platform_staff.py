"""
Management command to create a platform staff user.
"""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

User = get_user_model()


class Command(BaseCommand):
    help = 'Create a platform staff user who can access platform admin'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Email address for the platform staff user')
        parser.add_argument(
            '--superuser',
            action='store_true',
            help='Also grant superuser access (full platform control)',
        )

    def handle(self, *args, **options):
        email = options['email']
        is_superuser = options['superuser']

        # Check if user already exists
        if User.objects.filter(email=email).exists():
            raise CommandError(f'User with email "{email}" already exists')

        # Get password from stdin
        import getpass
        password = getpass.getpass('Password: ')
        password_confirm = getpass.getpass('Password (again): ')

        if password != password_confirm:
            raise CommandError('Passwords do not match')

        # Create user
        if is_superuser:
            user = User.objects.create_superuser(
                email=email,
                password=password
            )
            self.stdout.write(
                self.style.SUCCESS(f'✓ Created SUPERUSER: {email}')
            )
            self.stdout.write(
                self.style.WARNING('  ⚠ This user has FULL platform access!')
            )
        else:
            user = User.objects.create_user(
                email=email,
                password=password,
                is_staff=True,
                is_platform_staff=True,
                is_superuser=False
            )
            self.stdout.write(
                self.style.SUCCESS(f'✓ Created platform staff user: {email}')
            )
            self.stdout.write(
                '  • Can access platform admin at http://localhost:8000/admin/'
            )
            self.stdout.write(
                '  • Use Django groups to control specific permissions'
            )
            self.stdout.write(
                '  • Cannot access tenant admins (unless given TenantMembership)'
            )

        self.stdout.write('')
        self.stdout.write('Next steps:')
        if not is_superuser:
            self.stdout.write('  1. Add user to a Django group for specific permissions:')
            self.stdout.write('     python manage.py add_to_group {email} "Platform: Tenant Manager"')
            self.stdout.write('  2. Or manage permissions via admin at http://localhost:8000/admin/')
        else:
            self.stdout.write('  1. User can access platform admin at http://localhost:8000/admin/')
            self.stdout.write('  2. User has full access to all platform features')
