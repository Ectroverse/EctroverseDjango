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
from django.contrib.messages import get_messages
from django.core.exceptions import ObjectDoesNotExist
from django.template import RequestContext
from django.db.models import Q, Max, Sum
from django.contrib.auth.decorators import user_passes_test
from app.map_settings import *
from app.helper_functions import *
from app.specops import *
from app.battle import *

import json
import numpy as np
import time
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from datetime import datetime
from datetime import timedelta

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
            # print(status.user_name, form.cleaned_data['game_name'])
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
    fresh_news = News.objects.filter(user1 = request.user, is_read = False, is_personal_news = True).order_by('-date_and_time')
    old_news = News.objects.filter(user1 = request.user, is_read = True, is_personal_news = True).order_by('-date_and_time')
    for n in fresh_news:
        n.is_read = True
    News.objects.bulk_update(fresh_news, ['is_read'])
    status.construction_flag = 0
    status.economy_flag = 0
    status.military_flag = 0
    status.save()
    context = {"status": status,
               "page_title": "Headquarters",
               "week": week,
               "year": year,
               "fresh_news": fresh_news,
               "old_news": old_news}
    return render(request, "headquarters.html", context)

@login_required
@user_passes_test(race_check, login_url="/choose_empire_race")
def btn(request):
    status = get_object_or_404(UserStatus, user=request.user)
    # mail
    btn1 = "i09.jpg"
    if status.mail_flag == 1: #blue
        btn1 = "i09a.jpg"
    # building
    btn2 = "i10.jpg"
    if status.construction_flag == 1: #yellow
        btn2 = "i10a.jpg"
    # market
    btn3 = "i11.jpg"
    if status.economy_flag == 1: #green
        btn3 = "i11a.jpg"
    # fleets
    btn4 = "i12.jpg"
    if status.military_flag == 1: #red
        btn4 = "i12a.jpg"
    if status.military_flag == 2: #green
        btn4 = "i12b.jpg"
    if status.military_flag == 3: #yellow
        btn4 = "i12c.jpg"
    context = {"status": status,
                "btn1": btn1,
                "btn2": btn2,
                "btn3": btn3,
                "btn4": btn4
                }
    return render(request, "btn.html", context)

@login_required
@user_passes_test(race_check, login_url="/choose_empire_race")
def scouting(request):
    status = get_object_or_404(UserStatus, user=request.user)
    scouted = Scouting.objects.filter(user=request.user)
    order_by = request.GET.get('order_by', 'planet')

    if order_by == 'planet':
        # scouted = Scouting.objects.filter(planet__owner=request.user).\
        #     values('planet__size','scout','planet__x','planet__y','planet__i','planet__x').\
        #     order_by('planet__x','planet__y','planet__i')
        scouted = Scouting.objects.select_related('planet').filter(user=request.user).\
            order_by('planet__x','planet__y','planet__i')

    elif order_by == 'size':
        scouted = Scouting.objects.select_related('planet').filter(user=request.user).order_by('planet__size')
    else:
        scouted = Scouting.objects.select_related('planet').filter(user=request.user). \
            order_by('planet__'+order_by)


    context = {"status": status,
               "page_title": "Planatery Scouting",
               "scouted": scouted,
               "planets": planets,
               "sql": scouted.query
                   }
    return render(request, "scouting.html", context)

@login_required
@user_passes_test(race_check, login_url="/choose_empire_race")
def battle(request, fleet_id):
    status = get_object_or_404(UserStatus, user=request.user)
    fleet = get_object_or_404(Fleet, pk=fleet_id)
    attacked_planet = Planet.objects.get(x=fleet.x, y=fleet.y, i=fleet.i)
    if attacked_planet.home_planet:
        request.session['error'] = "You cannot attack a home planet!"
        return fleets(request)
    if attacked_planet.owner == request.user:
        request.session['error'] = "Why would you want to attack yourself?"
        messages.error(request, 'Document deleted.')
        return fleets(request)
    if fleet.owner != status.user:
        return fleets(request)
    if fleet.ticks_remaining != 0:
        return fleets(request)
    battle_report = attack_planet(fleet)
    context = {"status": status,
               "page_title": "Battle",
               "fleet": fleet,
               "battle_report": battle_report
               }
    return render(request, "battle.html", context)

@login_required
@user_passes_test(race_check, login_url="/choose_empire_race")
def map_settings(request):
    status = get_object_or_404(UserStatus, user=request.user)
    msg = ""
    err_msg = ""
    if request.method == 'POST':
        print(request.POST)
        if 'new_setting' in request.POST:
            nr_settings = MapSettings.objects.filter(user=request.user).count()
            if nr_settings > 19:
                err_msg = "You can have 20 settings at max!"
            else:
                MapSettings.objects.create(user=request.user)
                msg = "New setting created!"
        else:
            settings_id = request.POST.getlist("setting_object")
            color = request.POST.getlist("color")
            delete_setting2 = request.POST.getlist("delete_setting")
            delete_setting = []
            j = 0
            while j < len(delete_setting2):
                if j < len(delete_setting2) - 1 and delete_setting2[j] == "0":
                    if delete_setting2[j+1] == "1":
                        delete_setting.append(1)
                        j += 2
                    else:
                        delete_setting.append(0)
                        j += 1
                else:
                    delete_setting.append(0)
                    j += 1
            print("delete_setting", delete_setting)

            map_settings = request.POST.getlist("map_settings")
            details = request.POST.getlist("details")
            for i in range(0, len(settings_id)):
                if map_settings[i] == 'PF':
                    if not details[i]:
                        err_msg = "You have to specify faction id or name for setting # " + str(i) +" !"
                        break

                    faction_setting, err_msg = get_userstatus_from_id_or_name(details[i])
                    if faction_setting == None:
                        break

                elif map_settings[i] == 'PE':
                    if not details[i]:
                        err_msg = "You have to specify empire id or name for setting # " + str(i) +"!"
                        break
                    if isinstance(details[i], int):
                        if Empire.objects.filter(number=details[i]).first() is None:
                            err_msg = "The empire id " + str(details[i]) + " doesn't exist for setting # " + str(i) +"!"
                            break
                        else:
                            empire_setting = Empire.objects.filter(number=details[i]).first()
                    else:
                        if Empire.objects.filter(name=details[i]).first() is None:
                            err_msg = "The empire name " + str(details[i]) + " doesn't exist for setting # " + str(i) +"!"
                            break
                        else:
                            empire_setting = Empire.objects.filter(name=details[i]).first()
                setting = MapSettings.objects.get(id=settings_id[i])
                if delete_setting[i] == 1:
                    setting.delete()
                    msg = "Settings updated!"
                else:
                    setting.color_settings = color[i]
                    setting.map_setting = map_settings[i]

                    if map_settings[i] == 'PF':
                        setting.faction = faction_setting
                        setting.empire = None
                    elif map_settings[i] == 'PE' and details[i]:
                        setting.empire = empire_setting
                        setting.faction = None
                    else:
                        setting.empire = None
                        setting.faction = None
                    setting.save()
                    msg = "Settings updated!"

    map_gen_settings = MapSettings.objects.filter(user=request.user).order_by('id')
    context = {"status": status,
               "page_title": "Map Settings",
               "map_settings": map_gen_settings,
               "msg": msg,
               "err_msg": err_msg
               }
    return render(request, "map_settings.html", context)

