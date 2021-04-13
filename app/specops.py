import numpy as np
from app.constants import *
from app.models import *
from datetime import datetime
from django.db.models import Sum
import random

all_spells = ["Irradiate Ectrolium",
              "Dark Web",
              "Incandescence",
              "Black Mist",
              "War Illusions",
              "Psychic Assault",
              "Phantoms",
              "Enlightenment",
              "Grow Planet's Size"]

all_incantations = ["Survey System"]

# tech, readiness, difficulty, self-spell
psychicop_specs = {
    "Irradiate Ectrolium": [0, 12, 1.5, False, 'IE',
                            "Your psychics will attempt to irradiate the target's ectrolium reserves, making it unusable.", ],
    "Incandescence": [0, 30, 2.5, True, 'IN',
                      "Your psychics will convert crystal into vast amounts of energy."],
    "Dark Web": [10, 18, 2.4, True, 'DW',
                 "Creating a thick dark web spreading in space around your planets will make them much harder to locate and attack."],
    "Black Mist": [50, 24, 3.0, False, 'BM',
                   "Creating a dense black mist around the target's planets will greatly reduce the effectiveness of solar collectors."],
    "War Illusions": [70, 30, 4.0, True, 'WI',
                      "These illusions will help keeping enemy fire away from friendly units."],
    "Psychic Assault": [90, 35, 1.7, False, 'PA',
                        "Your psychics will engage the targeted faction's psychics, to cause large casualities."],
    "Phantoms": [110, 40, 5.0, True, 'PM',
                 "Your psychics will create etheral creatures to join your fleets in battle."],
    "Grow Planet's Size": [110, 20, 2.5, True, 'GP',
                           "Your psychics will try to create new land on one of the planets of your empire. \
                <br>The more planets and psychic power you have, the better are the chances."],
    "Enlightenment": [120, 35, 1.0, True, 'EN',
                      "Philosophers and scientists will try to bring a golden Age of Enlightenment upon your empire."],
}

all_operations = ["Spy Target",
                "Observe Planet",
                "Network Infiltration",
                "Infiltration",
                "Diplomatic Espionage",
                "Bio Infection",
                "Energy Transfer",
                "Military Sabotage",
                "Planetary Beacon",
                "Computer virus",
                "Nuke Planet",
                "Maps theft",
                "High Infiltration",
                ]

# tech, readiness, difficulty, stealth
agentop_specs = {
    "Spy Target": [0, 12, 1.5, True, 'ST',
                            "Spy target will reveal information regarding an faction resources and readiness.", ],
    "Observe Planet": [0, 5, 1.0, True, 'OP',
                      "Your agents will observe the planet and provide you with all information regarding it, habited or not."],
    "Network Infiltration": [25, 22, 3.5, False, 'NW',
                 "Your agents will try to infiltrate research network in order to steal new technologies."],
    "Infiltration": [40, 18, 2.5, True, 'IF',
                   "Infiltrating the target network will provide you with information regarding its resources, research and buildings."],
    "Diplomatic Espionage": [40, 15, 1.5, True, 'DE',
                             "Your diplomats will try to gather information regarding operations and spells, currently affecting the target faction."],
    "Bio Infection": [60, 25, 3.0, False, 'BI',
                      "Your agents will attempt to spread a dangerous infection which will kill most of the population and spread in nearby planets."],
    "Energy Transfer": [80, 22, 2.5, False, 'ET',
                        "Your agents will infiltrate the enemy energy storage facilities and transfer energy to your own energy storage."],
    "Military Sabotage": [100, 30, 3.5, False, 'MT',
                 "Through an enemy portal, your agents will attempt to reach the enemy fleet and destroy military units."],
    "Planetary Beacon": [100, 7, 1.0, False, 'PB',
                         "Your agents will attempt to place a beacon on target planet, if successful it will remove any dark webs present."],
    "Computer virus": [120, 22, 2.5, False, 'CV',
                       "Your hackers will try to plant a nasty computer virus that will increase targets resources decay rate!"],
    "Nuke Planet": [120, 20, 5.0, False, 'NP',
                           "Your agents will place powerful nuclear devices on the surface of the planet, destroying all buildings and units, leaving in uninhabited."],
    "Maps theft": [140, 40, 4.5, False, 'MT',
                   "Your agents will try to steal the maps of the enemie's territory!"],
    "High Infiltration": [160, 40, 6.0, False, 'HI',
                      "Performing this operation will provide you with detailled information about an faction for several weeks."],
}

