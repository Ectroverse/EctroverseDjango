from django.db.models import Q, Sum
from .models import *
from app.constants import *
import numpy as np
from app.models import *
from datetime import datetime
import copy



def battleReadinessLoss(user1, user2):
    print(user1, user2)
    fa = (1+user1.num_planets) / (1+user2.num_planets)
    empire1 = user1.empire
    empire2 = user2.empire
    max = 100

    if (empire1 == empire2): #intra-fam attack
        fa = pow(fa, 1.3)
        fb = 1.0
        max = 16.0
    else:
        fa = pow(fa, 1.3);
        fb = (1 + empire1.planets) / (1 + empire2.planets)
        fb = pow(fb, 1.8)

    fdiv = 0.5
    if fb < fa:
        fdiv = 0.5 * pow(fb / fa, 0.8)
    fa = (fdiv * fa) + ((1.0 - fdiv) * fb)
    if fa < 0.50:
        fa = 0.50
    fa *= 11.5

    war = False
    ally = False
    nap = False

    relations_from_empire = Relations.objects.filter(empire1=empire1)
    relations_to_empire = Relations.objects.filter(empire2=empire2)

    for rel in relations_from_empire:
        if rel.relation_type == 'W' and rel.empire2 == empire2:
            war = True
        if rel.relation_type == 'A' and rel.empire2 == empire2:
            ally = True
        if rel.relation_type == 'NC' or rel.relation_type == 'PC' or rel.relation_type == 'N' and rel.empire2 == empire2:
            nap = True

    for rel in relations_to_empire:
        if rel.relation_type == 'W' and rel.empire2 == empire1:
            war = True
        if rel.relation_type == 'A' and rel.empire2 == empire1:
            ally = True
        if rel.relation_type == 'NC' or rel.relation_type == 'PC' or rel.relation_type == 'N' and rel.empire2 == empire1:
            nap = True

    if empire1.id == empire2.id or ally or war:
        fa /= 3

    if nap:
        fa = max(50, fa)

    return min(int(fa), max)


def attack_planet(attacking_fleet):
    attacker = UserStatus.objects.get(id=attacking_fleet.owner.id)
    attacked_planet = Planet.objects.get(x=attacking_fleet.x,y=attacking_fleet.y,i=attacking_fleet.i)
    defender = UserStatus.objects.get(id=attacked_planet.owner.id)
    defending_fleets = Fleet.objects.filter(Q(owner=defender.id), Q(main_fleet=True)|\
                    Q(on_planet=True, x=attacking_fleet.x, y =attacking_fleet.y, i=attacking_fleet.i ) ).\
        aggregate(Sum('bomber'),Sum('fighter'),Sum('transport'),Sum('cruiser'),Sum('carrier'),Sum('soldier'),\
                  Sum('droid'),Sum('goliath'),Sum('phantom'),Sum('wizard'),Sum('agent'),Sum('ghost'),Sum('exploration'))

    attstats = {}
    defstats = {}
    msg = ""
    for i in range(0, len(unit_labels)):
        attstats[unit_labels[i]] = copy.deepcopy(unit_stats[i])
        unit_bonus = race_info_list[attacker.get_race_display()].get(unit_race_bonus_labels[i], 1.0)
        for j in range(0, 4):
            attstats[unit_labels[i]][j] = round(attstats[unit_labels[i]][j] * unit_bonus, 2)
        defstats[unit_labels[i]] = copy.deepcopy(unit_stats[i])
        unit_bonus = race_info_list[defender.get_race_display()].get(unit_race_bonus_labels[i], 1.0)
        for j in range(0, 4):
            defstats[unit_labels[i]][j] = round(defstats[unit_labels[i]][j] * unit_bonus, 2)


    msg += "\n\n attstats" + str(attstats) + " attacker.get_race_display() " + str(attacker.get_race_display())
    msg += "\n\n defstats" + str(defstats) + " defender.get_race_display() " + str(defender.get_race_display())

    msg += "\n\n defending_fleets1" + str(defending_fleets)
    msg += "\n\n protection" + str(attacked_planet.protection)
    for key, value in defending_fleets.items():
        defending_fleets[key] = value * attacked_planet.protection/100
        if key == 'bomber__sum':
            defending_fleets[key]
    msg += "\n\n defending_fleets2" + str(defending_fleets)

    if attacker.fleet_readiness < -100:
        msg += "<b>Your forces require time to recover and prepare before engaging a new battle.\
         Forcing them to attack would have more than disastrous consequences.</b>\n"
        return msg;
    elif attacker.fleet_readiness < -60:
        msg += "<b>Your forces are completely unprepared for another battle!\
         Their effectiveness will be greatly reduced, you can also expect desertions.</b>\n"
    elif attacker.fleet_readiness < -40:
        msg += "<b>Your forces are exhausted, their effectiveness in battle will be very low.</b>\n"
    elif attacker.fleet_readiness < -20:
        msg += "<b>Your forces are very tired and certainly won't fight well.</b>\n"
    elif attacker.fleet_readiness < 0:
        msg += "<b>Your forces seem to require rest, they won't be fighting as well\
         as they could in different circumstances.</b>\n"

    fa = 1
    if attacker.fleet_readiness < 0:
        fa = 1.0 - attacker.fleet_readiness / 130.0

    attfactor = race_info_list[attacker.get_race_display()].get("military_attack", 1.0) / \
                race_info_list[defender.get_race_display()].get("military_defence", 1.0) * fa
    deffactor = race_info_list[defender.get_race_display()].get("military_attack", 1.0) / \
                race_info_list[attacker.get_race_display()].get("military_defence", 1.0) / fa

    attacker.fleet_readiness -= battleReadinessLoss(attacker, defender)

    # defsatsbase = defsats = attacked_planet.defense_sats


    shields = shield_absorb * attacked_planet.shield_networks  #+ specopShieldingCalc(defid, fleetd.destid);


    attacker.save()

    msg += "\n\n attacked planet id: " + str(attacked_planet.id) + "\n def id: " +str(defender.id) + "\n  def fleets:" + str(defending_fleets)
    return msg

