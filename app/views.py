from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from .models import *
from .constants import *
from .calculations import *
from .helper_classes import *
from .tables import *
from .forms import *
from django.contrib.auth.decorators import login_required
from django.templatetags.static import static
from io import BytesIO
import base64
from django_tables2 import SingleTableView
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash, logout, authenticate, login
from .forms import RegisterForm
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.template import RequestContext
from django.db.models import Q
from django.contrib.auth.decorators import user_passes_test
from app.map_settings import *
from app.helper_functions import *

import json
import numpy as np
import time
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from datetime import datetime

# Remember that Django uses the word View to mean the Controller in MVC.  Django's "Views" are the HTML templates. Models are models.


def race_check(user):
    if not user.userstatus.race or not user.userstatus.empire:
        return False
    else:
        return True

def reverse_race_check(user):
    if not user.userstatus.race or not user.userstatus.empire:
        return True
    else:
        return False

def index(request):
    context = {"news_feed": NewsFeed.objects.all().order_by('-date_and_time')}
    return render(request, "login.html", context)

def guide(request):
    return render(request, "guide.html")

def faq(request):
    return render(request, "faq.html")

def custom_login(request):
    username = request.POST['username']
    password = request.POST['password']

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect("/choose_empire_race")
    else:
        context = {"news_feed": NewsFeed.objects.all().order_by('-date_and_time'),
                   "errors": "Wrong username/password!"}
        return render(request, "login.html", context)

# In contrast to HttpRequest objects, which are created automatically by Django, HttpResponse objects are your responsibility. Each view you write is responsible for instantiating, populating, and returning an HttpResponse.
# The HttpResponse class lives in the django.http module.
def register(response):
    if response.method == "POST":
        form = RegisterForm(response.POST)
        if form.is_valid():
            form.save()
            new_user = authenticate(username=form.cleaned_data['username'],
                                    password=form.cleaned_data['password1'],
                                    )
            print(new_user.userstatus.user_name)
            status = get_object_or_404(UserStatus, user=new_user)
            status.user_name = form.cleaned_data['game_name']
            status.save()
            print(status.user_name, form.cleaned_data['game_name'])
            login(response, new_user)
            return redirect("/headquarters")
    else:
        form = RegisterForm()
    return render(response, "register.html", {"form":form})


@login_required
@user_passes_test(race_check, login_url="/choose_empire_race")
def headquarters(request):
    status = get_object_or_404(UserStatus, user=request.user)
    tick_time = RoundStatus.objects.get().tick_number
    week = tick_time % 52
    year = tick_time // 52
    context = {"status": status,
               "page_title": "Headquarters",
               "week": week,
               "year": year}
    return render(request, "headquarters.html", context)

@login_required
@user_passes_test(reverse_race_check, login_url="/headquarters")
def choose_empire_race(request):
    status = get_object_or_404(UserStatus, user=request.user)
    error = None
    if request.POST and 'chose_race' in request.POST and 'chose_emp' in request.POST:
        if request.POST['chose_emp'] == 'Random':
            empires = Empire.objects.filter(numplayers__lt=players_per_empire)
            emp_choice = np.random.randint(0, empires.count())
            # empire1 = Empire.objects.get(number=emp_choice)
            empire1 = empires[emp_choice]
        else:
            empire1 = Empire.objects.get(number=int(request.POST['chose_emp']))
            if empire1.password or not ('fampass' in request.POST and empire1.password == request.POST['fampass']):
                if empire1.password != request.POST['fampass']:
                    error = "Wrong pass enterted!"
                empire1 = None

        if empire1 is not None:
            empire1.numplayers += 1
            empire1.save()
            status.race = request.POST['chose_race']
            status.empire = empire1
            status.save()
            for p in Planet.objects.filter(x=empire1.x, y=empire1.y):
                if p.owner is None:
                    give_first_planet(request.user, status, p)
                    break
            return render(request, "headquarters.html")

    races = status.Races.choices
    empires = Empire.objects.filter(numplayers__lt=players_per_empire)
    empires_have_pass = None
    if empires.count() < 1:
        error = "Sorry, the galaxy is full! Try writing to the admin on discord that he needs to enlarge the map!"
    else:
        empires_have_pass = {'Random': False}
        for emp in empires:
            if not emp.password:
                empires_have_pass[emp.number] = False
            else:
                empires_have_pass[emp.number] = True

    context = {"races": races,
               "empires": empires_have_pass,
               'empires_json': json.dumps(empires_have_pass),
               'error': error}
    return render(request, "choose_empire_race.html", context)

@login_required
@user_passes_test(race_check, login_url="/choose_empire_race")
def council(request):
    status = get_object_or_404(UserStatus, user=request.user)
    constructions = Construction.objects.filter(user=request.user)
    # Make list of total buildings under construction for each building type
    build_list = {}
    for construction in constructions:
        label = construction.get_building_type_display()  # get_X_display() is the trick for getting the full label of the textchoice
        build_list[label] = build_list.get(label, 0) + construction.n
    context = {"status": status,
               "constructions": constructions,
               "build_list": build_list,
               "page_title": "Council"}
    return render(request, "council.html", context)


