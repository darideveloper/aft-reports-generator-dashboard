import os

from django.core.management.base import BaseCommand

from survey import models

BASE_FILE = os.path.basename(__file__)


class Command(BaseCommand):
    help = "Delete all test responses (users like 'user_<random_string>@test.com')"

    def handle(self, *args, **kwargs):

        # Get random company and survey
        users = models.Participant.objects.filter(email__startswith="user_")
        print(f"Deleting {users.count()} test users")
        users.delete()
        print("Users deleted")
