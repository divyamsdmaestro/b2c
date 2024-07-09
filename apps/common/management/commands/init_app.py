from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Initializes the app by running the necessary initial commands."

    def handle(self, *args, **kwargs):
        """Call all the necessary commands."""

        # application db migrate
        call_command("migrate")