@login_required
@user_passes_test(race_check, login_url="/choose_empire_race")
def map(request):
    if request.GET.get('heatmap', None):
        start_t = time.time()
        portals = Planet.objects.filter(portal=True).values_list('x', 'y')
        print("Found", len(portals), "portals")
        heatmap = np.zeros((100, 100))
        for x in range(100):
            for y in range(100):
                for portal in portals:
                    d = np.sqrt((x - portal[0]) ** 2 + (y - portal[1]) ** 2)
                    research_culture = 0
                    cover = np.max(
                        (0, 1.0 - np.sqrt(d / (7.0 * (1.0 + 0.01 * research_culture)))))  # from battlePortalCalc()
                    # specopForcefield = specopForcefieldCalc(planet_owner, feel_destinaton) # in specop.c, I haven't converted it over yet
                    # cover /= (1.0 + 0.01*specopForcefield)
                    heatmap[y, x] += cover  # FIXME no idea why but i had to swap x and y for it to match planets...
        heatmap /= np.max(np.max(heatmap))
        colors = [(0.0, 0.0, 0.0), (0.0, 0.0, 1.0)]  # black to blue colormap
        cm = LinearSegmentedColormap.from_list('custom-cmap', colors, N=20)
        plt.imsave(static('heatmap.png'), heatmap, cmap=cm)
        # print("Heatmap generation took this many seconds:", time.time() - start_t)
        show_heatmap = True
    else:
        show_heatmap = False
    status = get_object_or_404(UserStatus, user=request.user)
    systems = Planet.objects.filter(i=0).values_list('x', 'y')  # result is a list of 2-tuples
    context = {"status": status,
               "planets": Planet.objects.all(),
               "systems": systems, "page_title": "Map", "show_heatmap": show_heatmap}
    return render(request, "map.html", context)


@login_required
@user_passes_test(race_check, login_url="/choose_empire_race")
def planets(request):
    status = get_object_or_404(UserStatus, user=request.user)
    order_by = request.GET.get('order_by', 'planet')
    print("order by-", order_by)

    # TODO, it currently does not support reversing the order by clicking it a second time
    if order_by == 'planet':
        planets = Planet.objects.filter(owner=request.user).order_by('x', 'y', 'i')
    elif order_by in ['ancient', 'bonus_all', 'bonus_none', 'fission']:
        print("Havent implemented that sort yet")
        planets = Planet.objects.filter(owner=request.user).order_by('x', 'y', 'i')
    else:
        planets = Planet.objects.filter(owner=request.user).order_by(order_by)  # directly use the keyword

    context = {"status": status,
               "planets": planets,
               "page_title": "Planets"}
    return render(request, "planets.html", context)


@login_required
@user_passes_test(race_check, login_url="/choose_empire_race")
def planet(request, planet_id):
    status = get_object_or_404(UserStatus, user=request.user)
    planet = get_object_or_404(Planet, pk=planet_id)

    if planet.owner:  # if planet is owned by someone, grab that owner's status, in order to get faction and other info of owner
        planet_owner_status = UserStatus.objects.get(user=planet.owner)
    else:
        planet_owner_status = None

    context = {"status": status,
               "planet": planet,
               "planet_owner_status": planet_owner_status,
               "page_title": "Planet " + str(planet.x) + ',' + str(planet.y) + ':' + str(planet.i)}
    return render(request, "planet.html", context)


@login_required
@user_passes_test(race_check, login_url="/choose_empire_race")
def raze(request, planet_id):
    status = get_object_or_404(UserStatus, user=request.user)
    planet = get_object_or_404(Planet, pk=planet_id)

    # Make sure its owned by user
    if planet.owner != request.user:
        return HttpResponse("This is not your planet!")

    if request.method == 'POST':
        # print(request.POST)
        # List of building types, except portals
        building_list = [SolarCollectors(), FissionReactors(), MineralPlants(), CrystalLabs(), RefinementStations(),
                         Cities(), ResearchCenters(), DefenseSats(), ShieldNetworks()]
        top_msg = ''
        for building in building_list:
            num_to_raze = request.POST.get(building.short_label,
                                           None)  # number user entered to raze for this building type
            if num_to_raze == 'on':
                num_to_raze = 1
            elif num_to_raze:
                num_to_raze = int(num_to_raze)
            else:
                num_to_raze = 0
            num_on_planet = getattr(planet,
                                    building.model_name)  # This is how to access a field of a model using a string for the name of that field
            if (num_to_raze > 0) and (num_on_planet >= num_to_raze):
                setattr(planet, building.model_name, num_on_planet - num_to_raze)
                setattr(planet, 'total_buildings', getattr(planet, 'total_buildings') - num_to_raze)
                setattr(status, 'total_' + building.model_name,
                        getattr(status, 'total_' + building.model_name) - num_to_raze)
                setattr(status, 'total_buildings', getattr(status, 'total_buildings') - num_to_raze)
                top_msg += "You razed " + str(num_to_raze) + " " + building.label + "<p><p>"
            elif num_to_raze > 0:
                top_msg += "Did not have " + str(num_to_raze) + " " + building.label + " to raze<p><p>"
        # Do portal separately
        if request.POST.get("PL", None) and planet.portal:
            planet.portal = False
            top_msg += "You razed the Portal on this planet<p><p>"
        elif request.POST.get("PL", None):
            top_msg += "There is no Portal on this planet to raze<p><p>"
        # Any time we change buildings we need to update planet's overbuild factor
        planet.overbuilt = calc_overbuild(planet.size, planet.total_buildings + planet.buildings_under_construction)
        planet.overbuilt_percent = (planet.overbuilt - 1.0) * 100
        # Save our changes to planet and status
        planet.save()
        status.save()
    else:
        top_msg = None

    context = {"status": status,
               "planet": planet,
               "top_msg": top_msg,
               "page_title": "Raze Buildings on Planet " + str(planet.x) + ',' + str(planet.y) + ':' + str(planet.i)}
    return render(request, "raze.html", context)


