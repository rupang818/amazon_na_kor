import os
from django.core.management.base import BaseCommand, CommandError
from account.models import User

class Command(BaseCommand):

    def handle(self, *args, **options):
        username = os.environ['SUPER_USER_EMAIL']
        if not User.objects.filter(email=username).exists():
            User.objects.create_superuser(username,
                                          os.environ['SUPER_USER_PASSWORD'])