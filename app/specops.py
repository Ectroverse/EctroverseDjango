import numpy as np
from app.constants import *
from app.models import *
from datetime import datetime

all_operations = ["Observe Planet"]
all_spells = ["Irradiate Ectrolium", "Incandescence"]
all_incantations = ["Survey System"]

psychicop_difficulty = {"Incandescence": 1, }
psychicop_requirement = {"Incandescence": 0, }
psychicop_self= {"Incandescence": 0, }
psychicop_cost= {"Incandescence": 30, }

def specopPsychicsReadiness(spell, user1, *args):
    if spell in psychicop_self:
        return psychicop_cost[spell]
#     finishthis function rewrite


def get_op_penalty(research, requirement):
    a = requirement - research
    if a <= 0:
        return 0
    da = pow(a, 1.20 )
    if da >= 150.0:
        return -1
    return da


def perform_spell(spell, psychics, status, user2ID):
    if spell not in psychicop_difficulty or spell not in psychicop_requirement or spell not in all_spells:
        return "This spell is broken/doesnt exist!"

    fa = 0.4 + (1.2 / 255.0) * (np.random.randint(0, 2147483647) & 255)

    attack = fa * race_info_list[status.get_race_display()].get("psychics_coeff", 1.0) * \
              psychics * (1.0 + 0.005 * status.research_percent_culture / psychicop_difficulty[spell] )

    penalty = get_op_penalty(status.research_percent_culture, psychicop_requirement[spell])

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

        News.objects.create(user1=User.objects.get(id=status.id),
                            empire1=status.empire,
                            news_type='PD',
                            date_and_time=datetime.now(),
                            is_personal_news=True,
                            is_empire_news=True,
                            extra_info=news_message,
                            tick_number=RoundStatus.objects.get().tick_number
                            )
        return message