@login_required
@user_passes_test(race_check, login_url="/choose_empire_race")
def razeall(request, planet_id):  # TODO still need an html template for this page
    status = get_object_or_404(UserStatus, user=request.user)
    planet = get_object_or_404(Planet, pk=planet_id)
    if request.method == 'POST':
        # List of building types, except portals
        building_list = [SolarCollectors(), FissionReactors(), MineralPlants(), CrystalLabs(), RefinementStations(),
                         Cities(), ResearchCenters(), DefenseSats(), ShieldNetworks()]
        for building in building_list:
            num_on_planet = getattr(planet, building.model_name)
            if num_on_planet:
                setattr(planet, building.model_name, 0)
                setattr(status, 'total_' + building.model_name,
                        getattr(status, 'total_' + building.model_name) - num_on_planet)
                setattr(status, 'total_buildings', getattr(status, 'total_buildings') - num_on_planet)
        setattr(planet, 'total_buildings', 0)
        # Portal
        if planet.portal:
            planet.portal = False
            setattr(status, 'total_portals', getattr(status, 'total_portals') - 1)
            setattr(status, 'total_buildings', getattr(status, 'total_buildings') - 1)
        # Any time we change buildings we need to update planet's overbuild factor
        planet.overbuilt = calc_overbuild(planet.size, planet.total_buildings + planet.buildings_under_construction)
        planet.overbuilt_percent = (planet.overbuilt - 1.0) * 100
        planet.save()
        status.save()
        return HttpResponse("Razed all buildings on this planet!")
    else:
        return HttpResponse("CAN ONLY GET HERE BY CLICKING RAZE ALL BUTTON")


@login_required
@user_passes_test(race_check, login_url="/choose_empire_race")
def build(request, planet_id):
    # This entire view + template is reproducing iohtmlFunc_build()

    status = get_object_or_404(UserStatus, user=request.user)
    planet = get_object_or_404(Planet, pk=planet_id)

    # Make sure its owned by user
    if planet.owner != request.user:
        return HttpResponse("This is not your planet!")

    # Create list of building classes, it's making 1 object of each
    building_list = [SolarCollectors(), FissionReactors(), MineralPlants(), CrystalLabs(), RefinementStations(),
                     Cities(), ResearchCenters(), DefenseSats(), ShieldNetworks(), Portal()]

    if request.method == 'POST':
        # Might be a cleaner way to do it that ties it more directly with the model

        # Following is a rewrite of cmdExecAddBuild in cmd.c, a function that got called for each building type
        msg = ''
        for building in building_list:
            num = request.POST.get(str(building.building_index), None)
            if num == 'on':
                num = 1
            if num == '':
                num = None
            if num:
                num = int(num)
                # calc_building_cost was designed to give the View what it needed, so pull out just the values and multiply by num
                total_resource_cost, penalty = building.calc_cost(num, status.research_percent_construction,
                                                                  status.research_percent_tech)
                if not total_resource_cost:
                    msg += 'Not enough tech research to build ' + building.label + '<br>'
                    continue

                total_resource_cost = ResourceSet(total_resource_cost)  # convert to more usable object
                ob_factor = calc_overbuild_multi(planet.size,
                                                 planet.total_buildings + planet.buildings_under_construction, num)
                total_resource_cost.apply_overbuild(
                    ob_factor)  # can't just use planet.overbuilt, need to take into account how many buildings we are making

                if not total_resource_cost.is_enough(status):
                    msg += 'Not enough resources to build ' + building.label + '<br>'
                    continue

                if isinstance(building, Portal) and planet.portal:
                    msg += 'A portal is already on this planet!'
                    continue

                if isinstance(building, Portal) and planet.portal_under_construction:
                    msg += 'A portal is already under construction on this planet!'
                    continue

                # Deduct resources
                status.energy -= total_resource_cost.ene
                status.minerals -= total_resource_cost.min
                status.crystals -= total_resource_cost.cry
                status.ectrolium -= total_resource_cost.ect

                ticks = total_resource_cost.time  # calculated ticks

                # Create new construction job
                msg += 'Building ' + str(num) + ' ' + building.label + '<br>'
                Construction.objects.create(user=request.user,
                                            planet=planet,
                                            n=num,
                                            building_type=building.short_label,
                                            ticks_remaining=ticks)
                planet.buildings_under_construction += num
                if isinstance(building, Portal):
                    planet.portal_under_construction = True

        # Any time we add buildings we need to update planet's overbuild factor
        planet.overbuilt = calc_overbuild(planet.size, planet.total_buildings + planet.buildings_under_construction)
        planet.overbuilt_percent = (planet.overbuilt - 1.0) * 100
        planet.save()
        status.save()  # update user's resources
    else:
        msg = None  # msg that gets displayed at the top after you build something

    # Build up list of dicts, designed to be used easily by template
    costs = []
    for building in building_list:
        # Below doesn't include overbuild, it gets added below
        cost_list, penalty = building.calc_cost(1, status.research_percent_construction, status.research_percent_tech)

        # Add resource names to the cost_list, for the sake of the for loop in the view
        if cost_list:  # Remember that cost_list will be None if the tech is too low
            cost_list_labeled = []
            for i in range(5):  # 4 types of resources plus time
                cost_list_labeled.append({"value": int(np.ceil(cost_list[i] * planet.overbuilt)),
                                          "name": resource_names[i]})
        else:
            cost_list_labeled = None  # Tech was too low

        cost = {"cost": cost_list_labeled,
                "penalty": penalty,
                "owned": getattr(status, 'total_' + building.model_name),
                "name": building.label}
        costs.append(cost)

    # Build context
    context = {"status": status,
               "planet": planet,
               "costs": costs,
               "portal": planet.portal,
               "portal_under_construction": planet.portal_under_construction,
               "msg": msg,
               "page_title": "Build on Planet " + str(planet.x) + ',' + str(planet.y) + ':' + str(planet.i)}
    return render(request, "build.html", context)


