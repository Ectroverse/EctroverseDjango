from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from app.models import *
from app.calculations import *
from app.constants import *
from app.helper_functions import *

class Command(BaseCommand): # must be called command, use file name to name the functionality
    @transaction.atomic # Makes it so all object saves get aggregated, otherwise process_tick would take a minute
    def handle(self, *args, **options):
        agent_fleets = Fleet.objects.filter(agent__gt=0, main_fleet=False, command_order=6, ticks_remaining=0)
        for agent_fleet in agent_fleets:
            # perform operation
            if agent_fleet.target_planet is None:
                agent_fleet.command_order = 2
                agent_fleet.save()
                continue

            perform_operation(agent_fleet)
            # (operation, agents, user1, planet):
            status = UserStatus.objects.get(id=agent_fleet.owner.id)
            speed = race_info_list[status.get_race_display()]["travel_speed"]

            # send agents home after operation
            portals = Planet.objects.filter(owner=agent_fleet.owner.id, portal=True)
            if portals is None:
                agent_fleet.command_order = 2 #if no portals the fleet cant return, make it hoover
                agent_fleet.save()
                continue

            portal = find_nearest_portal(agent_fleet.x, agent_fleet.y, portals)
            generate_fleet_order(agent_fleet, portal.x, portal.y, speed, 5, portal.i)


