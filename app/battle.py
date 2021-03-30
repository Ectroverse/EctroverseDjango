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


    # msg += "\n\n attstats" + str(attstats) + " attacker.get_race_display() " + str(attacker.get_race_display())
    # msg += "\n\n defstats" + str(defstats) + " defender.get_race_display() " + str(defender.get_race_display())
    #
    # msg += "\n\n defending_fleets1" + str(defending_fleets)
    # msg += "\n\n protection" + str(attacked_planet.protection)

    # portal coverage, th
    for key, value in defending_fleets.items():
        defending_fleets[key] = value * attacked_planet.protection/100

    # msg += "\n\n defending_fleets2" + str(defending_fleets)

    if attacker.fleet_readiness < -100:
        msg += "<b>Your forces require time to recover and prepare before engaging a new battle.\
         Forcing them to attack would have more than disastrous consequences.</b>\n"
        return msg
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

    ####################
    #      PHASE 1     #
    ####################
    attacker_flee = False

    '''
    #            air attack, air defence, ground attack, ground defence
    unit_stats = [[0, 64, 24,110, 4,  4], # bombers
              [20,120,  0, 60, 4, 3], # fighters
              [0, 60,  0, 50, 4,  5], # transports
              [70,600, 70,600, 4,12], # cruisers
              [0,540,  0,540, 4, 14], # carriers
              [0, 48,  3, 16, 0,  1], # soldiers
              [0, 48,  5, 30, 0,  1], # droids
              [28,140, 10, 90, 0, 4], # goliaths
              [32,130, 20,130, 10,7], # phantoms
              [0,  0,  0,  0, 0,  2], # psychics
              [0,  0,  0,  0, 8,  2], # agents
              [0,  0,  0,  0, 8,  6], # ghost ships
              [0,  0,  0,  0, 3, 30]] # explors

    unit_labels = ["Bombers","Fighters","Transports","Cruisers","Carriers","Soldiers",\
               "Droids","Goliaths","Phantoms","Psychics","Agents","Ghost Ships","Exploration Ships"]
               
    defending_fleets1
    {'bomber__sum': 0, 'fighter__sum': 110, 'transport__sum': 84, 'cruiser__sum': 50, 'carrier__sum': 50,
     'soldier__sum': 100, 'droid__sum': 0, 'goliath__sum': 0, 'phantom__sum': 0, 'wizard__sum': 38, 'agent__sum': 50,
     'ghost__sum': 0, 'exploration__sum': 1}
     
    '''
    # ========= Calculate damage factors =========#


    attdam = attacking_fleet.cruiser * attstats["Cruisers"][0] + \
             attacking_fleet.phantom * attstats["Phantoms"][0]

    defdam = defending_fleets["cruiser__sum"] * defstats["Cruisers"][0] + \
             defending_fleets["phantom__sum"]* defstats["Phantoms"][0] + \
             sats_attack * attacked_planet.defense_sats


    attdam = attdam * attfactor * ((1.0 + 0.005 * attacker.research_percent_military)/ \
                                    (1.0 + 0.005 * defender.research_percent_military))

    defdam = defdam * deffactor * ((1.0 + 0.005 * defender.research_percent_military)/ \
                                    (1.0 + 0.005 * attacker.research_percent_military))

    if attdam >= 1.0:
        attdam -= attdam * (1.0 - pow(2.5, -(shields / attdam)))

    # ========= Determine if anyone will flee =========#

    # damage is too high defender flee
    if (defdam < 1.0) or ((attdam / defdam) * 10.0 >= defender.long_range_attack_percent):
        # goto battleDefFlee1;
        # results[3] |= 0x100; What is this?
        pass
    # defender flees, if settings are 100% this means attacker deals 10x more damage than defender
    if (attdam / defdam) * 100.0 >= defender.long_range_attack_percent:
        defdam *= 0.15
        attdam *= 0.10
        # results[3] |= 0x100;
    # attacker flees, same logic as above
    if (attdam >= 1.0) and ((defdam / attdam) * 100.0 >= defender.long_range_attack_percent):
        defdam *= 0.20
        attdam *= 0.10
        attacker_flee = True

    # ========= Damage to attacking fleets =========#
    hpcarrier = attacking_fleet.carrier * attstats["Carriers"][1]
    hpcruiser = attacking_fleet.cruiser * attstats["Cruisers"][1]
    hpphantom = attacking_fleet.phantom * attstats["Phantoms"][1]
    hptotal = hpcarrier + hpcruiser + hpphantom
    damcarrier = 0
    damcruiser = 0
    damphantom = 0

    # percentage of damage that wil be received by the unit
    if hptotal:
        damcarrier = hpcarrier / hptotal
        damcruiser = hpcruiser / hptotal
        damphantom = hpphantom / hptotal

    # calc attacking/defending cruiser ratio, transfer the damage from carriers to cruisers and phantoms
    fa = 0.0
    if defending_fleets["cruiser__sum"] > 0:
        fa = attacking_fleet.cruiser / defending_fleets["cruiser__sum"]
    damcarrier *= pow(1.50, -fa)

    fb = damcarrier + damcruiser + damphantom

    # msg += "\n\n hpphantom" + str(hpphantom) + "damphantom" + str(damphantom)

    if fb >= 0.00001:
        fa = defdam / fb
        damcarrier *= fa
        damcruiser *= fa
        damphantom *= fa


    msg += "\n\n damcarrier" + str(damcarrier) + " hpcarrier " + str(hpcarrier)
    msg += "\n\n damcruiser" + str(damcruiser) + " hpcarrier " + str(hpcruiser)
    msg += "\n\n damphantom" + str(damphantom) + " hpcarrier " + str(hpphantom)

    if damcarrier > hpcarrier:
        damcruiser += damcarrier - hpcarrier
    if damcruiser > hpcruiser:
        damphantom += damcruiser - hpcruiser
    if damphantom > hpphantom:
        damcruiser += damphantom - hpphantom


    '''
        unit_labels = ["Bombers","Fighters","Transports","Cruisers","Carriers","Soldiers",\
               "Droids","Goliaths","Phantoms","Psychics","Agents","Ghost Ships","Exploration Ships"]
               '''

    attacker_carrier_loss_1phase = min(attacking_fleet.carrier, int(damcarrier / attstats["Carriers"][1]))
    attacker_cruiser_loss_1phase = min(attacking_fleet.cruiser, int(damcruiser / attstats["Cruisers"][1]))
    attacker_phantom_loss_1phase = min(attacking_fleet.phantom, int(damphantom / attstats["Phantoms"][1]))

    msg += "\n\n attacker_carrier_loss_1phase" + str(attacker_carrier_loss_1phase)
    msg += "\n\n attacker_cruiser_loss_1phase" + str(attacker_cruiser_loss_1phase)
    msg += "\n\n attacker_phantom_loss_1phase" + str(attacker_phantom_loss_1phase)

    # ========= Damage to defending fleets =========#
    defending_fleets1
    {'bomber__sum': 0, 'fighter__sum': 110, 'transport__sum': 84, 'cruiser__sum': 50, 'carrier__sum': 50,
     'soldier__sum': 100, 'droid__sum': 0, 'goliath__sum': 0, 'phantom__sum': 0, 'wizard__sum': 38, 'agent__sum': 50,
     'ghost__sum': 0, 'exploration__sum': 1}

    hpcruiser = defending_fleets["cruiser__sum"] *  defstats["Cruisers"][1]
    hpphantom = defending_fleets["phantom__sum"] *  defstats["Phantoms"][1]
    hpsats = attacked_planet.defense_sats * sats_defence
    hptotal = hpcruiser + hpphantom + hpsats;
    damcruiser = 0
    damphantom = 0
    damsats = 0

    if hptotal:
        damcruiser =  hpcruiser /  hptotal
        damphantom = hpphantom / hptotal
        damsats = hpsats / hptotal


    fa = 0.0
    if attacking_fleet.cruiser > 0:
        fa = defending_fleets["cruiser__sum"] / attacking_fleet.cruiser
    damsats *= pow(2.80, -fa)

    fb = damcruiser + damphantom + damsats

    if fb >= 0.00001:
        fa = attdam / fb
        damcruiser *= fa
        damphantom *= fa
        damsats *= fa


    if damcruiser > hpcruiser:
        damphantom += damcruiser - hpcruiser
    if damphantom > hpphantom:
        damsats += damphantom - hpphantom
    if damsats > hpsats:
        damcruiser += damsats - hpsats


    defender_cruiser_loss_1phase = min(defending_fleets["cruiser__sum"], int(damcruiser / defstats["Cruisers"][1]))
    defender_phantom_loss_1phase = min(defending_fleets["phantom__sum"], int(damphantom / defstats["Phantoms"][1]))
    defender_defsats_loss_1phase = min(attacked_planet.defense_sats, int(damsats / sats_defence))
    attacked_planet.defense_sats -= defender_defsats_loss_1phase
    attacked_planet.save()

    # battlePhaseUpdate(attunit, & results[4 + 0 * CMD_UNIT_FLEET] );
    # battlePhaseUpdate(defunit, & results[4 + 1 * CMD_UNIT_FLEET] );

    # if (flee)
    #     goto
    #     battleAttFlee;
    # battleDefFlee1:

    ####################
    #      PHASE 2     #
    ####################

    ####################
    #      PHASE 3     #
    ####################

    ####################
    #      PHASE 4     #
    ####################

    attacker.save()

    msg += "\n\n attacked planet id: " + str(attacked_planet.id) + "\n def id: " +str(defender.id) + "\n  def fleets:" + str(defending_fleets)
    return msg