@login_required
@user_passes_test(race_check, login_url="/choose_empire_race")
def ranking(request):
    status = get_object_or_404(UserStatus, user=request.user)
    table = UserRankTable(UserStatus.objects.exclude(race__isnull=True).exclude(race__exact='')
                          .exclude(empire__isnull=True)
                          , order_by=("-num_planets"))
    context = {"table": table,
               "status": status}
    return render(request, "ranking.html", context)


@login_required
@user_passes_test(race_check, login_url="/choose_empire_race")
def empire_ranking(request):
    status = get_object_or_404(UserStatus, user=request.user)
    empire = status.empire
    table = EmpireRankTable(Empire.objects.all().filter(numplayers__gt=0), order_by=("-planets"))
    context = {"table": table,
               "status": status,
               "empire": empire}
    return render(request, "empire_ranking.html", context)


@login_required
@user_passes_test(race_check, login_url="/choose_empire_race")
def account(request):
    status = get_object_or_404(UserStatus, user=request.user)
    context = {"status": status}
    return render(request, "account.html", context)


@login_required
@user_passes_test(race_check, login_url="/choose_empire_race")
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {
        'form': form
    })


@login_required
@user_passes_test(race_check, login_url="/choose_empire_race")
def units(request):
    status = get_object_or_404(UserStatus, user=request.user)
    if request.method == 'POST':
        msg = ''
        for i, unit in enumerate(unit_info["unit_list"]):
            if unit == 'phantom':
                continue
            num = request.POST.get(str(i),
                                   0)  # must match name of each inputfield in the template, in this case we are using integers
            if num == '':
                num = 0
            else:
                num = int(num)
            if num:
                # calc_building_cost was designed to give the View what it needed, so pull out just the values and multiply by num
                mult, _ = unit_cost_multiplier(status.research_percent_construction, status.research_percent_tech,
                                               unit_info[unit]['required_tech'])
                if not mult:
                    msg += 'Not enough tech research to build ' + unit_info[unit]['label'] + '<br>'
                    continue

                print("multiplier:", mult)
                total_resource_cost = [int(np.ceil(x * mult)) for x in unit_info[unit]['cost']]
                for j in range(4):  # multiply all resources except time by number of units
                    total_resource_cost[j] *= num
                print("total_resource_cost", total_resource_cost)
                total_resource_cost = ResourceSet(total_resource_cost)  # convert to more usable object
                if not total_resource_cost.is_enough(status):
                    msg += 'Not enough resources to build ' + unit_info[unit]['label'] + '<br>'
                    continue

                # Deduct resources
                status.energy -= total_resource_cost.ene
                status.minerals -= total_resource_cost.min
                status.crystals -= total_resource_cost.cry
                status.ectrolium -= total_resource_cost.ect

                # Create new construction job
                msg += 'Building ' + str(num) + ' ' + unit + '<br>'
                UnitConstruction.objects.create(user=request.user,
                                                n=num,
                                                unit_type=unit,
                                                ticks_remaining=total_resource_cost.time)  # calculated ticks

        status.save()  # update user's resources
    else:
        msg = None

    resource_names = ['Energy', 'Mineral', 'Crystal', 'Ectrolium', 'Time']
    unit_dict = []  # idea here is to build up a dict we can nicely iterate over in the template
    for unit in unit_info["unit_list"]:
        if unit == 'phantom':
            continue
        d = {}
        mult, penalty = unit_cost_multiplier(status.research_percent_construction, status.research_percent_tech,
                                             unit_info[unit]['required_tech'])
        if not mult:
            cost = None
        else:
            cost = []
            for i, resource in enumerate(resource_names):
                cost.append({"name": resource, "value": int(np.ceil(mult * unit_info[unit]['cost'][i]))})
            d["cost"] = cost
        d["penalty"] = penalty
        d["label"] = unit_info[unit]['label']
        d["owned"] = 0
        d["i"] = unit_info[unit]['i']
        unit_dict.append(d)
    context = {"status": status,
               "unit_dict": unit_dict,
               "msg": msg}
    return render(request, "units.html", context)


@login_required
@user_passes_test(race_check, login_url="/choose_empire_race")
def fleets(request):
    status = get_object_or_404(UserStatus, user=request.user)

    # If user changed order after attack or percentages
    if request.method == 'POST':
        status.post_attack_order = int(request.POST["attack"])
        status.long_range_attack_percent = int(request.POST["f0"])
        status.air_vs_air_percent = int(request.POST["f1"])
        status.ground_vs_air_percent = int(request.POST["f2"])
        status.ground_vs_ground_percent = int(request.POST["f3"])
        status.save()

    main_fleet = Fleet.objects.get(owner=status.user.id, main_fleet=True)  # should only ever be 1
    main_fleet_list = []
    send_fleet_list = []  # need to have a separate list that doesnt include agents/psycics/ghosts/explos
    for unit in unit_info["unit_list"]:
        num = getattr(main_fleet, unit)
        if num:
            main_fleet_list.append({"name": unit_info[unit]["label"], "value": num, "i": unit_info[unit]["i"]})
            if unit not in ['wizard', 'agent', 'ghost', 'exploration']:
                send_fleet_list.append({"name": unit_info[unit]["label"], "value": num, "i": unit_info[unit]["i"]})

    # TODO Generate list of traveling and stationed fleets (in old game i dont see anywhere a list of stationed fleets is shown)

    context = {"status": status,
               "main_fleet_list": main_fleet_list,
               "send_fleet_list": send_fleet_list}
    return render(request, "fleets.html", context)


