from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from app.models import *
from app.calculations import *
from app.constants import *
from app.helper_functions import *

class Command(BaseCommand): # must be called command, use file name to name the functionality
    @transaction.atomic # Makes it so all object saves get aggregated, otherwise process_tick would take a minute
    def handle(self, *args, **options):
        scouting1 = Scouting.objects.filter(user= User.objects.get(id=1))
        scouting2 = Scouting.objects.filter(user= User.objects.get(id=2))

        planets ={}
        for s1 in scouting1:
            planets[s1.planet.id] = s1

        for s2 in scouting2:
            if s2.planet.id in planets:
                tmp_scouting = planets[s2.planet.id]
                tmp_scouting.scout = max(tmp_scouting.scout, s2.scout)
                tmp_scouting.save()
            else:
                Scouting.objects.create(user=User.objects.get(id=1),
                                        planet=s2.planet,
                                        scout=s2.scout)
