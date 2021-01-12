import numpy as np
from .constants import *


# This is where longer formulas should go, 1-3 liners can go inside process_tick.py

def explore_FR_cost(num_planets, num_explos_traveling):
    return int(np.floor((num_planets + num_explos_traveling)/4.0 + 3)) # its either +3 or +10 depending on the round settings, not sure which one is normal
    # 27% FR for 97 planets

def attack_FR_cost(your_planets, targets_planets): # from battleReadinessLoss in battle.c
    fa = (1+your_planets) / (1+targets_planets)
    fa = fa**1.3
    if target_is_empiremate:
        fb = 1.0
        max_fr = 16.0
    else:
        # TODO count the number of players active in my empire within last 18 hours, nActive
        # TODO count the number of players active in their empire within last 18 hours, nActive2

        # we get the factor doing the number of max player in the emp * 2 - the active one / by the number of max player
        # so 1 active in a emp of one do (7*2-1)/7 = 1.85
        # 2 active in a emp of 3 do (7*2-2)/7 = 1.7
        # if its a full empire and everyone is active, it will be 1, which is the lowest number
        # if no one is active then it will be a 2, which is the highest it can be
        # If everyone is active and same empire size, fb = fa
        nMax = max_players_per_family
        fFactor1 = (nMax*2 - nActive) / nMax # if its SS round, this number is either a 2 or 1 depending if the user was active
        fFactor2 = (nMax*2 - nActive2) / nMax
        fb = (1 + your_planets*fFactor1) / (1 + targets_planets*fFactor2) # if target is inactive in SS round, its like attacker has twice the number of planets
        fb = fb**1.8
        max_fr = 100.0

        fdiv = 0.5 # determines how fa and fb are combined.  0.5 means they are avged
        if fb < fa:
            fdiv = 0.5 * (fb / fa)**0.8

        fa = ( fdiv * fa ) + ( (1.0-fdiv) * fb )
        fa *= 11.5

        # Caps lower end of FR cost
        fa = max(fa, 5.75)

        # Divide by 3 if its an empiremate or you are at war with this empire
        if target_is_empiremate or at_war_with_empire:
            fa /= 3.0

        # Multiply by 3.0 if it's an ally
        elif empire_is_an_ally:
            fa *= 3.0

        # Cap lower end to 50 if you have a NAP
        elif NAP_with_target:
            fa = max(fa, 50)

        if CMD_RACE_SPECIAL_CULPROTECT and not empire_is_an_ally:
	        fa *= np.log10(targets_culture_research + 10)

        #furti arti
        #if(( main2d->artefacts & ARTEFACT_128_BIT)&&(maind->empire != main2d->empire))
        #	fa *= log10(main2d->totalresearch[CMD_RESEARCH_CULTURE]+10);

        # Cap upper end to max_fr
        fa = min(fa, max_fr)
        return fa

def plot_attack_FR_cost():
    import matplotlib.pyplot as plt
    # Assume SS and both players are active
    x = np.arange(0,5,0.1)
    y = (0.5*x**1.3 + 0.5*x**1.8) * 11.5
    y = [min(z,100) for z in y]
    y = [max(z,5.75) for z in y]
    plt.plot(x,y)
    plt.xlabel("Fraction of your planets to their planets")
    plt.ylabel("FR Cost")
    plt.grid(True)
    plt.show()



# This is currently only used for units, although its the same math as used for buildings
def unit_cost_multiplier(research_construction, research_tech, required_unit_tech):
    multiplier = 100.0 / (100.0 + research_construction)
    tech_penalty = required_unit_tech - research_tech;
    if tech_penalty > 0:
        penalty = tech_penalty**1.1
        if (penalty) >= 100:
            return None, None # cannot build due to tech being too low
        multiplier *= 1.0 + 0.01*(penalty)
    else:
        penalty = 0
    return multiplier, np.round(penalty,2)



# Return overbuild multiplier, comes from cmdGetBuildOvercost()
def calc_overbuild(planet_size, total_buildings): # include buildings under construction
    if total_buildings <= planet_size:
        return 1
    else:
        return (total_buildings/planet_size)**2