@login_required
@user_passes_test(race_check, login_url="/choose_empire_race")
def fleetsend(request):
    status = get_object_or_404(UserStatus, user=request.user)
    round_params = get_object_or_404(RoundStatus)  # should only be one
    main_fleet = Fleet.objects.get(owner=status.user.id, main_fleet=True)  # should only ever be 1

    if request.method != 'POST':
        return HttpResponse("You shouldnt be able to get to this page!")

    # Process POST
    print(request.POST)
    x = int(request.POST['X']) if request.POST['X'] else None
    y = int(request.POST['Y']) if request.POST['Y'] else None
    planet_i = int(request.POST['I']) if request.POST['I'] else None
    order = int(request.POST['order'])
    send_unit_dict = {}  # contains how many of each unit to send, dict so its quick to look up different unit counts
    total_sent_units = 0
    for i, unit in enumerate(unit_info["unit_list"][0:9]):
        num = int(request.POST['u' + str(i)]) if request.POST['u' + str(i)] else 0
        if getattr(main_fleet, unit) < num:
            return HttpResponse("Don't have enough" + unit_info[unit]["label"])
        send_unit_dict[unit] = num
        total_sent_units += num

    if total_sent_units == 0:
        return HttpResponse("You must send some units to make a fleet")

    # The rest mostly comes from cmdExecSendFleet in cmdexec.c
    if order == 0 or order == 1:  # if attack planet or station on planet, make sure planet exists and get planet object
        try:
            planet = Planet.objects.get(x=x, y=y, i=planet_i)
        except Planet.DoesNotExist:
            return HttpResponse("This planet doesn't exist")
    else:  # if move to system, make sure x and y are actual coords
        if x < 0 or x >= round_params.galaxy_size or y < 0 or y >= round_params.galaxy_size:
            return HttpResponse("Coordinates aren't valid")

    # Find closest portal and its distance away, which is done in specopVortexListCalc in cmd.c in the C code
    portal_planets = Planet.objects.filter(owner=request.user,
                                           portal=True)  # should always have at least the home planet
    min_dist = 9999999999
    best_portal_planet = None
    for planet in portal_planets:
        dist = np.sqrt((planet.x - x) ** 2 + (planet.y - y) ** 2)
        if dist < min_dist:
            min_dist = dist
            best_portal_planet = planet
    print("Fleet is starting from", best_portal_planet.x, best_portal_planet.y)

    speed = race_info_list[status.get_race_display()]["travel_speed"]  # * specopEnlightemntCalc(id,CMD_ENLIGHT_SPEED);
    # CODE for artefact that decreases/increases travel speed by n%
    # if ( maind.artefacts & ARTEFACT_4_BIT)
    # fa *= 0.8
    fleet_time = int(np.ceil(min_dist / speed))  # in ticks

    # Carrier/transport check
    if send_unit_dict['carrier'] * 100 < (
            send_unit_dict['bomber'] + send_unit_dict['fighter'] + send_unit_dict['transport']):
        return HttpResponse(
            "You are not sending enough carriers, each carrier can hold 100 fighters, bombers or transports")
    if send_unit_dict['transport'] * 100 < (
            send_unit_dict['soldier'] + send_unit_dict['droid'] + 4 * send_unit_dict['goliath']):
        return HttpResponse(
            "You are not sending enough transports, each transport can hold 100 soldiers or droids, or 25 goliaths")

    # Remove units from main fleet
    for unit in unit_info["unit_list"][0:9]:
        setattr(main_fleet, unit, getattr(main_fleet, unit) - send_unit_dict[unit])

    # Create new Fleet object
    Fleet.objects.create(owner=request.user,
                         command_order=order,
                         x=x,
                         y=y,
                         ticks_remaining=fleet_time)

    # If instant travel then immediately do the cmdFleetAction stuff
    if fleet_time == 0:
        # TODO
        # cmdFleetAction()
        return HttpResponse("The fleet reached its destination<br>")

    return HttpResponse("The fleet will reach its destination in " + str(fleet_time) + " weeks<br>")


# TODO, COPY FROM RAZE VIEW
@login_required
@user_passes_test(race_check, login_url="/choose_empire_race")
def fleetdisband(request):
    status = get_object_or_404(UserStatus, user=request.user)
    return HttpResponse("GOT HERE")


@login_required
@user_passes_test(race_check, login_url="/choose_empire_race")
def empire(request, empire_id):
    status = get_object_or_404(UserStatus, user=request.user)
    player_list = UserStatus.objects.filter(empire=empire_id)
    empire1 = Empire.objects.get(pk=empire_id)
    print(empire_id)
    context = {"status": status,
               "page_title": empire1.name_with_id,
               "player_list": player_list,
               "empire": empire1}
    return render(request, "empire.html", context)


@login_required
@user_passes_test(race_check, login_url="/choose_empire_race")
def vote(request):
    status = get_object_or_404(UserStatus, user=request.user)
    player_list = UserStatus.objects.filter(empire=status.empire)
    try:
        new_voting_for = (request.POST['choice'])
    except (KeyError, ObjectDoesNotExist):
        context = {"status": status,
                   "page_title": "Vote",
                   "player_list": player_list}
        return render(request, "vote.html", context)
    else:
        print("check votiung for", status.voting_for)
        if status.voting_for is not None:
            # find previous user voted for and remove one vote from him
            status.voting_for.votes -= 1
            status.voting_for.save()
        voted_for_status = get_object_or_404(UserStatus, user=new_voting_for)
        # check if user voted for himself, to avoid db saving conflicts
        status = get_object_or_404(UserStatus, user=request.user)
        if status.id == voted_for_status.id:
            status.votes += 1
            status.voting_for = status
        else:
            status.voting_for = voted_for_status
            voted_for_status.votes += 1
            voted_for_status.save()
        status.save()

        # part to check/make a new leader when someone has voted
        # if mutiple players have the same ammount of votes - the old leader stays, regarding of his votes
        # otherwise a player with max votes is chosen

        current_leader = None
        max_votes = 0
        for player in player_list:
            if player.empire_role == 'PM':
                current_leader = player
            if player.votes > max_votes:
                max_votes = player.votes
        leaders = []
        for player in player_list:
            if player.votes == max_votes:
                leaders.append(player)
        if len(leaders) == 1:
            if current_leader is not None:
                current_leader.empire_role = 'P'
                current_leader.save()
            leaders[0].empire_role = 'PM'
            leaders[0].save()

        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect("/results")