inca_specs= {}


def specopReadiness(specop, type, user1, *args):
    user2 = None
    if args:
        user2 = args[0]

    if type == "Spell":
        penalty = get_op_penalty(user1.research_percent_culture, specop[0])
        if user2 == None and specop[3] == False:
            return -1
        if specop[3]: #if self op
            return int((1.0 + 0.01 * penalty) * specop[1])
    elif type == "Inca":
        penalty = get_op_penalty(user1.research_percent_culture, specop[0])
        if specop[3]: #if self op
            return int((1.0 + 0.01 * penalty) * specop[1])
    else:
        penalty = get_op_penalty(user1.research_percent_operations, specop[0])


    if penalty == -1:
        return -1


    empire1 = user1.empire
    empire2 = user2.empire

    fa = (1 + user1.num_planets) / (1 + user2.num_planets)
    fb = (1 + empire1.planets) / (1 + empire2.planets)
    fa = pow(fa, 1.8)
    fb = pow(fb, 1.2)
    fa = 0.5 * (fa + fb)

    if fa < 0.75:
        fa = 0.75

    fa = (1.0 + 0.01 * penalty) * specop[1] * fa

    relations_from_empire = Relations.objects.filter(empire1=empire1)
    relations_to_empire = Relations.objects.filter(empire2=empire2)

    war = False
    ally = False
    nap = False

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

    if fa > 300:
        fa = 300

    return round(fa)


def get_op_penalty(research, requirement):
    a = requirement - research
    if a <= 0:
        return 0
    da = pow(a, 1.20)
    if da >= 150.0:
        return -1
    return round(da)


