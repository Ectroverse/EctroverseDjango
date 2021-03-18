from django.core.management.base import BaseCommand, CommandError
from app.models import *
from app.calculations import *
from app.constants import *
import time
import matplotlib.pyplot as plt
import random
from app.map_settings import *
from django.db import transaction

def random_combination(iterable, r):
    pool = tuple(iterable)
    n = len(pool)
    indices = sorted(random.sample(range(n), r))
    return tuple(pool[i] for i in indices)


def fill_system(x,y):
    planet_buffer_fill = []
    planets_in_system = np.random.randint(1,9) # max of 8 planets per system with the way we are visualizing it
    positions = random_combination(range(8), planets_in_system)
    for i in range(planets_in_system):
        size = planet_size_distribution()
        planet_buffer_fill.append(Planet(home_planet=False,
                                         x=x,
                                         y=y,
                                         i=i,
                                         pos_in_system=positions[i],
                                         current_population=size*population_base_factor,
                                         size=size)) # create is the same as new() and add()
    return planet_buffer_fill


class Command(BaseCommand): # must be called command, use file name to name the functionality
    @transaction.atomic
    def handle(self, *args, **options):
        start_t = time.time()
        Planet.objects.all().delete() # remove all planets
        Empire.objects.all().delete() # remove all empires
        RoundStatus.objects.all().delete()
        Relations.objects.all().delete()
        News.objects.all().delete()
        Construction.objects.all().delete()
        Fleet.objects.all().delete()
        UnitConstruction.objects.all().delete()
        Messages.objects.all().delete()
        planet_buffer = [] # MUCH quicker to save them all at once, like 100x faster
        empires_buffer = []
        RoundStatus.objects.create()

        # We also need to purge all the non-needed info of players, without actualy deleting them!
        theta = 0
        for j in range(num_homes):
            home_x = round(distance*np.sin(theta) + map_size/2)
            home_y = round(distance*np.cos(theta) + map_size/2)
            theta += 2*np.pi/num_homes
            empires_buffer.append(Empire(number=j,
                                         x=home_x,
                                         y=home_y,
                                         name="Empire",
                                         name_with_id="Empire #" + str(j),
                                         pm_message="Welcome to empire #" + str(j)

            ))
            for i in range(players_per_empire): # max 8 players per empire/system
                size = 400
                planet_buffer.append(Planet(home_planet=True,
                                            x=home_x,
                                            y=home_y,
                                            i=i,
                                            pos_in_system=i,
                                            current_population=size*population_base_factor,
                                            size=size)) # create is the same as new() and add()


            # Now add N planets in a small area around the home planet
            N = 6
            d_from_home = 3
            history = []
            while len(history) < N:
                x = np.random.randint(-1*d_from_home, d_from_home+1) + home_x
                y = np.random.randint(-1*d_from_home, d_from_home+1) + home_y
                if (x,y) not in history:
                    history.append((x,y))
                    planet_buffer.extend(fill_system(x,y))

        # Main core in the center
        for x in range(map_size):
            for y in range(map_size):
                d_to_center = max(0, map_size*0.4 - np.sqrt((x-map_size/2)**2 + (y-map_size/2)**2))/(map_size*0.4) # between 0 and 1, higher is closer to center
                density = 0.3 # between 0 and 1
                roll_off_factor = 2.0 # higher means more planets clustered in the middle
                if (np.random.rand() < d_to_center**roll_off_factor) and (np.random.rand() < density): # higher density towards center of map, everyone starts towards the perimeter
                    planet_buffer.extend(fill_system(x,y))

        start_tt = time.time()
        Planet.objects.bulk_create(planet_buffer)
        Empire.objects.bulk_create(empires_buffer)
        print("Saving planets to db took this many seconds", time.time() - start_tt)

        # reset round user data
        for status in UserStatus.objects.all():

            Fleet.objects.create(owner=status.user, main_fleet=True)

            status.fleet_readiness = 100
            status.psychic_readiness = 100
            status.agent_readiness = 100

            # Loop through user's planets, lines 499 - 608 in cmdtick.c
            status.population = 0  # clear user's population
            status.num_planets = 1
            status.total_solar_collectors = 0
            status.total_fission_reactors = 0
            status.total_mineral_plants = 0
            status.total_crystal_labs = 0
            status.total_refinement_stations = 0
            status.total_cities = 0
            status.total_research_centers = 0
            status.total_defense_sats = 0
            status.total_shield_networks = 0
            status.total_portals = 0

            status.total_buildings = 0

            status.research_points_military = 0
            status.research_points_construction = 0
            status.research_points_tech = 0
            status.research_points_energy = 0
            status.research_points_population = 0
            status.research_points_culture = 0
            status.research_points_operations = 0
            status.research_points_portals = 0

            status.current_research_funding = 0

            status.research_percent_military = 0
            status.research_percent_construction = 0
            status.research_percent_tech = 0
            status.research_percent_energy = 0
            status.research_percent_population = 0
            status.research_percent_culture = 0
            status.research_percent_operations = 0
            status.research_percent_portals = 0


            status.energy_production = 0
            status.energy_decay = 0
            status.buildings_upkeep = 0
            status.units_upkeep = 0
            status.population_upkeep_reduction = 0
            status.portals_upkeep = 0
            status.population_upkeep_reduction = 0

            status.crystal_production = 0
            status.crystal_decay = 0
            status.mineral_production = 0
            status.ectrolium_production = 0

            status.energy_income = 0
            status.mineral_income = 0
            status.crystal_income = 0
            status.ectrolium_income = 0

            status.energy_interest = 0
            status.mineral_interest = 0
            status.crystal_interest = 0
            status.ectrolium_interest = 0
            status.energy = 120000
            status.minerals = 10000
            status.crystals = 5000
            status.ectrolium = 5000

            status.networth += 1
            status.save()


        # TEMPORARY - assign all planets to admin user, for debugging sake
        # all_planets = Planet.objects.all()
        # all_planets_without_home = Planet.objects.all().filter(home_planet=False)
        # all_planets_without_home.update(owner=User.objects.get(username='admin'))

        #Give empire 0 to the admin
        # admin = UserStatus.objects.get(user=User.objects.get(username='admin'))
        # admin.empire = Empire.objects.get(number=0)
        # empire0 = Empire.objects.get(number=0)
        # empire0.numplayers = 1
        # empire0.save()
        # admin.save()


        # num_planets = all_planets.count()
        # print("Num planets:", num_planets)
        print("Generating planetsand resetting users took " + str(time.time() - start_t) + "seconds")