@login_required
@user_passes_test(race_check, login_url="/choose_empire_race")
def famnews(request):
    status = get_object_or_404(UserStatus, user=request.user)
    current_tick_number = RoundStatus.objects.get().tick_number
    empire_news = News.objects.filter(empire1=status.empire,
                                      is_empire_news = True,
                                      tick_number__gte=current_tick_number-news_show).\
                                        order_by('-date_and_time')

    current_empire = status.empire
    context = {"status": status,
               "page_title": "Empire News",
               "current_empire": current_empire,
               "news": empire_news}
    return render(request, "empire_news.html", context)

@login_required
@user_passes_test(reverse_race_check, login_url="/headquarters")
def choose_empire_race(request):
    status = get_object_or_404(UserStatus, user=request.user)
    error = None
    if request.POST and 'faction' in request.POST and 'chose_race' in request.POST and 'chose_emp' in request.POST:
        if request.POST['faction'] == "":
            error = "Faction name is required!"
        elif UserStatus.objects.filter(user_name=request.POST['faction']).count() > 0:
            error = "This faction name is allready taken!"
        else:
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
                status.user_name = request.POST['faction']
                status.race = request.POST['chose_race']
                status.empire = empire1
                status.networth = 1
                status.construction_flag = 0
                status.economy_flag = 0
                status.military_flag = 0
                status.save()
                for p in Planet.objects.filter(x=empire1.x, y=empire1.y):
                    if p.owner is None:
                        give_first_planet(request.user, status, p)
                        give_first_fleet(Fleet.objects.get(owner=request.user,main_fleet=True))
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

    msg = ""
    refund = [0, 0, 0, 0]
    if 'cancel_unit' in request.POST:
        cancelled_units = request.POST.getlist('cancel_unit')
        for cu in cancelled_units:
            cf = UnitConstruction.objects.get(id=cu)
            refund[0] += int(cf.energy_cost/2)
            refund[1] += int(cf.mineral_cost/2)
            refund[2] += int(cf.crystal_cost/2)
            refund[3] += int(cf.ectrolium_cost/2)
            cf.delete()
        msg += "You were refunded with" + str(refund[0]) + " energy, " + str(refund[1]) + " minerals, " +\
            str(refund[2]) + " crystals, " + str(refund[3]) + " ectrolium! "

    if 'cancel_build' in request.POST:
        cancelled_buildings = request.POST.getlist('cancel_build')
        for cb in cancelled_buildings:
            cf = Construction.objects.get(id=cb)
            refund[0] += int(cf.energy_cost/2)
            refund[1] += int(cf.mineral_cost/2)
            refund[2] += int(cf.crystal_cost/2)
            refund[3] += int(cf.ectrolium_cost/2)
            cf.delete()
        msg += "You were refunded with" + str(refund[0]) + " energy, " + str(refund[1]) + " minerals, " +\
            str(refund[2]) + " crystals, " + str(refund[3]) + " ectrolium! "

    status.energy += refund[0]
    status.minerals += refund[1]
    status.crystals += refund[2]
    status.ectrolium += refund[3]
    status.save()

    # Make list of total buildings under construction for each building type
    main_fleet_list = []
    main_fleet = Fleet.objects.get(owner=request.user, main_fleet=True)
    unit_total = 0
    for unit in unit_info["unit_list"]:
        num = getattr(main_fleet, unit)
        if num:
            main_fleet_list.append({"name": unit_info[unit]["label"], "value": num})
            unit_total += num

    constructions = Construction.objects.filter(user=request.user)
    built_fleet = UnitConstruction.objects.filter(user=request.user)

    construction_sum_filter = Construction.objects.filter(user=request.user).\
        values("building_type").annotate(buildings_sum=Sum("n"))
    fleets_sum_filter = UnitConstruction.objects.filter(user=request.user).\
        values("unit_type").annotate(units_sum=Sum("n"))
    print("fleets_sum_filter",fleets_sum_filter)

    fleets_sum = {}
    for unit_query in fleets_sum_filter:
        unit = unit_query['unit_type']
        num = unit_query['units_sum']
        fleets_sum[unit_info[unit]["label"]] = num

    construction_sum = {}
    for build_query in construction_sum_filter:
        building = build_query['building_type']
        num = build_query['buildings_sum']
        construction_sum[building_labels[building]] = num


    # fleets_sum = UnitConstruction.objects.filter(user=request.user).aggregate(Sum('unit_type'))
    context = {"status": status,
               "constructions": constructions,
               "built_fleet": built_fleet,
               "main_fleet": main_fleet_list,
               "unit_total": unit_total,
               "page_title": "Council",
               "construction_sum": construction_sum,
               "fleets_sum": fleets_sum,
               "msg": msg}
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
               "settings": MapSettings.objects.filter(user=status.id),
               "systems": systems, "page_title": "Map", "show_heatmap": show_heatmap}
    return render(request, "map.html", context)