@login_required
@user_passes_test(race_check, login_url="/choose_empire_race")
def results(request):
    status = get_object_or_404(UserStatus, user=request.user)
    player_list = UserStatus.objects.filter(empire=status.empire)
    context = {"status": status,
               "page_title": "Results",
               "player_list": player_list}
    return render(request, "results.html", context)

@login_required
@user_passes_test(race_check, login_url="/choose_empire_race")
def set_relation(relation, current_empire, target_empire_nr, *rel_time_passed):
    target_empire = Empire.objects.get(number=target_empire_nr)

    if current_empire.id == target_empire.id:
        return
    if not rel_time_passed or rel_time_passed[0] == '':
        rel_time = 0
    else:
        # rel time is given in hours in leaders options, however is stored as number of ticks internally
        rel_time = int(rel_time_passed[0])*3600/tick_time

    if current_empire is None or target_empire is None:
        return

    try:
        tmp_rel = Relations.objects.get(empire1=current_empire, empire2=target_empire)
    except(ObjectDoesNotExist):
        pass
    else:
        if tmp_rel.relation_type == 'AO' or tmp_rel.relation_type == 'NO':
            tmp_rel.delete()
        # if there allready is an established relation we cant create a new offer before the last one is canclled
        elif relation != "cancel_nap":
            return

    # check if there target empire already offered a relation:
    try:
        rel = Relations.objects.get(empire1=target_empire, empire2=current_empire)
    except ObjectDoesNotExist:
        rel = None

    if relation == 'ally':
        if rel is not None and rel.relation_type == 'AO':
            # if second empire allready offered an alliance, make two empires allies
            Relations.objects.create(empire1=current_empire,
                                     empire2=target_empire,
                                     relation_type='A',
                                     relation_length=rel_time,
                                     relation_creation_tick=RoundStatus.objects.get().tick_number,
                                     relation_remaining_time=rel_time)
            rel.relation_type = 'A'
            rel.save()
        else:
            # make an alliance offer from current_empire to target_empire
            Relations.objects.create(empire1=current_empire,
                                     empire2=target_empire,
                                     relation_type='AO',
                                     relation_length=rel_time,
                                     relation_creation_tick=RoundStatus.objects.get().tick_number,
                                     relation_remaining_time=rel_time)
    if relation == 'war':
        Relations.objects.create(empire1=current_empire,
                                 empire2=target_empire,
                                 relation_type='W',
                                 relation_length=war_declaration_timer,
                                 relation_creation_tick=RoundStatus.objects.get().tick_number,
                                 relation_remaining_time=war_declaration_timer)
    if relation == 'nap':
        if rel is not None and rel.relation_type == 'NO' and rel.relation_length == rel_time:
            # if second empire allready offered a nap with the same timer, make two empires napped
            Relations.objects.create(empire1=current_empire,
                                     empire2=target_empire,
                                     relation_type='N',
                                     relation_length=rel_time,
                                     relation_creation_tick=RoundStatus.objects.get().tick_number,
                                     relation_remaining_time=rel_time)
            rel.relation_type = 'N'
            rel.save()
        else:
            # make a nap offer from current_empire to target_empire
            Relations.objects.create(empire1=current_empire,
                                     empire2=target_empire,
                                     relation_type='NO',
                                     relation_length=rel_time,
                                     relation_creation_tick=RoundStatus.objects.get().tick_number,
                                     relation_remaining_time=rel_time)
@login_required
@user_passes_test(race_check, login_url="/choose_empire_race")
def cancel_relation(relation):
    rel = Relations.objects.get(id=relation)
    rel2 = Relations.objects.get(empire1=rel.empire2, empire2=rel.empire1)
    if rel.relation_type == 'AO' or rel.relation_type == 'NO':
        rel.delete()
    elif rel.relation_type == 'A' or rel.relation_type == 'W':
        if rel.relation_type == 'A':
            rel2.relation_type = 'AO'
            rel2.save()
        if RoundStatus.objects.get().tick_number - rel.relation_creation_tick > min_relation_time:
            rel.delete()
    elif rel.relation_length is not None:
        # cancel timed nap for both empires, any empire of two can trigger this
        # this will be cancelled in process_tick when the right time comes
        rel.relation_type = 'NC'
        rel.relation_cancel_tick = RoundStatus.objects.get().tick_number
        rel2.relation_type = 'NC'
        rel2.relation_cancel_tick = RoundStatus.objects.get().tick_number
        rel.save()
        rel2.save()
    else:
        # if this is a permanent NAP both parties need to cancel it for it to be deleted
        if rel2.relation_type == 'PC':
            rel.delete()
            rel2.delete()
        else:
            rel.relation_type = 'PC'
            rel.save()


