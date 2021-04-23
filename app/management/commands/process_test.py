from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from app.models import *
from app.calculations import *
from app.constants import *
from app.helper_functions import *
from machina import MACHINA_MAIN_STATIC_DIR
from machina import MACHINA_MAIN_TEMPLATE_DIR

class Command(BaseCommand): # must be called command, use file name to name the functionality
    @transaction.atomic # Makes it so all object saves get aggregated, otherwise process_tick would take a minute
    def handle(self, *args, **options):
        print(MACHINA_MAIN_TEMPLATE_DIR)
        print(MACHINA_MAIN_STATIC_DIR)