@login_required
@user_passes_test(race_check, login_url="/choose_empire_race")
def planets(request):
    status = get_object_or_404(UserStatus, user=request.user)
    request.session['mass_build'] = None
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
    attack_cost = None
    if planet.owner:  # if planet is owned by someone, grab that owner's status, in order to get faction and other info of owner
        planet_owner_status = UserStatus.objects.get(user=planet.owner)
        attack_cost = battleReadinessLoss(status, planet_owner_status, planet)
    else:
        planet_owner_status = None

    exploration_cost = calc_exploration_cost(status)

    context = {"status": status,
               "planet": planet,
               "attack_cost":attack_cost,
               "planet_owner_status": planet_owner_status,
               "page_title": "Planet " + str(planet.x) + ',' + str(planet.y) + ':' + str(planet.i),
               "exploration_cost": exploration_cost}
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
    msg = ""
    building_list = [SolarCollectors(), FissionReactors(), MineralPlants(), CrystalLabs(), RefinementStations(),
                     Cities(), ResearchCenters(), DefenseSats(), ShieldNetworks(), Portal()]

    if request.method == 'POST':
        if planet.owner != request.user:
            return "This is not your planet!"
        building_list_dict = {}

        for building in building_list:
            building_list_dict[building] = request.POST.get(str(building.building_index), None)

        msg = "building on planet " + str(planet.x) + ":" + str(planet.y) + "," +str(planet.i) + "\n"
        msg += build_on_planet(status, planet, building_list_dict)

    # Build up list of dicts, designed to be used easily by template
    costs = []
    for building in building_list:
        # Below doesn't include overbuild, it gets added below
        cost_list, penalty = building.calc_cost(1, status.research_percent_construction, status.research_percent_tech, status)
        # Add resource names to the cost_list, for the sake of the for loop in the view
        if cost_list:  # Remember that cost_list will be None if the tech is too low
            cost_list_labeled = []
            for i in range(5):  # 4 types of resources plus time
                cost_list_labeled.append({"value": int(np.ceil(cost_list[i] * max(1, planet.overbuilt))),
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
def mass_build(request):
    status = get_object_or_404(UserStatus, user=request.user)
    if request.method != 'POST':
        return planets(request)

    building_list = [SolarCollectors(), FissionReactors(), MineralPlants(), CrystalLabs(), RefinementStations(),
                     Cities(), ResearchCenters(), DefenseSats(), ShieldNetworks(), Portal()]

    average_ob = 1
    msg = ""
    building_list_dict = {}

    if 'planets_id_mass_build' in request.POST:
        request.session['mass_build'] = request.POST.getlist('planets_id_mass_build')
    elif 'mass_build' in request.session and request.session['mass_build'] is not None:
        planets_id = request.session['mass_build']
        for pid in planets_id:
            planet = Planet.objects.get(id=pid)
            for building in building_list:
                building_list_dict[building] = request.POST.get(str(building.building_index), None)
            msg += "building on planet " + str(planet.x) + ":" + str(planet.y) + "," + str(planet.i) + "\n"
            msg += build_on_planet(status, planet, building_list_dict)
            request.session['mass_build'] = None

    costs = []
    for building in building_list:
        # Below doesn't include overbuild, it gets added below
        cost_list, penalty = building.calc_cost(1, status.research_percent_construction, status.research_percent_tech, status)
        # Add resource names to the cost_list, for the sake of the for loop in the view
        if cost_list:  # Remember that cost_list will be None if the tech is too low
            cost_list_labeled = []
            for i in range(5):  # 4 types of resources plus time
                cost_list_labeled.append({"value": int(np.ceil(cost_list[i] * max(1, average_ob))),
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
               "costs": costs,
               "msg": msg,
               "page_title": "Mass build"}
    return render(request, "mass_build.html", context)

@login_required
@user_passes_test(race_check, login_url="/choose_empire_race")
def ranking(request):
    status = get_object_or_404(UserStatus, user=request.user)
    table = UserRankTable(UserStatus.objects.exclude(race__isnull=True).exclude(race__exact='')
                          .exclude(empire__isnull=True)
                          , order_by=("-num_planets", "-networth"))
    context = {"table": table,
               "page_title": "Faction ranking",
               "status": status}
    return render(request, "ranking.html", context)


@login_required
@user_passes_test(race_check, login_url="/choose_empire_race")
def empire_ranking(request):
    status = get_object_or_404(UserStatus, user=request.user)
    empire = status.empire
    table = EmpireRankTable(Empire.objects.all().filter(numplayers__gt=0), order_by=("-planets", "-networth"))
    context = {"table": table,
               "page_title": "Empire ranking",
               "status": status,
               "empire": empire}
    return render(request, "empire_ranking.html", context)


@login_required
@user_passes_test(race_check, login_url="/choose_empire_race")
def account(request):
    status = get_object_or_404(UserStatus, user=request.user)
    context = {"status": status,
               "page_title": "Account",}
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

    # bribe officials operation modifier
    bribe_resource_multiplier = 1
    bribe_time_multiplier = 1
    if Specops.objects.filter(user_to=status.user, name="Bribe officials",
                              extra_effect="resource_cost").exists():
        bribe = Specops.objects.filter(user_to=status.user, name="Bribe officials",
                                       extra_effect="resource_cost")
        for br in bribe:
            bribe_resource_multiplier *= 1 + br.specop_strength / 100

    if Specops.objects.filter(user_to=status.user, name="Bribe officials",
                              extra_effect="building_time").exists():
        bribe = Specops.objects.filter(user_to=status.user, name="Bribe officials",
                                       extra_effect="building_time")
        for br in bribe:
            bribe_time_multiplier *= 1 + br.specop_strength / 100


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

                total_resource_cost = [int(np.ceil(x * mult)) for x in unit_info[unit]['cost']]

                for j in range(4):  # multiply all resources except time by number of units
                    total_resource_cost[j] *= num * bribe_resource_multiplier

                #multiply time cost by bribe multiplier
                total_resource_cost[4] *= bribe_time_multiplier

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
                                                ticks_remaining=total_resource_cost.time,
                                                energy_cost=total_resource_cost.ene,
                                                mineral_cost=total_resource_cost.min,
                                                crystal_cost=total_resource_cost.cry,
                                                ectrolium_cost=total_resource_cost.ect
                                                )  # calculated ticks

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
                if resource != 'Time':
                    cost.append({"name": resource,
                                 "value": int(np.ceil(mult * unit_info[unit]['cost'][i]*bribe_resource_multiplier))})
                else:
                    cost.append({"name": resource,
                                 "value": int(np.ceil(mult * unit_info[unit]['cost'][i]*bribe_time_multiplier))})

            d["cost"] = cost
        d["penalty"] = penalty
        d["label"] = unit_info[unit]['label']
        d["owned"] = 0
        d["i"] = unit_info[unit]['i']
        unit_dict.append(d)
    context = {"status": status,
               "page_title":"Units",
               "unit_dict": unit_dict,
               "msg": msg}
    return render(request, "units.html", context)


@login_required
@user_passes_test(race_check, login_url="/choose_empire_race")
def fleets_orders(request):
    status = get_object_or_404(UserStatus, user=request.user)

    if request.POST and "fleet_nr" in request.POST and "fleet_select" in request.POST:
        fleets_id = request.POST.getlist("fleet_nr")
        fleets_checkbox = request.POST.getlist("fleet_select")
    else:
        return fleets(request)

    # checkboxes values arent passed if they are not checked, hence passing a hidden,which needs to be removed if
    # the box was actually checked, stupid html :P
    fleets_checkbox2 = []
    for i in range(0, len(fleets_checkbox)):
        print("i",i)
        if fleets_checkbox[i] == '0':
            if i < len(fleets_checkbox)-1 and fleets_checkbox[i+1] == '1':
                fleets_checkbox2.append('1')
            else:
                fleets_checkbox2.append('0')

    fleets_id2 = []
    # select only checked fleets
    for i,fleet in enumerate(fleets_id):
        print(i,fleet,fleets_checkbox2[i])
        if fleets_checkbox2[i] == '1':
            fleets_id2.append(fleet)

    fleets = Fleet.objects.filter(id__in=fleets_id2)
    display_fleet = {}
    for fleet in fleets:
        display_fleet_inner = {}
        for unit in unit_info["unit_list"]:
            num = getattr(fleet, unit)
            if num > 0:
                display_fleet_inner[unit_info[unit]["label"]] = num
        display_fleet[fleet] = display_fleet_inner

    if 'massExplo1' in request.POST:
        context = {"status": status,
                   "page_title": "Exploration orders",
                   "display_fleet": display_fleet,
                   "hidden_fleet_id":fleets_id2,
                   }
        return render(request, "explo_orders.html", context)
    else:
        context = {"status": status,
                   "page_title": "Fleets orders",
                   "display_fleet": display_fleet,
                   "hidden_fleet_id":fleets_id2,
                   }
        return render(request, "fleets_orders.html", context)

@login_required
@user_passes_test(race_check, login_url="/choose_empire_race")
def fleets_orders_process(request):
    status = get_object_or_404(UserStatus, user=request.user)
    round_params = get_object_or_404(RoundStatus)

    if not request.POST:
        request.session['error'] = "Not a right request!"
        return fleets(request)

    if not "fleet_select_hidden" in request.POST:
        request.session['error'] = "No fleets selected!"
        return fleets(request)
    if not "order" in request.POST:
        request.session['error'] = "No order selected!"
        return fleets(request)

    fleets_id = request.POST.getlist("fleet_select_hidden")
    order = int(request.POST.get("order"))

    if (order == 0 or order == 1  or order == 2 or order == 3 or order == 10) and not request.POST.get("X"):
        request.session['error'] = "You must enter x coordinate!"
        return fleets(request)
    if (order == 0 or order == 1  or order == 2 or order == 3 or order == 10) and not request.POST.get("Y"):
        request.session['error'] = "You must enter y coordinate!"
        return fleets(request)

    if order == 0 or order == 1  or order == 2 or order == 3 or order == 10:
        x = int(request.POST.get("X"))
        y = int(request.POST.get("Y"))

    if (order == 0 or order == 1 or order == 10) and not request.POST.get("I"):
        request.session['error'] = "You must enter planets number!"
        return fleets(request)

    if (order == 6) and not request.POST.get("split_pct"):
        request.session['error'] = "You must enter fleet split %!"
        return fleets(request)

    if order == 0 or order == 1 or order == 10:  # if attack planet or station on planet, make sure planet exists and get planet object
        i = request.POST.get("I")
        try:
            planet = Planet.objects.get(x=x, y=y, i=i)
        except Planet.DoesNotExist:
            request.session['error'] = "This planet doesn't exist"
            return fleets(request)
    elif order == 2 or order == 3:  # if move to system, make sure x and y are actual coords
        if x < 0 or x >= round_params.galaxy_size or y < 0 or y >= round_params.galaxy_size:
            request.session['error'] = "Coordinates aren't valid"
            return fleets(request)

    fleets_id2 = Fleet.objects.filter(id__in=fleets_id)
    # print("fleets_id2",fleets_id2)

    # option value="0" Attack the planet
    # option value="1" Station on planet
    # option value="2" Move to system
    # option value="3" Merge in system (chose system yourself)
    # option value="4" Merge in system (auto/optimal)
    # option value="5" Join main fleet
    # option value="6" Split fleet

    speed = race_info_list[status.get_race_display()]["travel_speed"]
    if order == 0 or order == 1:
        for f in fleets_id2:
            generate_fleet_order(f, x, y, speed, order, i)
        # do instant merge of stationed fleets if allready present on that planet
        fleets_id3 = Fleet.objects.filter(id__in=fleets_id, ticks_remaining=0, command_order=1)
        station_fleets(request, fleets_id3, status)
    if order == 2 or order == 3:
        for f in fleets_id2:
            generate_fleet_order(f, x, y, speed, order)
    # mass merge auto
    if order == 3 or order == 4:
        systems = []
        for f in fleets_id2:
            tmp = []
            tmp.append(f.current_position_x)
            tmp.append(f.current_position_y)
            systems.append(tmp)
        pos = find_bounding_circle(systems)
        for f in fleets_id2:
            generate_fleet_order(f, pos[0], pos[1], speed, order)
        fleets_id3 = Fleet.objects.filter(id__in=fleets_id, ticks_remaining=0)
        # do instant merge of fleets allready present in same systems
        merge_fleets(fleets_id3)
    # join main fleet
    if order == 5:
        portal_planets = Planet.objects.filter(owner=request.user,
                                               portal=True)  # should always have at least the home planet, unless razed!!!
        # print(portal_planets)
        if not portal_planets:
            request.session['error'] = "You need at least one portal for fleet to returnto main fleet!"
            return fleets(request)
        for f in fleets_id2:
            portal = find_nearest_portal(f.current_position_x, f.current_position_y, portal_planets)
            generate_fleet_order(f, portal.x, portal.y, speed, order, portal.i)
        # do instant join of fleets allready present in systems with portals
        main_fleet = Fleet.objects.get(owner=request.user, main_fleet=True)
        fleets_id3 = Fleet.objects.filter(id__in=fleets_id, ticks_remaining=0)
        join_main_fleet(main_fleet, fleets_id3)
    if order == 6:
        split_pct = int(request.POST.get("split_pct"))
        total_fleets = Fleet.objects.filter(owner=status.user.id, main_fleet=False)
        if len(total_fleets) >= 50 :
            request.session['error'] = "You cant have more than 50 fleets out at the same time!"
            return fleets(request)
        split_fleets(fleets_id2, split_pct)
    if order == 10:
        for f in fleets_id2:
            generate_fleet_order(f, x, y, speed, order, i)
        # instant explore
        fleets_buffer = Fleet.objects.filter(main_fleet=False, ticks_remaining=0, command_order=10)
        explore_planets(fleets_buffer)

    return fleets(request)

@login_required
@user_passes_test(race_check, login_url="/choose_empire_race")
def fleets(request):
    status = get_object_or_404(UserStatus, user=request.user)
    other_fleets = Fleet.objects.filter(owner=status.user.id, main_fleet=False)
    display_fleet_exploration = Fleet.objects.filter(owner=status.user.id, main_fleet=False, exploration=1)

    # show errors from fleetsend such as not having enough transports for droids, etc
    error = None
    if 'error' in request.session:
        error = request.session['error']
        request.session['error'] = ''

    planet_to_template_explore = None
    if request.method == 'POST' and 'explore_planet' in request.POST:
        try:
            pl_id = request.POST.get('explore_planet')
            planet_to_template_explore = Planet.objects.get(id=pl_id)
        except Planet.DoesNotExist:
            planet_to_template_explore = None

    planet_to_template_attack = None
    if request.method == 'POST' and 'attack_planet' in request.POST:
        try:
            pl_id = request.POST.get('attack_planet')
            planet_to_template_attack = Planet.objects.get(id=pl_id)
        except Planet.DoesNotExist:
            planet_to_template_attack = None

    exploration_cost = None
    if planet_to_template_explore:
        exploration_cost = calc_exploration_cost(status)

    attack_cost = None
    status2 = None
    if planet_to_template_attack:
        status2 = UserStatus.objects.get(id=planet_to_template_attack.owner.id)
        attack_cost = battleReadinessLoss(status, status2,planet_to_template_attack)

    # If user changed order after attack or percentages
    if request.method == 'POST' and 'attack' in request.POST:
        status.post_attack_order = int(request.POST["attack"])
        status.long_range_attack_percent = int(request.POST["f0"])
        status.air_vs_air_percent = int(request.POST["f1"])
        status.ground_vs_air_percent = int(request.POST["f2"])
        status.ground_vs_ground_percent = int(request.POST["f3"])
        status.save()

    main_fleet = Fleet.objects.get(owner=status.user.id, main_fleet=True)  # should only ever be 1
    main_fleet_list = []
    send_fleet_list = []  # need to have a separate list that doesnt include agents/psycics/ghosts/explos
    explo_ships = main_fleet.exploration

    for unit in unit_info["unit_list"]:
        num = getattr(main_fleet, unit)
        if num:
            main_fleet_list.append({"name": unit_info[unit]["label"], "value": num, "i": unit_info[unit]["i"]})
            if unit not in ['wizard', 'agent', 'ghost', 'exploration']:
                send_fleet_list.append({"name": unit_info[unit]["label"], "value": num, "i": unit_info[unit]["i"]})

    display_fleet = {}
    for fleet in other_fleets:
        display_fleet_inner = {}
        for unit in unit_info["unit_list"]:
            if unit not in ['wizard', 'agent', 'ghost', 'exploration']:
                num = getattr(fleet, unit)
                if num > 0:
                    print(unit, num)
                    display_fleet_inner[unit_info[unit]["label"]] = num
                    display_fleet[fleet] = display_fleet_inner

    context = {"status": status,
               "page_title": "Fleets",
               "main_fleet_list": main_fleet_list,
               "send_fleet_list": send_fleet_list,
               "other_fleets": other_fleets,
               "display_fleet":display_fleet,
               "display_fleet_exploration": display_fleet_exploration,
               "explo_ships": explo_ships,
               "error":error,
               "planet_to_template_explore": planet_to_template_explore,
               "planet_to_template_attack": planet_to_template_attack,
               "exploration_cost": exploration_cost,
               "owner_of_attacked_pl" : status2,
               "attack_cost" : attack_cost}
    return render(request, "fleets.html", context)

@login_required
@user_passes_test(race_check, login_url="/choose_empire_race")
def fleets_disband(request):
    status = get_object_or_404(UserStatus, user=request.user)
    main_fleet = Fleet.objects.get(owner=status.user.id, main_fleet=True)  # should only ever be 1
    main_fleet_list = []
    print("main_fleet",main_fleet)

    disband_info = {}

    if request.method == 'POST':
        for unit in unit_info["unit_list"]:
            if unit in request.POST:
                setattr(main_fleet, unit, getattr(main_fleet, unit) - int(request.POST.get(unit)))
                if int(request.POST.get(unit)) > 0:
                    disband_info[unit_info[unit]["label"]] = request.POST.get(unit)
        main_fleet.save()

    for unit in unit_info["unit_list"]:
        num = getattr(main_fleet, unit)
        if num:
            main_fleet_list.append({"name": unit_info[unit]["label"], "value": num, "i": unit_info[unit]["i"], "db_name": unit})

    context = {"status": status,
               "page_title": "Fleets disband",
               "main_fleet": main_fleet_list,
               "disband_info" : disband_info,
                }
    return render(request, "fleets_disband.html", context)


@login_required
@user_passes_test(race_check, login_url="/choose_empire_race")
def fleetsend(request):
    status = get_object_or_404(UserStatus, user=request.user)
    round_params = get_object_or_404(RoundStatus)  # should only be one
    main_fleet = Fleet.objects.get(owner=status.user.id, main_fleet=True)  # should only ever be 1

    if request.method != 'POST':
        return HttpResponse("You shouldnt be able to get to this page!")


    total_fleets = Fleet.objects.filter(owner=status.user.id, main_fleet=False)
    if len(total_fleets) >= 50:
        request.session['error'] = "You cant send more than 50 fleets out at the same time!"
        return fleets(request)

    # Process POST
    print(request.POST)
    x = int(request.POST['X']) if request.POST['X'] else None
    y = int(request.POST['Y']) if request.POST['Y'] else None
    planet_i = int(request.POST['I']) if request.POST['I'] else None
    order = int(request.POST['order'])
    send_unit_dict = {}  # contains how many of each unit to send, dict so its quick to look up different unit counts
    total_sent_units = 0

    if 'exploration' in request.POST:
        if getattr(main_fleet, 'exploration') < 1:
            request.session['error'] = "You don't have any exploration ships!"
            return fleets(request)
        send_unit_dict['exploration'] = 1
        total_sent_units = 1
    else:
        for i, unit in enumerate(unit_info["unit_list"][0:9]):
            # print('u' + str(i))
            if 'u' + str(i) in request.POST:
                if request.POST['u' + str(i)]:
                    num = int(request.POST['u' + str(i)])
                else:
                    num = 0
            else:
                num = 0
            if getattr(main_fleet, unit) < num:
                request.session['error'] = "Don't have enough" + unit_info[unit]["label"]
                return fleets(request)
            send_unit_dict[unit] = num
            total_sent_units += num

    if total_sent_units == 0:
        request.session['error'] = "You must send some units to make a fleet"
        return fleets(request)


    # The rest mostly comes from cmdExecSendFleet in cmdexec.c
    if order == 0 or order == 1 or order == 10:  # if attack planet or station on planet orexplore, make sure planet exists and get planet object
        try:
            planet = Planet.objects.get(x=x, y=y, i=planet_i)
        except Planet.DoesNotExist:
            request.session['error'] = "This planet doesn't exist"
            return fleets(request)
    else:  # if move to system, make sure x and y are actual coords
        if not x or not y or x < 0 or x >= round_params.galaxy_size or y < 0 or y >= round_params.galaxy_size:
            request.session['error'] = "Coordinates aren't valid"
            return fleets(request)

    if not 'exploration' in request.POST:
        # Carrier/transport check
        if send_unit_dict['carrier'] * 100 < (
                send_unit_dict['bomber'] + send_unit_dict['fighter'] + send_unit_dict['transport']):
            request.session['error'] = "You are not sending enough carriers, each carrier can hold 100 fighters, bombers or transports"
            return fleets(request)
        if send_unit_dict['transport'] * 100 < (
                send_unit_dict['soldier'] + send_unit_dict['droid'] + 4 * send_unit_dict['goliath']):
            request.session['error'] = "You are not sending enough transports, each transport can hold 100 soldiers or droids, or 25 goliaths"
            return fleets(request)


    # Find closest portal and its distance away, which is done in specopVortexListCalc in cmd.c in the C code
    portal_planets = Planet.objects.filter(owner=request.user,
                                           portal=True)  # should always have at least the home planet, unless razed!!!

    if not portal_planets:
        request.session['error'] = "You need at least one portal to send the fleet from!"
        return fleets(request)

    best_portal_planet =  find_nearest_portal(x, y, portal_planets)
    min_dist = np.sqrt((best_portal_planet.x - x) ** 2 + (best_portal_planet.y - y) ** 2)
    speed = race_info_list[status.get_race_display()]["travel_speed"]
    speed_boost_enlightement = 1
    if Specops.objects.filter(user_to=request.user, name="Enlightenment", extra_effect="Speed").exists():
        en = Specops.objects.get(user_to=request.user, name="Enlightenment", extra_effect="Speed")
        speed_boost_enlightement = (1 + en.specop_strength / 100)
    speed *= speed_boost_enlightement
    # * specopEnlightemntCalc(id,CMD_ENLIGHT_SPEED);
    fleet_time = int(np.ceil(min_dist / speed))  # in ticks

    if not 'exploration' in request.POST:
    # Remove units from main fleet
        for unit in unit_info["unit_list"][0:9]:
            setattr(main_fleet, unit, getattr(main_fleet, unit) - send_unit_dict[unit])
    else:
        setattr(main_fleet, 'exploration', getattr(main_fleet, 'exploration') - 1)

    # Create new Fleet object
    fleet = Fleet.objects.create(owner=request.user,
                         command_order=order,
                         x=x,
                         y=y,
                         i=planet_i,
                         ticks_remaining=fleet_time,
                         current_position_x=best_portal_planet.x,
                         current_position_y=best_portal_planet.y,
                         **send_unit_dict)

    main_fleet.save()
    # If instant travel then immediately do the cmdFleetAction stuff

    fleets_tmp = []
    if fleet_time == 0:
        fleets_tmp.append(fleet)

    if order == 10 :
        fr_cost = calc_exploration_cost(status)
        status.fleet_readiness -= fr_cost
        status.save()
        # instant explore
        if fleet_time == 0:
            explore_planets(fleets_tmp)

    if order == 1 and fleet_time == 0:
        station_fleets(request,fleets_tmp,status)

    if fleet_time == 0:
        # TODO
        # cmdFleetAction()
        request.session['error'] = "The fleet reached its destination!"
        return fleets(request)

    request.session['error'] = "The fleet will reach its destination in " + str(fleet_time) + " weeks"

    return fleets(request)


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
def set_relation(request,relation, current_empire, target_empire, *rel_time_passed):

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
            News.objects.create(empire1=current_empire,
                                empire2=target_empire,
                                news_type='RAD',
                                date_and_time=datetime.now()+timedelta(seconds=1),
                                is_personal_news=False,
                                is_empire_news=True,
                                tick_number=RoundStatus.objects.get().tick_number
                                )
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
            News.objects.create(empire1=current_empire,
                                empire2=target_empire,
                                news_type='RND',
                                date_and_time=datetime.now()+timedelta(seconds=1),
                                is_personal_news=False,
                                is_empire_news=True,
                                tick_number=RoundStatus.objects.get().tick_number
                                )
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
def cancel_relation(request, rel):

    try:
        rel2 = Relations.objects.get(empire1=rel.empire2, empire2=rel.empire1)
    except ObjectDoesNotExist:
        rel2 = None

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
    error = None

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
            target_empire = Empire.objects.get(number=int(request.POST['empire_offer_alliance']))
            set_relation(request,'ally', status.empire, target_empire)
            News.objects.create(empire1=status.empire,
                                empire2=target_empire,
                                news_type='RAP',
                                date_and_time=datetime.now(),
                                is_personal_news=False,
                                is_empire_news=True,
                                tick_number=RoundStatus.objects.get().tick_number
                                )
        elif request.POST['empire_offer_nap']:
            target_empire = Empire.objects.get(number=int(request.POST['empire_offer_nap']))
            set_relation(request,'nap', status.empire, target_empire, request.POST['empire_offer_nap_hours'])
            if request.POST['empire_offer_nap_hours']:
                info = request.POST['empire_offer_nap_hours'] +" hour"
            else:
                info = "permanent"
            News.objects.create(empire1=status.empire,
                                empire2=target_empire,
                                news_type='RNP',
                                date_and_time=datetime.now(),
                                is_personal_news=False,
                                is_empire_news=True,
                                extra_info =info,
                                tick_number=RoundStatus.objects.get().tick_number
                                )
        elif request.POST['empire_cancel_relation']:
            relation = request.POST['empire_cancel_relation']
            try:
                rel = Relations.objects.get(id=relation)
            except ObjectDoesNotExist:
                rel = None
            if rel:
                if rel.empire1 == status.empire:
                    target_empire = rel.empire2
                else:
                    target_empire = rel.empire1

                if (rel.relation_type=='A' or rel.relation_type=='W') and RoundStatus.objects.get().tick_number - rel.relation_creation_tick <= min_relation_time:
                    error = "You can't cancel the relation for " +str(min_relation_time) + " ticks after creating it!"
                else:
                    n_type = 'N'
                    if rel.relation_type=='W':
                        n_type = 'RWE'
                    elif rel.relation_type=='A':
                        n_type = 'RAE'
                    elif rel.relation_type=='N':
                        n_type = 'RNE'
                    cancel_relation(request, rel)
                    News.objects.create(empire1=status.empire,
                                        empire2=target_empire,
                                        news_type=n_type,
                                        date_and_time=datetime.now(),
                                        is_personal_news=False,
                                        is_empire_news=True,
                                        tick_number=RoundStatus.objects.get().tick_number
                                        )
        elif request.POST['empire_declare_war']:
            target_empire = Empire.objects.get(number=int(request.POST['empire_declare_war']))
            set_relation(request,'war', status.empire, target_empire)
            News.objects.create(empire1=status.empire,
                                empire2=target_empire,
                                news_type='RWD',
                                date_and_time=datetime.now(),
                                is_personal_news=False,
                                is_empire_news=True,
                                tick_number=RoundStatus.objects.get().tick_number
                                )

        user_empire.save()
    context = {"status": status,
               "page_title": "Prime Minister options",
               "empire": status.empire,
               "relation_empires": relation_empires,
               'error':error}
    return render(request, "pm_options.html", context)


@login_required
@user_passes_test(race_check, login_url="/choose_empire_race")
def relations(request):
    status = get_object_or_404(UserStatus, user=request.user)
    relations_from_empire = Relations.objects.filter(empire1=status.empire).order_by('-relation_creation_tick')
    relations_to_empire = Relations.objects.filter(empire2=status.empire).order_by('-relation_creation_tick')
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
def specops(request):
    status = get_object_or_404(UserStatus, user=request.user)
    race_ops = race_info_list[status.get_race_display()]["op_list"]
    race_spells = race_info_list[status.get_race_display()]["spell_list"]
    race_inca = race_info_list[status.get_race_display()]["incantation_list"]

    planet_to_template_specop = None
    if request.method == 'POST' and 'specop_planet' in request.POST:
        try:
            pl_id = request.POST.get('specop_planet')
            planet_to_template_specop = Planet.objects.get(id=pl_id)
        except Planet.DoesNotExist:
            planet_to_template_specop = None

    user_to_template_specop = None
    if planet_to_template_specop is not None:
        if planet_to_template_specop.owner is not None:
            user_to_template_specop = (UserStatus.objects.get(id=planet_to_template_specop.owner.id))

    ops = {}
    for o in agentop_specs:
        if o in race_ops:
            specs = [None]*8
            for j in range(len(agentop_specs[o])):
                specs[j] = agentop_specs[o][j]
            if user_to_template_specop:
                specs[6] = specopReadiness(agentop_specs[o], "Op", status, user_to_template_specop)
            else:
                specs[6] = None
            specs[7] = get_op_penalty(status.research_percent_operations, agentop_specs[o][0])
            ops[o] = specs

    spells = {}
    for s in psychicop_specs:
        if s in race_spells:
            specs = [None] * 8
            for j in range(len(psychicop_specs[s])):
                specs[j] = psychicop_specs[s][j]
            if user_to_template_specop:
                specs[6] = specopReadiness(psychicop_specs[s], "Spell", status, user_to_template_specop)
            else:
                specs[6] = None
            specs[7] = get_op_penalty(status.research_percent_culture, psychicop_specs[s][0])
            spells[s] = specs

    inca = list(set(race_inca) & set(all_incantations))
    msg = ""
    main_fleet = Fleet.objects.get(owner=status.user.id, main_fleet=True)

    if request.method == 'POST':
        if 'spell' in request.POST and 'unit_ammount' in request.POST:
            if status.psychic_readiness < 0:
                msg = "You don't have enough psychic readiness to perform this spell!"
            elif int(request.POST['unit_ammount']) > main_fleet.wizard:
                msg = "You don't have that many psychics!"
            else:
                if psychicop_specs[request.POST['spell']][3] is False and request.POST['user_id2'] == "" :
                    msg = "You must specify a target player for this spell!"
                else:
                    if psychicop_specs[request.POST['spell']][3] is False:
                        faction, err_msg = get_userstatus_from_id_or_name(request.POST['user_id2'])
                    else:
                        faction = None
                    # if second faction not found and not self spell
                    if faction is None and psychicop_specs[request.POST['spell']][3] is False:
                        msg = err_msg
                    else:
                        msg = perform_spell(request.POST['spell'], int(request.POST['unit_ammount']), status, faction)

        print(request.POST)
        if 'operation' in request.POST and 'unit_ammount' in request.POST:
            if status.agent_readiness < 0:
                msg = "You don't have enough agent readiness to perform this spell!"
            elif int(request.POST['unit_ammount']) > main_fleet.agent:
                msg = "You don't have that many agents!"
            elif request.POST['X'] == "" or request.POST['Y'] == "" or request.POST['I'] == "":
                msg = "You must specify a planet!"
            elif get_op_penalty(status.research_percent_operations, agentop_specs[request.POST['operation']][0])  == -1:
                msg = "You don't have enough operations research to perform this covert operation!"
            else:
                planet = None
                try:
                    planet = Planet.objects.get(x=request.POST['X'], y=request.POST['Y'], i=request.POST['I'])
                except Planet.DoesNotExist:
                   msg = "This planet doesn't exist"
                if planet:
                    msg = send_agents_ghosts(status, int(request.POST['unit_ammount']), 0,
                        request.POST['X'], request.POST['Y'], request.POST['I'], request.POST['operation'])
        if 'agent_select' in request.POST:
            agent_select = request.POST.getlist('agent_select')
            for agent_id in agent_select:
                # TODO remake later to 1 function
                speed = race_info_list[status.get_race_display()]["travel_speed"]
                agent_fleet = Fleet.objects.get(id=agent_id)
                portal_planets = Planet.objects.filter(owner=request.user, portal=True)
                portal = find_nearest_portal(agent_fleet.current_position_x, agent_fleet.current_position_y, portal_planets)
                generate_fleet_order(agent_fleet, portal.x, portal.y, speed, 5, portal.i)
                main_fleet = Fleet.objects.get(owner=request.user, main_fleet=True)
                fleets_id3 = Fleet.objects.filter(id=agent_id, ticks_remaining=0)
                join_main_fleet(main_fleet, fleets_id3)
                msg = "Agents sent!"

    agent_fleets = Fleet.objects.filter(owner=status.user, agent__gt=1, main_fleet=False)

    ops_in = Specops.objects.filter(user_to=status.user, specop_type='O', stealth=False)
    ops_out = Specops.objects.filter(user_from=status.user, specop_type='O')
    spells_in = Specops.objects.filter(user_to=status.user, specop_type='S', stealth=False)
    spells_out = Specops.objects.filter(user_from=status.user, specop_type='S')
    inca_in = Specops.objects.filter(user_to=status.user, specop_type='G', stealth=False)
    inca_out = Specops.objects.filter(user_from=status.user, specop_type='G')

    template_name = None
    if user_to_template_specop is not None:
        template_name = user_to_template_specop.user_name

    context = {"status": status,
                "page_title": "Special Operations",
                "operations": ops,
                "spells": spells,
                "incantations": inca,
                "msg": msg,
                "main_fleet": main_fleet,
                "agent_fleets": agent_fleets,
                "ops_out": ops_out,
                "ops_in": ops_in,
                "spells_in": spells_in,
                "spells_out": spells_out,
                "inca_out": inca_out,
                "inca_in": inca_in,
                "planet_to_template_specop": planet_to_template_specop,
                "user_to_template_specop": template_name,
               }
    return render(request, "specops.html", context)

@login_required
@user_passes_test(race_check, login_url="/choose_empire_race")
def specop_show(request, specop_id):
    status = get_object_or_404(UserStatus, user=request.user)
    specop = Specops.objects.get(id=specop_id)
    specop_info = ""
    if specop.name == "Diplomatic Espionage":
        specops_affecting_target = Specops.objects.filter(user_to=specop.user_to)
        for s in specops_affecting_target:
            specop_info += "Specop: " + str(s.name)
            specop_info += " Time remaining: " + str(s.ticks_left)
            if s.specop_strength > 0 :
                specop_info += " Strength: " + str(s.ticks_left)
            if s.extra_effect is not None:
                specop_info += " Extra effect: " + str(s.extra_effect)
            specop_info += "\n"


    context = {"status": status,
               "page_title": specop.name,
               "specop_info": specop_info
               }
    return render(request, "specop_show.html", context)

@login_required
@user_passes_test(race_check, login_url="/choose_empire_race")
def famaid(request):
    status = get_object_or_404(UserStatus, user=request.user)
    player_list = UserStatus.objects.filter(empire=status.empire)
    num_players = len(player_list)
    message = ''
    news_message = ''
    if request.method == 'POST':
        status2 = get_object_or_404(UserStatus, user=request.POST['player'])
        total = 0
        if request.POST['energy']:
            e = int(request.POST['energy'])
            if e > status.energy:
                message += "You don't have so much energy!<br>"
            else:
                status.energy -= e
                status2.energy += e
                message += str(e) + " Energy was transferred!<br>"
                news_message += str(e) + " energy "
                total+= e
        if request.POST['minerals']:
            m = int(request.POST['minerals'])
            if m > status.minerals:
                message += "You don't have so much minerals!<br>"
            else:
                status.minerals -= m
                status2.minerals += m
                message += str(m) + " Minerals was transferred!<br>"
                news_message += str(m) + " minerals "
                total += m
        if request.POST['crystals']:
            c = int(request.POST['crystals'])
            if c > status.crystals:
                message += "You don't have so much crystals!<br>"
            else:
                status.crystals -= c
                status2.crystals += c
                message += str(c) + " Crystals was transferred!<br>"
                news_message += str(c) + " crystals "
                total += c
        if request.POST['ectrolium']:
            e = int(request.POST['ectrolium'])
            if e > status.ectrolium:
                message += "You don't have so much ectrolium!<br>"
            else:
                status.ectrolium -= e
                status2.ectrolium += e
                message += str(e) + " Ectrolium was transferred!<br>"
                news_message += str(e) + " ectrolium "
                total += e
        if total > 0:
            News.objects.create(user1=request.user,
                            user2=status2.user,
                            empire1=status.empire,
                            news_type='SI',
                            date_and_time=datetime.now(),
                            is_personal_news=True,
                            is_empire_news=True,
                            extra_info=news_message,
                            tick_number=RoundStatus.objects.get().tick_number
                            )
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
    news_message = ''
    if 'receive_aid' in request.POST:
        status2 = get_object_or_404(UserStatus, user=request.POST['player'])
        if status2.request_aid == 'A' or (status2.request_aid == 'PM' and status.empire_role == 'PM') or \
            (status2.request_aid == 'VM' and (status.empire_role == 'PM' or status.empire_role == 'VM')):
            total = 0
            if request.POST['energy']:
                e = int(request.POST['energy'])
                if e > status2.energy:
                    message += status2.user_name + " doesn't have so much energy!<br>"
                else:
                    status.energy += e
                    status2.energy -= e
                    message += str(e) + " Energy was transferred!<br>"
                    news_message += str(e) + " energy "
                    total += e
            if request.POST['minerals']:
                m = int(request.POST['minerals'])
                if m > status2.minerals:
                    message += status2.user_name + " doesn't have so much minerals!<br>"
                else:
                    status.minerals += m
                    status2.minerals -= m
                    message += str(m) + " Minerals was transferred!<br>"
                    news_message += str(m) + " minerals "
                    total += m
            if request.POST['crystals']:
                c = int(request.POST['crystals'])
                if c > status2.crystals:
                    message += status2.user_name + " doesn't have so much crystals!<br>"
                else:
                    status.crystals += c
                    status2.crystals -= c
                    message += str(c) + " Crystals was transferred!<br>"
                    news_message += str(c) + " crystals "
                    total += m
            if request.POST['ectrolium']:
                e = int(request.POST['ectrolium'])
                if e > status2.ectrolium:
                    message += status2.user_name + " doesn't have so much ectrolium!<br>"
                else:
                    status.ectrolium += e
                    status2.ectrolium -= e
                    message += str(e) + " Ectrolium was transferred!<br>"
                    news_message += str(e) + " ectrolium "
                    total += e
            if total > 0:
                News.objects.create(user1=request.user,
                                user2=status2.user,
                                empire1=status.empire,
                                news_type='RA',
                                date_and_time=datetime.now(),
                                is_personal_news=True,
                                is_empire_news=True,
                                extra_info = news_message,
                                tick_number=RoundStatus.objects.get().tick_number
                                )
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
def game_messages(request):
    status = get_object_or_404(UserStatus, user=request.user)
    messages_from = Messages.objects.filter(user2=status.id, user2_deleted=False).order_by('-date_and_time')
    status.mail_flag = 0
    status.save()
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
                News.objects.create(user1 = request.user,
                                    user2 = User.objects.get(id=request.POST['recipient']),
                                    news_type = 'MS',
                                    date_and_time=datetime.now(),
                                    is_personal_news=True,
                                    is_empire_news=False,
                                    tick_number = RoundStatus.objects.get().tick_number
                                    )
                News.objects.create(user1 = User.objects.get(id=request.POST['recipient']),
                                    user2 = request.user,
                                    news_type = 'MR',
                                    date_and_time=datetime.now(),
                                    is_personal_news=True,
                                    is_empire_news=False,
                                    tick_number = RoundStatus.objects.get().tick_number
                                    )
                status2.mail_flag = 1
                status2.save()
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


def hall_of_fame(request):
    rounds = HallOfFame.objects.aggregate(Max('round'))
    round_records = {}
    msg = ""

    if rounds["round__max"] is None:
        msg = "The hall of fame is empty!"
    else:
        num_rounds = int(rounds["round__max"])
        for i in range ((num_rounds), -1, -1):
            round_records[i] = HallOfFame.objects.filter(round=i).order_by('-planets')

    context = {"page_title": "Hall of Fame",
               "round_records": round_records,
               "msg":msg
                }

    return render(request, "hall_of_fame.html", context)