@login_required
@user_passes_test(race_check, login_url="/choose_empire_race")
def pm_options(request):
    status = get_object_or_404(UserStatus, user=request.user)
    user_empire = status.empire
    relation_empires = Relations.objects.filter(empire1=status.empire)

    if request.method == 'POST':
        print(request.POST)
        if request.FILES:
            if user_empire.empire_image is not None:
                user_empire.empire_image.delete(save=True)
            picture = request.FILES['empire_picture']
            user_empire.empire_image = picture
            user_empire.save()

        user_empire.name = request.POST['empire_name']
        user_empire.name_with_id = request.POST['empire_name'] + " #" + str(user_empire.number)
        user_empire.password = request.POST['empire_pass']
        user_empire.taxation = float(request.POST['empire_taxation'])
        user_empire.pm_message = (request.POST['empire_pm_message'])
        user_empire.relations_message = (request.POST['empire_relations_message'])
        if request.POST['empire_offer_alliance']:
            set_relation('ally', status.empire, request.POST['empire_offer_alliance'])
        if request.POST['empire_offer_nap']:
            set_relation('nap', status.empire, request.POST['empire_offer_nap'], request.POST['empire_offer_nap_hours'])
        if request.POST['empire_cancel_relation']:
            cancel_relation(request.POST['empire_cancel_relation'])
        if request.POST['empire_declare_war']:
            set_relation('war', status.empire, request.POST['empire_declare_war'])
        user_empire.save()
    context = {"status": status,
               "page_title": "Prime Minister options",
               "empire": status.empire,
               "relation_empires": relation_empires}
    return render(request, "pm_options.html", context)


@login_required
@user_passes_test(race_check, login_url="/choose_empire_race")
def relations(request):
    status = get_object_or_404(UserStatus, user=request.user)
    relations_from_empire = Relations.objects.filter(empire1=status.empire)
    relations_to_empire = Relations.objects.filter(empire2=status.empire)
    tick_time = RoundStatus.objects.get().tick_number
    context = {"status": status,
               "page_title": "Relations",
               "relations_from_empire": relations_from_empire,
               "relations_to_empire": relations_to_empire,
               "empire": status.empire,
               "tick_time":tick_time}
    return render(request, "relations.html", context)


@login_required
@user_passes_test(race_check, login_url="/choose_empire_race")
def research(request):
    status = get_object_or_404(UserStatus, user=request.user)
    message = ''
    print(request.POST)
    if request.method == 'POST':
        if 'fund_form' in request.POST:
            if request.POST['fund']:
                if status.energy >= int(request.POST['fund']):
                    status.energy -= int(request.POST['fund'])
                    status.current_research_funding += int(request.POST['fund'])
                    message = request.POST['fund'] + " energy was funded!"
                    status.save()
                else:
                    message = "You don't have so much energy!"
        if 'rc_alloc_form' in request.POST:
            total = 0
            for a, key in enumerate(request.POST.items()):
                if a > 0 and key[0] != 'rc_alloc_form':
                    print("key",a,key[1])
                    total += int(key[1])
            if total != 100:
                message = "Research allocation percentages must be equal to 100% in total!"
            else:
                status.alloc_research_military = request.POST['military']
                status.alloc_research_construction = request.POST['construction']
                status.alloc_research_tech = request.POST['technology']
                status.alloc_research_energy = request.POST['energy']
                status.alloc_research_population = request.POST['population']
                status.alloc_research_culture = request.POST['culture']
                status.alloc_research_operations = request.POST['operations']
                status.alloc_research_portals = request.POST['portals']
                status.save()

    context = {"status": status,
               "page_title": "Research",
               "message": message}
    return render(request, "research.html", context)


@login_required
@user_passes_test(race_check, login_url="/choose_empire_race")
def famaid(request):
    status = get_object_or_404(UserStatus, user=request.user)
    player_list = UserStatus.objects.filter(empire=status.empire)
    num_players = len(player_list)
    message = ''
    if request.method == 'POST':
        status2 = get_object_or_404(UserStatus, user=request.POST['player'])
        if request.POST['energy']:
            e = int(request.POST['energy'])
            if e > status.energy:
                message += "You don't have so much energy!<br>"
            else:
                status.energy -= e
                status2.energy += e
                message += str(e) + " Energy was transferred!<br>"
        if request.POST['minerals']:
            m = int(request.POST['minerals'])
            if m > status.minerals:
                message += "You don't have so much minerals!<br>"
            else:
                status.minerals -= m
                status2.minerals += m
                message += str(m) + " Minerals was transferred!<br>"
        if request.POST['crystals']:
            c = int(request.POST['crystals'])
            if c > status.crystals:
                message += "You don't have so much crystals!<br>"
            else:
                status.crystals -= c
                status2.crystals += c
                message += str(c) + " Crystals was transferred!<br>"
        if request.POST['ectrolium']:
            e = int(request.POST['ectrolium'])
            if e > status.ectrolium:
                message += "You don't have so much ectrolium!<br>"
            else:
                status.ectrolium -= e
                status2.ectrolium += e
                message += str(e) + " Ectrolium was transferred!<br>"
        status.save()
        status2.save()
    context = {"status": status,
               "num_players": num_players,
               "page_title": "Send aid",
               "player_list": player_list,
               "message": message}
    return render(request, "famaid.html", context)


