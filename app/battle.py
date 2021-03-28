from django.db.models import Q, Sum
from .models import *


def attack_planet(attacking_fleet):
    attacked_planet = Planet.objects.get(x=attacking_fleet.x,y=attacking_fleet.y,i=attacking_fleet.i)
    defender = UserStatus.objects.get(id=attacked_planet.owner.id)
    defending_fleets = Fleet.objects.filter(Q(owner=defender.id), Q(main_fleet=True)|\
                    Q(on_planet=True, x=attacking_fleet.x, y =attacking_fleet.y, i=attacking_fleet.i ) ).\
        aggregate(Sum('bomber'),Sum('fighter'),Sum('transport'),Sum('cruiser'),Sum('carrier'),Sum('soldier'),\
                  Sum('droid'),Sum('goliath'),Sum('phantom'),Sum('wizard'),Sum('agent'),Sum('ghost'),Sum('exploration'))
    print(defending_fleets)

    msg = "attacked planet id: " + str(attacked_planet.id) + " def id: " +str(defender.id) + " <br>  def fleets:" + str(defending_fleets)
    return msg