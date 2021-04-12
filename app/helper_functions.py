from .models import *
from app.helper_functions import *
import numpy as np
import miniball
from collections import defaultdict
from .map_settings import *
from .specops import *
from datetime import datetime
from datetime import timedelta
from django.template import RequestContext

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
    Scouting.objects.create(user=status.user, planet=planet, scout=1.0 )

def give_first_fleet(main_fleet):
    for i,unit in enumerate(unit_info["unit_list"]):
        print(i, unit, len(starting_fleet))
        setattr(main_fleet, unit, starting_fleet[i])
    main_fleet.save()

def find_nearest_portal(x, y, portal_list):
    # print("find_nearest_portal",x,y,portal_list)
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
        planet = Planet.objects.filter(x=target_x, y=target_y, i=args[0]).first()
        if planet is not None:
            fleet.target_planet = planet
        # print(fleet.current_position_x,fleet.current_position_y)
    min_dist = np.sqrt((fleet.current_position_x - float(target_x)) ** 2 +
                       (fleet.current_position_y - float(target_y)) ** 2)
    fleet.ticks_remaining = int(np.ceil((min_dist / speed) - 0.001))  # due to rounding and
    # floating points the fleet travel time becomes more than it should, hence the subtraction
    fleet.command_order = order_type


    fleet.save()

def merge_fleets(fleets):
    fleet1 = None
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
    return fleet1

def station_fleets(request, fleets, status):
    stationed_fleets = Fleet.objects.filter(owner=status.id,command_order=1,ticks_remaining=0)
    sf_dict = {}
    for f in stationed_fleets:
        if f.on_planet is not None:
            sf_dict[f.on_planet.id] = f

    for f in fleets:
        planet = Planet.objects.filter(x=f.x, y=f.y, i=f.i).first()
        msg = ""
        fleet_units = ""
        for u in unit_info["unit_list"]:
            if getattr(f, u) > 0:
                fleet_units += str(unit_info[u]['label']) + ": " + str(getattr(f, u)) + " "

        if planet is None:
            f.command_order = 2
            f.save()
            msg = "could not station because it doesn't exist!"
            request.session['error'] = "Could not station on " \
                                       + str(planet.x) + ":" + str(planet.y) + "," + str(planet.i) \
                                       + " because the planet doesnt exist!"
            news_type = 'FU'
        elif planet.owner is None or planet.owner.id != status.id:
            f.command_order = 2
            f.save()
            msg = "could not station because you do not own it!"
            request.session['error'] = "Could not station on " \
                                       + str(planet.x) + ":" + str(planet.y) + "," + str(planet.i) \
                                        + " because you do not own the planet!"
            news_type = 'FU'
        elif planet.id in sf_dict:
            stationed_fleet = sf_dict[planet.id]
            for unit in unit_info["unit_list"]:
                setattr(stationed_fleet, unit, getattr(stationed_fleet, unit) + getattr(f, unit))
            stationed_fleet.command_order=8
            f.delete()
            stationed_fleet.save()
            news_type = 'FS'
            msg = "successfully merged with the other fleet allready stationed on planet: " \
                  + str(planet.x) + ":" + str(planet.y) + "," + str(planet.i) + "!"
        else:
            f.on_planet = planet
            f.command_order = 8
            f.save()
            sf_dict[planet.id] = f
            news_type = 'FS'
            msg = "successfully stationed on planet: " \
                  + str(planet.x) + ":" + str(planet.y) + "," + str(planet.i) + "!"

        News.objects.create(user1=User.objects.get(id=status.id),
                            empire1=status.empire,
                            fleet1=fleet_units,
                            planet=planet,
                            news_type=news_type,
                            date_and_time=datetime.now() + timedelta(seconds=1),
                            is_read=False,
                            is_personal_news=True,
                            is_empire_news=False,
                            tick_number=RoundStatus.objects.get().tick_number,
                            extra_info=msg
                            )



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


def explore_planets(fleets):
    for fl in fleets:
        status = UserStatus.objects.get(user=fl.owner)
        try:
            planet = Planet.objects.get(x=fl.x, y=fl.y, i=fl.i)
        except Planet.DoesNotExist:
            planet = None
        if planet:
            if not planet.home_planet and planet.owner == None:
                planet.owner = fl.owner
                fl.delete()
                planet.save()
                status.military_flag = 1;
                News.objects.create(user1 = fl.owner,
                                    empire1 = status.empire,
                                    news_type = 'SE',
                                    date_and_time=datetime.now(),
                                    is_personal_news=True,
                                    is_empire_news=True,
                                    tick_number = RoundStatus.objects.get().tick_number,
                                    planet = planet)
                Scouting.objects.create(user= fl.owner,
                                        planet = planet,
                                        scout = '1')
            else:
                fl.command_order = 2
                fl.save()
                status.military_flag = 2;
                status.save()
                News.objects.create(user1 = fl.owner,
                                    empire1 = status.empire,
                                    news_type = 'UE',
                                    date_and_time=datetime.now(),
                                    is_personal_news = True,
                                    is_empire_news = True,
                                    tick_number = RoundStatus.objects.get().tick_number,
                                    planet = planet)


def calc_exploration_cost(status):
    expo_ship_nr = Fleet.objects.filter(owner = status.user, main_fleet = False, exploration = 1).count()
    pl_number = Planet.objects.filter(owner = status.user).count()
    return (pl_number + expo_ship_nr + 40) >> 2


def get_userstatus_from_id_or_name(d):
    try:
        detail = int(d)
    except ValueError:
        detail = str(d)

    faction_setting = None
    err_msg = ""

    if isinstance(detail, int):
        if UserStatus.objects.filter(id=detail).first() is None:
            err_msg += "The faction id " + str(detail) + " doesn't exist!"
        else:
            faction_setting = UserStatus.objects.filter(id=detail).first()
    else:
        if UserStatus.objects.filter(user_name=detail).first() is None:
            err_msg += "The faction name " + str(detail) + " doesn't exist!"
        else:
            faction_setting = UserStatus.objects.filter(user_name=detail).first()

    return faction_setting, err_msg


def send_agents_ghosts(status, agents, ghosts, x, y, i, specop):
    x = int(x)
    y = int(y)
    i = int(i)
    planet = Planet.objects.filter(x=x, y=y, i=i).first()
    if planet is None:
        return "This planet doesn't exist!"
    portal_planets = Planet.objects.filter(owner=status.user, portal=True)
    if not portal_planets:
        return "You need at least one portal to send the fleet from!"
    best_portal_planet = find_nearest_portal(x, y, portal_planets)
    min_dist = np.sqrt((best_portal_planet.x - x) ** 2 + (best_portal_planet.y - y) ** 2)
    speed = race_info_list[status.get_race_display()]["travel_speed"]  # * specopEnlightemntCalc(id,CMD_ENLIGHT_SPEED);
    fleet_time = int(np.ceil(min_dist / speed))
    fleet = Fleet.objects.create(owner=status.user,
                         command_order=6,
                         target_planet=planet,
                         x=x,
                         y=y,
                         i=i,
                         ticks_remaining=fleet_time,
                         current_position_x=best_portal_planet.x,
                         current_position_y=best_portal_planet.y,
                         agent=agents,
                         ghost=ghosts,
                         specop=specop)
    main_fleet = Fleet.objects.get(owner=status.user.id, main_fleet=True)
    main_fleet.agent -= agents
    main_fleet.ghost -= ghosts
    main_fleet.save()
    if fleet_time == 0:
        if agents > 0:
            perform_operation()
        if ghosts > 0:
            perform_incantation()

