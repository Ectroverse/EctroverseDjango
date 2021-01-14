from .models import *
from app.helper_functions import *
import numpy as np
import miniball
from collections import defaultdict
from .map_settings import *


def give_first_planet(user, status, planet):
    planet.solar_collectors = staring_solars
    planet.mineral_plants = starting_meral_planets
    planet.refinement_stations = starting_ectrolium_refs
    planet.crystal_labs = starting_crystal_labs
    planet.cities = starting_cities
    planet.portal = True
    planet.owner = user
    planet.save()
    status.home_planet = planet
    status.num_planets = 1
    status.save()

def give_first_fleet(main_fleet):
    for i,unit in enumerate(unit_info["unit_list"]):
        print(i, unit, len(starting_fleet))
        setattr(main_fleet, unit, starting_fleet[i])
    main_fleet.save()

def find_nearest_portal(x, y, portal_list):
    print("find_nearest_portal",x,y,portal_list)
    min_dist = (portal_list[0].x- x)**2+ (portal_list[0].y -y)**2;
    portal = portal_list[0]
    for p in portal_list:
        dist = (p.x-x)**2 + (p.y-y)**2
        print(p.x,p.y, dist)
        if dist < min_dist:
            min_dist = dist
            portal = p
    return portal

# use this function to find the minimum max distance from all systems to
def find_bounding_circle(systems):
    S = np.array(systems)
    # The algorithm implemented is Welzl’s algorithm. It is a pure Python implementation,
    # it is not a binding of the popular C++ package Bernd Gaertner’s miniball.
    # The algorithm, although often presented in its recursive form, is here implemented in an iterative fashion.
    # Python have an hard-coded recursion limit, therefore a recursive implementation of Welzl’s
    # algorithm would have an artificially limited number of point it could process.
    C, r2 = miniball.get_bounding_ball(S)
    return C

# option value="0" Attack the planet
# option value="1" Station on planet
# option value="2" Move to system
# option value="3" Merge in system (chose system yourself)
# option value="4" Merge in system (auto/optimal)
# option value="5" Join main fleet
def generate_fleet_order(fleet, target_x, target_y, speed, order_type, *args):
    # args[0] - planet number
    fleet.x = target_x
    fleet.y = target_y
    if args:
        fleet.i = args[0]
    print(fleet.current_position_x,fleet.current_position_y)
    min_dist = np.sqrt((fleet.current_position_x - float(target_x)) ** 2 +
                       (fleet.current_position_y - float(target_y)) ** 2)
    print("min_dist",min_dist,speed)
    fleet.ticks_remaining = int(np.ceil((min_dist / speed) - 0.001))  # due to rounding and
    # floating points the fleet travel time becomes more than it should, hence the subtraction
    fleet.command_order = order_type
    fleet.save()
    
def merge_fleets(fleets):
    d = defaultdict(list)
    for fl in fleets:
        coords = 'x' + str(fl.x) + 'y' + str(fl.y)
        d[coords].append(fl)
    for coord,fleet in d.items():
        fleet1 = fleet[0]
        for i in range(1,len(fleet)):
            for unit in unit_info["unit_list"]:
                setattr(fleet1, unit, getattr(fleet1, unit) + getattr(fleet[i], unit))
            fleets[i].delete()
        fleet1.save()


def join_main_fleet(main_fleet, fleets):
    for fl in fleets:
        for unit in unit_info["unit_list"]:
            setattr(main_fleet, unit, getattr(main_fleet, unit) + getattr(fl, unit))
        fl.delete()
    main_fleet.save()

def split_fleets(fleets, split_pct):
    for fl in fleets:
        fl2 = {}
        total_fl2 = 0
        for i, unit in enumerate(unit_info["unit_list"]):
            unit_num = int(getattr(fl, unit)*split_pct/100)
            fl2[unit] = unit_num
            setattr(fl, unit, getattr(fl, unit) - unit_num)
            total_fl2 += unit_num
            fl.save()
        if total_fl2 > 0:
            Fleet.objects.create(owner=fl.owner,
                                 command_order=fl.command_order,
                                 x=fl.x,
                                 y=fl.y,
                                 i=fl.i,
                                 ticks_remaining=fl.ticks_remaining,
                                 current_position_x=fl.current_position_x,
                                 current_position_y=fl.current_position_y,
                                 **fl2)