@login_required
@user_passes_test(race_check, login_url="/choose_empire_race")
def famgetaid(request):
    status = get_object_or_404(UserStatus, user=request.user)
    player_list = UserStatus.objects.filter(empire=status.empire)
    num_players = len(player_list)
    message = ''
    if 'receive_aid' in request.POST:
        status2 = get_object_or_404(UserStatus, user=request.POST['player'])
        if status2.request_aid == 'A' or (status2.request_aid == 'PM' and status.empire_role == 'PM') or \
            (status2.request_aid == 'VM' and (status.empire_role == 'PM' or status.empire_role == 'VM')):
            if request.POST['energy']:
                e = int(request.POST['energy'])
                if e > status2.energy:
                    message += status2.user_name + " doesn't have so much energy!<br>"
                else:
                    status.energy += e
                    status2.energy -= e
                    message += str(e) + " Energy was transferred!<br>"
            if request.POST['minerals']:
                m = int(request.POST['minerals'])
                if m > status2.minerals:
                    message += status2.user_name + " doesn't have so much minerals!<br>"
                else:
                    status.minerals += m
                    status2.minerals -= m
                    message += str(m) + " Minerals was transferred!<br>"
            if request.POST['crystals']:
                c = int(request.POST['crystals'])
                if c > status2.crystals:
                    message += status2.user_name + " doesn't have so much crystals!<br>"
                else:
                    status.crystals += c
                    status2.crystals -= c
                    message += str(c) + " Crystals was transferred!<br>"
            if request.POST['ectrolium']:
                e = int(request.POST['ectrolium'])
                if e > status2.ectrolium:
                    message += status2.user_name + " doesn't have so much ectrolium!<br>"
                else:
                    status.ectrolium += e
                    status2.ectrolium -= e
                    message += str(e) + " Ectrolium was transferred!<br>"
            status.save()
            status2.save()
        else:
            message = "You are not authorised to take aid from this faction!"
    if 'aid_settings' in request.POST:
        status.request_aid = request.POST['settings']
        message = "Settings changed!"
        status.save()
    context = {"status": status,
               "num_players": num_players,
               "page_title": "Receive aid",
               "player_list": player_list,
               "message": message}
    return render(request, "famgetaid.html", context)


@login_required
@user_passes_test(race_check, login_url="/choose_empire_race")
def messages(request):
    status = get_object_or_404(UserStatus, user=request.user)
    messages_from = Messages.objects.filter(user2=status.id, user2_deleted=False).order_by('-date_and_time')
    context = {"status": status,
               "page_title": "Inbox",
               "messages_from": messages_from,
                }
    return render(request, "messages.html", context)


@login_required
@user_passes_test(race_check, login_url="/choose_empire_race")
def outbox(request):
    status = get_object_or_404(UserStatus, user=request.user)
    messages_to = Messages.objects.filter(user1=status.id, user1_deleted=False).order_by('-date_and_time')
    context = {"status": status,
               "page_title": "Outbox",
               "messages_to": messages_to,
                }
    return render(request, "outbox.html", context)


@login_required
@user_passes_test(race_check, login_url="/choose_empire_race")
def compose_message(request, user_id):
    status = get_object_or_404(UserStatus, user=request.user)
    msg_on_top = ''
    user_found = True
    if request.method == 'POST':
        if UserStatus.objects.filter(user_name=request.POST['recipient']).exists():
            status2 = UserStatus.objects.get(user_name=request.POST['recipient'])
        else:
            if UserStatus.objects.filter(id=request.POST['recipient']).exists():
                status2 = UserStatus.objects.get(id=request.POST['recipient'])
            else:
                msg_on_top = 'This player is not found, try again!'
                user_found = False

        if user_found:
            msg = request.POST['message']
            if len(msg) > 0:
                Messages.objects.create(user1 = status,
                                        user2 = status2,
                                        message = msg,
                                        date_and_time = datetime.now())
                msg_on_top = 'Message sent!'
            else:
                msg_on_top = 'You cannot send an empty message!'

    context = {"status": status,
               "page_title": "Compose message",
               "msg_on_top": msg_on_top,
               "user_id": user_id,
                }
    return render(request, "compose_message.html", context)


@login_required
@user_passes_test(race_check, login_url="/choose_empire_race")
def del_message_in(request, message_id):
    status = get_object_or_404(UserStatus, user = request.user)
    message = get_object_or_404(Messages, id = message_id, user2 = status.id)
    if message.user1_deleted:
        message.delete()
    else:
        message.user2_deleted = True
        message.save()
    messages_from = Messages.objects.filter(user2=status.id, user2_deleted=False).order_by('-date_and_time')
    context = {"status": status,
               "page_title": "Inbox",
               "messages_from": messages_from,
                }
    return render(request, "messages.html", context)


@login_required
@user_passes_test(race_check, login_url="/choose_empire_race")
def del_message_out(request, message_id):
    status = get_object_or_404(UserStatus, user = request.user)
    message = get_object_or_404(Messages, id = message_id, user1 = status.id)
    if message.user2_deleted:
        message.delete()
    else:
        message.user1_deleted = True
        message.save()
    messages_to = Messages.objects.filter(user1=status.id, user1_deleted=False).order_by('-date_and_time')
    context = {"status": status,
               "page_title": "Outbox",
               "messages_to": messages_to,
                }
    return render(request, "outbox.html", context)


@login_required
@user_passes_test(race_check, login_url="/choose_empire_race")
def bulk_del_message_out(request):
    status = get_object_or_404(UserStatus, user = request.user)
    messages_buffer = Messages.objects.filter(user1 = status.id)
    for message in messages_buffer:
        message.user1_deleted = True
    Messages.objects.bulk_update(messages_buffer, ['user1_deleted'])
    Messages.objects.filter(user1_deleted = True, user2_deleted = True).delete()
    messages_to = ''
    context = {"status": status,
               "page_title": "Outbox",
               "messages_to": messages_to,
                }
    return render(request, "outbox.html", context)


@login_required
@user_passes_test(race_check, login_url="/choose_empire_race")
def bulk_del_message_in(request):
    status = get_object_or_404(UserStatus, user = request.user)
    messages_buffer = Messages.objects.filter(user2 = status.id)
    for message in messages_buffer:
        message.user2_deleted = True
    Messages.objects.bulk_update(messages_buffer, ['user2_deleted'])
    Messages.objects.filter(user1_deleted = True, user2_deleted = True).delete()
    messages_from = ''
    context = {"status": status,
               "page_title": "Inbox",
               "messages_to": messages_from,
                }
    return render(request, "messages.html", context)

@login_required
@user_passes_test(race_check, login_url="/choose_empire_race")
def custom_logout(request):
    logout(request)
    return HttpResponseRedirect('/')




