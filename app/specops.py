import numpy as np
from app.constants import *
from app.models import *
from datetime import datetime
from django.db.models import Sum

all_operations = ["Observe Planet"]
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


def specopPsychicsReadiness(spell, user1, *args):
    if args:
        user2 = args[0]

    if psychicop_specs[spell][3] is False and not user2:
        return -1

    penalty = get_op_penalty(user1.research_percent_culture, psychicop_specs[spell][0])
    if penalty == -1:
        return -1
    elif psychicop_specs[spell][3]:
        return int((1.0 + 0.01 * penalty) * psychicop_specs[spell][1])

    empire1 = Empire.objects.get(id=user1.empire)
    empire2 = Empire.objects.get(id=user2.empire)

    fa = (1 + user1.num_planets) / (1 + user2.num_planets)
    fb = (1 + empire1.planets) / (1 + empire2.planets)
    fa = pow(fa, 1.8)
    fb = pow(fb, 1.2)
    fa = 0.5 * (fa + fb)

    if fa < 0.75:
        fa = 0.75

    fa = (1.0 + 0.01 * penalty) * psychicop_specs[spell][1] * fa

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

    return fa


def get_op_penalty(research, requirement):
    a = requirement - research
    if a <= 0:
        return 0
    da = pow(a, 1.20)
    if da >= 150.0:
        return -1
    return da


def perform_spell(spell, psychics, status, *args):
    if spell not in psychicop_specs:
        return "This spell is broken/doesnt exist!"

    fa = 0.4 + (1.2 / 255.0) * (np.random.randint(0, 2147483647) & 255)

    attack = fa * race_info_list[status.get_race_display()].get("psychics_coeff", 1.0) * \
             psychics * (1.0 + 0.005 * status.research_percent_culture / psychicop_specs[spell][2])

    penalty = get_op_penalty(status.research_percent_culture, psychicop_specs[spell][0])

    if penalty == -1:
        return

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
        status.crystals
        cry_converted = attack * 5
        if cry_converted > status.crystals:
            cry_converted = status.crystals
        cry_converted = int(cry_converted)
        status.crystals -= cry_converted

        energy = int(cry_converted * 24.0 * (1.0 + 0.01 * status.research_percent_culture))
        status.energy += energy
        status.psychic_readiness -= specopPsychicsReadiness(spell, status)
        status.save()
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

        status.psychic_readiness -= specopPsychicsReadiness(spell, status, user2)
        status.save()

        news_message = str(destroyed_ectro) + " ectrolium was destroyed!"
        message = "You have irradiated " + str(destroyed_ectro) + " ectrolium!"

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

        status.psychic_readiness -= specopPsychicsReadiness(spell, status, user2)
        status.save()

    if spell =="Phantoms":
        phantom_cast = round(attack / 2)
        fleet1.phantom += phantom_cast
        fleet1.save()

        news_message = status.user_name + " has summoned " + str(phantom_cast) + " Phantoms to fight in their army!"
        message = "You have summoned " + str(phantom_cast) + " Phantoms to join your army!"

        status.psychic_readiness -= specopPsychicsReadiness(spell, status)
        status.save()

    if spell =="Grow Planet's Size":
        planet = random.choice(Planet.objects.filter(owner=status.user))
        grow = (attack * 1.3)
        growth = np.clip(round(200 * grow / status.networth / 2 / status.num_planets),0,300)
        planet.size += growth
        planet.save()

        news_message = status.user_name + " planet " + str(planet.x) + "," + str(planet.y) + ":" + str(planet.i) + " has grown " + str(growth)
        message = "Your planet  " + str(planet.x) + "," + str(planet.y) + ":" + str(planet.i) + " has grown by " + str(growth)

        status.psychic_readiness -= specopPsychicsReadiness(spell, status)
        status.save()

        news_message = str(psychics_loss1) + " psychics were lost by " + status.user_name + \
                       " and " + str(psychics_loss2) + " were lost by " + user2.user_name + "!"
        message = "You have assaulted " + str(psychics_loss2) + " enemy psychics of " + user2.user_name + \
                  " however " + str(psychics_loss1) + " of your psychics have also suffered critical brain damages!"

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


'''
char *cmdAgentopName[CMD_AGENTOP_NUMUSED] =
{
"Spy Target",
"Observe Planet",
"Network Virus",
"Infiltration",
"Bio Infection",
"Energy Transfer",
"Military Sabotage",
"Nuke Planet",
"High Infiltration",
"Planetary Beacon",
"Diplomatic Espionage",
"Steal Resources"
};

char *cmdPsychicopName[CMD_PSYCHICOP_NUMUSED] =
{
"Irradiate Ectrolium",
"Dark Web",
"Incandescence",
"Black Mist",
"War Illusions",
"Psychic Assault",
"Phantoms",
"Enlightenment",
"Grow Planet's Size"
};

char *cmdGhostopName[CMD_GHOSTOP_NUMUSED] =
{
"Sense Artefact",
"Survey System",
"Planetary Shielding",
"Portal Force Field",
"Vortex Portal",
"Mind Control",
"Energy Surge",
"Call to Arms"
};


int cmdAgentopTech[CMD_AGENTOP_NUMUSED] =
{
0, 0, 25, 40, 60, 80, 100, 120, 160, 100, 40, 80
};



int cmdGhostopTech[CMD_GHOSTOP_NUMUSED] =
{
20, 40, 60, 80, 100, 120, 140, 110
};


float cmdAgentopReadiness[CMD_AGENTOP_NUMUSED] =
{
12.0, 5.0, 22.0, 18.0, 25.0, 22.0, 30.0, 20.0, 40.0, 7.0, 15.0, 22.0
};



int cmdGhostopReadiness[CMD_GHOSTOP_NUMUSED] =
{
50, 20, 40, 30, 60, 40, 70, 20
};


float cmdAgentopDifficulty[CMD_AGENTOP_NUMUSED] =
{
1.0, 1.0, 3.5, 2.5, 3.0, 2.5, 3.5, 5.0, 6.0, 1.0, 1.5, 2.5
};



float cmdGhostopDifficulty[CMD_GHOSTOP_NUMUSED] =
{
1.0, 1.0, 2.0, 1.5, 1.0, 5.0, 6.0, 2.0
};

int cmdAgentopStealth[CMD_AGENTOP_NUMUSED] =
{
1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0
};
'''