# Return overbuild multiplier given a certain number of buildings being built, the C code did this in an inefficient for loop
def calc_overbuild_multi(planet_size, planet_buildings, new_buildings): # planet_buildings just includes existing and under construction
    ob = min(max(0, planet_size - planet_buildings), new_buildings) # number of slots left on the planet, or N, whichever one is smaller
    new_buildings -= ob # remove it from N to find what's left to build
    ob += (sum_of_squares(new_buildings + max(planet_buildings,planet_size)) - sum_of_squares(max(planet_buildings,planet_size))) / (planet_size**2)
    return ob

# The original C code did a for loop for this calc =)
def sum_of_squares(N):
    return (N * (N + 1) * (2 * N + 1)) / 6

# Used to make a plot of the OB for different planet sizes, to show how larger planets are WAY more valuable
def plot_ob():
    import matplotlib.pyplot as plt
    N = np.arange(3000)
    planet_buildings = 0
    for planet_size in [100,200,300]:
        ob = [calc_overbuild_multi(planet_size, planet_buildings, n) for n in N]
        plt.plot(N,ob)
    plt.grid(True)
    plt.xlabel('Number of Buildings to Build')
    plt.ylabel('Total Cost Multiplier')
    plt.legend(['Planet Size: 100','Planet Size: 200','Planet Size: 300'])
    plt.show()

'''
def unit_costs(research_construction): # cmdGetBuildCosts() in cmd.c
    cost = 100.0 / (100.0 + research_construction)
    type &= 0xFFFF;
    b++;
    if( cmdUnitCost[type][0] < 0 )
    {
      buffer[0] = -2;
      return;
    }
    a = cmdUnitTech[type] - maind->totalresearch[CMD_RESEARCH_TECH];
    buffer[CMD_RESSOURCE_NUMUSED+1] = 0;
    if( a > 0 )
    {
      da = pow( (double)a, 1.1 );
      if( da >= 100.0 )
      {
        buffer[0] = -1;
        return;
      }
      buffer[CMD_RESSOURCE_NUMUSED+1] = (int64_t)da;
      cost *= 1.0 + 0.01*da;
    }
    for( a = 0 ; a < CMD_RESSOURCE_NUMUSED+1 ; a++ )
    {
      buffer[a] = ceil( cost * cmdUnitCost[type][a] );
    }

  }
  return;
'''


def specopEnlightemntCalc(user_id, CMD_ENLIGHT_X):
    return 1

def specopSolarCalc(user_id):
    return 1

# I would move this function into the Portal class in buidings.py, but then we would have to instantiate one every time we wanted to run this calculation...
def battlePortalCalc(x, y, portal_xy_list, research_culture):
    cover = 0
    for portal in portal_xy_list:
        d = np.sqrt((x-portal[0])**2 + (y-portal[1])**2)
        cover += np.max((0, 1.0 - np.sqrt(d/(7.0*(1.0 + 0.01*research_culture)))))
    return cover

def planet_size_distribution():
    # The idea here is to make most the planets small, and a tiny fraction of them WAY bigger,
    # so they are exciting (especially to new people)
    # while still capping the size to 500 for visualization sake
    return int(min(500, 100 + 50*np.random.chisquare(1.25)))


def x_move_calc(speed, x, current_position_x, y, current_position_y):
    dist_x = x - current_position_x
    dist_y = y - current_position_y
    if dist_x == 0:
        return x
    move_x = speed / np.sqrt(1+(dist_y/dist_x)**2)
    print("move_x", move_x)
    if x < current_position_x:
        return current_position_x - move_x
    else:
        return current_position_x + move_x

def y_move_calc(speed, x, current_position_x, y, current_position_y):
    dist_x = x - current_position_x
    dist_y = y - current_position_y
    if dist_y == 0:
        return y
    move_y = speed / np.sqrt(1+(dist_x/dist_y)**2)
    print("move_y",move_y)
    if y < current_position_y:
        return current_position_y - move_y
    else:
        return current_position_y + move_y
