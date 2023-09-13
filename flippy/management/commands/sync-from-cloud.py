from django.core.management.base import BaseCommand, CommandError
from flippy.config import flippy_backend
from flippy.backends import FlipperCloudBackend
from os import environ

try:
    TOKEN = environ['FLIPPER_CLOUD_TOKEN']
except KeyError:
    TOKEN = None


class Command(BaseCommand):
    help = "Sync from Flipper Cloud to another backend"

    def handle(self, *args, **options):
        if not TOKEN:
            raise CommandError(
                "FLIPPER_CLOUD_TOKEN must be set in the environment for sync to operate"
            )

        if isinstance(flippy_backend, FlipperCloudBackend):
            raise CommandError(
                "Will not sync from Flipper Cloud back to Flipper Cloud"
            )

        source = FlipperCloudBackend(TOKEN)
        flippy_backend.from_json(source.to_json())

        self.stdout.write(
            self.style.SUCCESS(
                f"Completed sync from {source.__class__.__name__} "
                f"to {flippy_backend.__class__.__name__}"
            )
        )
