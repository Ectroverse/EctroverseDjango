from .models import *
from app.helper_functions import *


def give_first_planet(user, status, planet):
    planet.solar_collectors = staring_solars
    planet.mineral_plants = starting_meral_planets
    planet.refinement_stations = starting_ectrolium_refs
    planet.crystal_labs = starting_crystal_labs
    planet.cities = starting_cities
    planet.owner = user
    planet.save()
    status.home_planet = planet
    status.num_planets = 1
    status.save()