def perform_spell(spell, psychics, status, *args):
    if spell not in psychicop_specs:
        return "This spell is broken/doesnt exist!"

    fa = 0.4 + (1.2 / 255.0) * (np.random.randint(0, 2147483647) & 255)

    attack = fa * race_info_list[status.get_race_display()].get("psychics_coeff", 1.0) * \
             psychics * (1.0 + 0.005 * status.research_percent_culture / psychicop_specs[spell][2])

    penalty = get_op_penalty(status.research_percent_culture, psychicop_specs[spell][0])

    if penalty == -1:
        return "You don't have enough psychic research to perform this spell!"

    if penalty > 0:
        attack /= 1.0 + 0.01 * penalty

    fleet1 = Fleet.objects.get(owner=status.id, main_fleet=True)

    news_message = ""
    message = ""

    if args[0]:
        user2 = args[0]
        if user2 == status and psychicop_specs[spell][3] is False:
            message = "You cannot perform this spell on yourself!"
            return message
        empire2 = user2.empire
        fleet2 = Fleet.objects.get(owner=user2.id, main_fleet=True)
        psychics2 = Fleet.objects.filter(owner=user2.id).aggregate(Sum('wizard'))
        psychics2 = psychics2['wizard__sum']
        print(psychics2)
        defence = race_info_list[user2.get_race_display()].get("psychics_coeff", 1.0) * psychics2 * \
                  (1.0 + 0.005 * user2.research_percent_culture)
        success = attack / (defence + 1)

    if penalty > 0:
        attack = attack / (1.0 + 0.01 * penalty)

    if spell == "Incandescence":
        cry_converted = attack * 5
        if cry_converted > status.crystals:
            cry_converted = status.crystals
        cry_converted = int(cry_converted)
        status.crystals -= cry_converted

        energy = int(cry_converted * 24.0 * (1.0 + 0.01 * status.research_percent_culture))
        status.energy += energy
        news_message = str(cry_converted) + " crystals were converted into " + str(energy) + " energy!"
        message = "Your " + str(cry_converted) + " crystals were converted into " + str(energy) + " energy!"

    if spell == "Irradiate Ectrolium":
        destroyed_ectro = 0
        if success > 1:
            frac_destroyed = 0.2
        else:
            frac_destroyed = (20.0 / 0.6) * (success - 0.4) * 0.01

        if frac_destroyed > 0:
            destroyed_ectro = int(frac_destroyed * user2.ectrolium)
            user2.ectrolium -= destroyed_ectro
            user2.military_flag = 1
            user2.save()

        news_message = str(destroyed_ectro) + " ectrolium was destroyed!"
        message = "You have irradiated " + str(destroyed_ectro) + " ectrolium!"

    if spell == "Black Mist":
        if success >= 1.0:
            effect = 25
        else:
            effect = int((25.0 / 0.6) * (success - 0.4))
        if effect > 0:
            time = random.randint(26, 57)
            Specops.objects.create(user_to=user2.user,
                                   user_from=status.user,
                                   specop_type='S',
                                   name="Black Mist",
                                   specop_strength=effect,
                                   ticks_left=time)
            news_message = " solar power reduced by " + str(effect) + "%!"
            message = "A black mist is spreading over " + str(user2.user_name) + \
                      " planets, reducing solar collectors efficiency by " + str(effect)
        else:
            news_message = " solar power wasn't reduced!"
            message = "Your psychic power wasn't enough to cast a black mist!"

    if spell == "Psychic Assault":
        refdef = pow(attack / (attack + defence), 1.1)
        refatt = pow(defence / (attack + defence), 1.1)
        tlosses = 0.2

        psychics_loss1 = min(int(refatt * tlosses * psychics), psychics)
        fleet1.wizard -= psychics_loss1
        fleet1.save()

        psychics_loss2 = min(int(refdef * tlosses * psychics2), psychics2)
        fleet2.wizard -= psychics_loss2
        fleet2.save()

        news_message = str(psychics_loss1) + " psychics were lost by " + status.user_name + \
                       " and " + str(psychics_loss2) + " were lost by " + user2.user_name + "!"
        message = "You have assaulted " + str(psychics_loss2) + " enemy psychics of " + user2.user_name + \
                  " however " + str(psychics_loss1) + " of your psychics have also suffered critical brain damages!"

    if spell =="Phantoms":
        phantom_cast = round(attack / 2)
        fleet1.phantom += phantom_cast
        fleet1.save()

        news_message = status.user_name + " has summoned " + str(phantom_cast) + " Phantoms to fight in their army!"
        message = "You have summoned " + str(phantom_cast) + " Phantoms to join your army!"

    if spell =="Grow Planet's Size":
        planet = random.choice(Planet.objects.filter(owner=status.user))
        grow = (attack * 1.3)
        growth = np.clip(round(200 * grow / status.networth / 2 * (status.num_planets/10)),0,300)
        planet.size += growth
        planet.save()

        news_message = status.user_name + "'s planet " + str(planet.x) + "," + str(planet.y) + ":" + str(planet.i) + " has grown by " + str(growth)
        message = "Your planet  " + str(planet.x) + "," + str(planet.y) + ":" + str(planet.i) + " has grown by " + str(growth)


    status.psychic_readiness -= specopReadiness(psychicop_specs[spell],"Spell", status, user2)
    status.save()

    if psychicop_specs[spell][3] == True:
        News.objects.create(user1=User.objects.get(id=status.id),
                            user2=User.objects.get(id=status.id),
                            empire1=status.empire,
                            fleet1=spell,
                            news_type='PD',
                            date_and_time=datetime.now(),
                            is_personal_news=True,
                            is_empire_news=True,
                            extra_info=news_message,
                            tick_number=RoundStatus.objects.get().tick_number
                            )
    else:
        News.objects.create(user1=User.objects.get(id=status.id),
                            user2=User.objects.get(id=user2.id),
                            empire1=status.empire,
                            empire2=empire2,
                            fleet1=spell,
                            news_type='PA',
                            date_and_time=datetime.now(),
                            is_personal_news=True,
                            is_empire_news=True,
                            extra_info=news_message,
                            tick_number=RoundStatus.objects.get().tick_number
                            )

        News.objects.create(user1=User.objects.get(id=user2.id),
                            user2=User.objects.get(id=status.id),
                            empire1=empire2,
                            empire2=status.empire,
                            fleet1=spell,
                            news_type='PD',
                            date_and_time=datetime.now(),
                            is_personal_news=True,
                            is_empire_news=True,
                            extra_info=news_message,
                            tick_number=RoundStatus.objects.get().tick_number
                            )
    return message

    # if news_message2_empire1:
    #
    #
    #
    # if news_message2_empire2:


def perform_operation(agent_fleet):
    operation = agent_fleet.specop
    agents = agent_fleet.agent
    user = agent_fleet.owner
    target_planet = agent_fleet.target_planet
    user1 = UserStatus.objects.get(id=user.id)
    if operation not in agentop_specs:
        return "This operation is broken/doesnt exist!"

    fa = 0.6 + (0.8/ 255.0) * (np.random.randint(0, 2147483647) & 255)

    attack = fa * race_info_list[user1.get_race_display()].get("agents_coeff", 1.0) * \
             agents * (1.0 + 0.01 * user1.research_percent_operations / agentop_specs[operation][2])

    penalty = get_op_penalty(user1.research_percent_operations, agentop_specs[operation][0])

    if penalty == -1:
        return "You don't have enough operations research to perform this spell!"

    if penalty > 0:
        attack /= 1.0 + 0.01 * penalty

    defense = 50
    user2 = None
    stealth = True
    empire2 = None

    if target_planet.owner is not None:
        user2 = UserStatus.objects.get(id=target_planet.owner.id)
        empire2 = user2.empire
        fleet2 = Fleet.objects.get(owner=user2.id, main_fleet=True)
        agents2 = fleet2.agent
        defense = agents2 * race_info_list[user2.get_race_display()].get("agents_coeff", 1.0) * \
                  (1.0 + 0.01 * user2.research_percent_operations)

    success = attack / (defense + 1)
    news_message = ""
    news_message2 = ""

    if success < 2.0 and target_planet.owner is not None:
        stealth = False
        refdef = 0.5 * pow((0.5 * success), 1.1)
        refatt = 1.0 - refdef
        tlosses = 1.0 - pow((0.5 * success), 0.2)
        fc = 0.75 + (0.5 / 255.0) * (np.random.randint(0, 2147483647) & 255)
        loss1 = round(fc * refatt * tlosses *agents)
        fc = 0.75 + (0.5 / 255.0) * (np.random.randint(0, 2147483647) & 255)
        loss2 = round(fc * refdef * tlosses * agents)
        agent_fleet.agent -= loss1
        agent_fleet.save()
        fleet2.agent -= loss2
        fleet2.save()
        news_message = "Attacker lost" + str(loss1) + "agents. Defender lost:" + str(loss2) + "agents."
        news_message2 = "Attacker lost" + str(loss1) + "agents. Defender lost:" + str(loss2) + "agents."


    if operation == "Observe Planet":
        if success < 0.4:
            news_message += "no information was gathered about this planet!"
        if success >= 0.4:
            news_message += "planet size: " + str(target_planet.size)
        # if success >= 1.0:
        #     news_message += "artefact: " + target_planet.artefact
        if success >= 0.9:
            if target_planet.bonus_solar > 0:
                news_message += "\nsolar bonus: " + str(target_planet.bonus_solar)
            if target_planet.bonus_fission > 0:
                news_message += "\nfission bonus: " + str(target_planet.bonus_fission)
            if target_planet.bonus_mineral > 0:
                news_message += "\nmineral bonus: " + str(target_planet.bonus_mineral)
            if target_planet.bonus_crystal > 0:
                news_message += "\ncrystal bonus: " + str(target_planet.bonus_crystal)
            if target_planet.bonus_ectrolium > 0:
                news_message += "\nectrolium bonus: " + str(target_planet.bonus_ectrolium)
        if target_planet.owner is not None:
            if success >= 0.5:
                news_message += "\ncurrent population: " + str(target_planet.current_population)
            if success >= 0.6:
                news_message += "\nmax population: " + str(target_planet.max_population)
            if success >= 0.7:
                news_message += "\nprotection: " + str(target_planet.protection)
            if success >= 0.8:
                news_message += "\nsolar collectors: " + str(target_planet.solar_collectors)
                news_message += "\nfission_reactors: " + str(target_planet.fission_reactors)
                news_message += "\nmineral_plants: " + str(target_planet.mineral_plants)
                news_message += "\ncrystal_labs: " + str(target_planet.crystal_labs)
                news_message += "\nrefinement_stations: " + str(target_planet.refinement_stations)
                news_message += "\ncities: " + str(target_planet.cities)
                news_message += "\nresearch_centers: " + str(target_planet.research_centers)
                news_message += "\ndefense_sats: " + str(target_planet.defense_sats)
                news_message += "\nshield_networks: " + str(target_planet.shield_networks)
            if success >= 1.0:
                if target_planet.portal:
                    news_message += "\nportal: present"
                elif target_planet.portal_under_construction:
                    news_message += "\nportal: under construction"
                else:
                    news_message += "\nportal: absent"
        scouting = Scouting.objects.filter(planet=target_planet).first()
        if scouting is None:
            Scouting.objects.create(user=user, planet=target_planet, scout=success)
        else:
            if scouting.scout < success:
                scouting.scout = success
                scouting.save()

    if operation == "Spy Target":
        if success < 0.4:
            news_message += "No information was gathered about this faction!"
        if success >= 0.5:
            news_message += "Fleet readiness: " + str(user2.fleet_readiness)
        if success >= 0.7:
            news_message += "\nPsychic readiness: " + str(user2.psychic_readiness)
        if success >= 0.9:
            news_message += "\nAgent readiness: " + str(user2.agent_readiness)
        if success >= 1.0:
            news_message += "\nEnergy: " + str(user2.energy)
        if success >= 0.6:
            news_message += "\nMinerals: " + str(user2.minerals)
        if success >= 0.4:
            news_message += "\nCrystals: " + str(user2.crystals)
        if success >= 0.8:
            news_message += "\nEctrolium: " + str(user2.ectrolium)
        if success >= 0.9:
            news_message += "\nPopulation: " + str(user2.population)

    if operation == "Network Infiltration":
        lost_research_pct = 3
        if success < 1.0:
            lost_research_pct = round((3.0 / 0.6) * (success - 0.4), 2)
        if lost_research_pct > 0:
            fa = 0.3 + (0.7 / 255.0) * (np.random.randint(0, 2147483647) & 255)
            gained_research_pct = round(lost_research_pct * fa, 2)
            for research in researchNames:
                lost_research_points = int(getattr(user2, research) * (0.01 * lost_research_pct))
                research_points_new2 = getattr(user2, research) - lost_research_points
                setattr(user2, research, research_points_new2)
                research_points_new1 = getattr(user1, research) + int(lost_research_points * fa)
                setattr(user1, research, research_points_new1)
            news_message += "\n" + str(lost_research_pct) + " research % was lost by the defender! " + \
                                   str(gained_research_pct) + "research % was stolen for our faction!"
            news_message2 += "\n" + str(lost_research_pct) + " research % was lost!"
            user2.save()
            user1.save()
        else:
            news_message += "\nNo research was stolen!"
            news_message2 += "\nNo research was lost!"

    if operation == "Diplomatic Espionage":
        if success >= 1.0:
            if success >= 2:
                time = 50
            else:
                time = pow(7, success)
            Specops.objects.create(user_to=user2.user,
                                   user_from=user1.user,
                                   specop_type='O',
                                   name="Diplomatic Espionage",
                                   ticks_left=time)
        else:
            news_message = "Your agents couldn't gather any information!"

    user1.agent_readiness -= specopReadiness(agentop_specs[operation],"Operation", user1, user2)
    user1.save()

    if empire2 is None:
        News.objects.create(user1=User.objects.get(id=user1.id),
                        user2=None,
                        empire1=user1.empire,
                        fleet1=operation,
                        news_type='AA',
                        date_and_time=datetime.now(),
                        is_personal_news=True,
                        is_empire_news=True,
                        extra_info=news_message,
                        tick_number=RoundStatus.objects.get().tick_number,
                        planet=target_planet
                        )
    else:
        News.objects.create(user1=User.objects.get(id=user1.id),
                        user2=User.objects.get(id=user2.id),
                        empire1=user1.empire,
                        empire2=empire2,
                        fleet1=operation,
                        news_type='AA',
                        date_and_time=datetime.now(),
                        is_personal_news=True,
                        is_empire_news=True,
                        extra_info=news_message,
                        tick_number=RoundStatus.objects.get().tick_number,
                        planet=target_planet
                        )
        if not stealth:
            user2.military_flag = 1
            News.objects.create(user1=User.objects.get(id=user2.id),
                        user2=User.objects.get(id=user1.id),
                        empire1=empire2,
                        empire2=user1.empire,
                        fleet1=operation,
                        news_type='AD',
                        date_and_time=datetime.now(),
                        is_personal_news=True,
                        is_empire_news=True,
                        extra_info=news_message2,
                        tick_number=RoundStatus.objects.get().tick_number,
                        planet=target_planet

                        )
    return news_message