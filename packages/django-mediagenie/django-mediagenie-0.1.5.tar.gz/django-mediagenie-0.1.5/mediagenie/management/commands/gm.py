from django.core.management.base import NoArgsCommand
from mediagenie.env import get_env
from mediagenie.generate import generate_media

class Command(NoArgsCommand):
    requires_model_validation = False

    def handle(self, *args, **options):
        generate_media(parallelism=get_env().parallelism)
