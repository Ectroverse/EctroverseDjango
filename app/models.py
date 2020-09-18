from django.db import models
from django.contrib.auth.models import User # from Django's built-in user management system
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _ # for the enumeration's labels
from .constants import *
from django.db.models.signals import post_save # used to auto create UserStatus and fleet after a new user is created

# Is there any reason to have a model for solar system?  That would then contain N planet objects

class Planet(models.Model):
    # Static
    x = models.IntegerField()
    y = models.IntegerField()
    i = models.IntegerField() # index of planet in system, starting at 0
    # note that each user's status contains their home planet as a child object, the field below is more for quick checks
    home_planet = models.BooleanField(default=False) # players start with their home planet and it cannot be attacked
    pos_in_system = models.IntegerField(default=0) # used to spread out the planets around the circle better
    size = models.IntegerField()

    owner = models.ForeignKey(User, null=True, blank=True, default=None, on_delete=models.SET_NULL) # if owner is removed from game set back to null

    # Calculated each tick
    current_population = models.IntegerField(default=0) # calculated each tick
    max_population = models.IntegerField(default=0) # calculated each tick
    protection = models.IntegerField(default=0) # in % points, the calculation will round it
    overbuilt = models.FloatField(default=0.0) # DecimalField was being weird with its rounding
    overbuilt_percent = models.FloatField(default=0.0)

    # Bonuses
    bonus_solar = models.IntegerField(default=0) # in % points, e.g. 104 for 104% bonus.  Note that the solar energy bonus does NOT apply to fission reactors
    bonus_mineral = models.IntegerField(default=0)
    bonus_crystal = models.IntegerField(default=0)
    bonus_ectrolium = models.IntegerField(default=0)
    bonus_fission = models.IntegerField(default=0)

    # Buildings (I decided to break them out into separate fields instead of having an array, to make the code easier to read in the various spots these buildings will be involved in calculaitons and such
    solar_collectors = models.IntegerField(default=0)
    fission_reactors = models.IntegerField(default=0)
    mineral_plants = models.IntegerField(default=0)
    crystal_labs = models.IntegerField(default=0)
    refinement_stations = models.IntegerField(default=0)
    cities = models.IntegerField(default=0)
    research_centers = models.IntegerField(default=0)
    defense_sats = models.IntegerField(default=0)
    shield_networks = models.IntegerField(default=0)
    portal = models.BooleanField(default=False)
    portal_under_construction = models.BooleanField(default=False)
    total_buildings = models.IntegerField(default=0) # on this planet. doesn't include under construction
    buildings_under_construction = models.IntegerField(default=0) # number of total buildings under construction. NOTE- the C code doesnt have a field for this, it jsut calculates it each time, since it uses a single array for the buildings



class Empire(models.Model):
    '''
  int id;
  int rank;
  int flags;
  int numplayers;
  int politics[CMD_EMPIRE_POLITICS_TOTAL];
  int player[ARRAY_MAX];
  int vote[ARRAY_MAX];
  int depreciated;
  int homeid;
  int homepos; // ( y << 16 ) + x
  int picture;
  int planets;
  int artefacts;
  int construction;
  int building[CMD_BLDG_EMPIRE_NUMUSED];
  int counters[16];
  float taxation;
  int64_t networth;
  int64_t fund[CMD_RESSOURCE_NUMUSED];
  int64_t infos[CMD_RESSOURCE_NUMUSED];
  char name[USER_NAME_MAX];
  char password[USER_PASS_MAX];
    '''
    number = models.IntegerField(default=0)
    x = models.IntegerField(default=0)
    y = models.IntegerField(default=0)
    rank = models.IntegerField(default=0)
    numplayers = models.IntegerField(default=0)
    planets = models.IntegerField(default=0)
    artefacts = models.IntegerField(default=0) #do we need this?
    taxation = models.FloatField(default=0.0)
    networth = models.BigIntegerField(default=0)
    name = models.CharField(max_length=30, default="")
    name_with_id = models.CharField(max_length=35, default="")
    password = models.CharField(max_length=30, default="", blank=True)
    fund_energy = models.IntegerField(default=0)
    fund_minerals = models.IntegerField(default=0)
    fund_crystals = models.IntegerField(default=0)
    fund_ectrolium = models.IntegerField(default=0)
    pm_message = models.CharField(max_length=300, default="")
    relations_message = models.CharField(max_length=300, default="No relations message.")
    empire_image = models.ImageField(upload_to='empire_images/', blank=True)


class UserStatus(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE) # when referenced object is deleted, also delete this

    # Info that doesn't change over the round
    user_name = models.CharField(max_length=30, default="user-display-name") # Display name
    # empire_num = models.IntegerField()
    empire = models.ForeignKey(Empire, on_delete=models.SET_NULL, blank=True, null=True, default=None)
    home_planet = models.ForeignKey(Planet, on_delete=models.SET_NULL, blank=True,
                                    null=True)  # only time we delete planets will be mid-round

    # empire politics section
    class EmpireRoles(models.TextChoices):
        PM = 'PM', _('Prime Minister')
        VM = 'VM', _('Vice Minister')
        P = 'P', _('') #normal player
        I = 'I', _('Independent')
    empire_role = models.CharField(max_length=2, choices=EmpireRoles.choices, default=EmpireRoles.P)
    votes =  models.IntegerField(default=0) #number of people voting for this user to be a leader of their empire
    voting_for =  models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True, default=None)


    # Race
    class Races(models.TextChoices):
        HK = 'HK', _('Harks')
        MT = 'MT', _('Manticarias')
        FH = 'FH', _('Foohons')
        SB = 'SB', _('Spacebornes')
        DW = 'DW', _('Dreamweavers')
        WK = 'WK', _('Wookiees')
    race = models.CharField(max_length=2, choices=Races.choices)

    # Resources
    energy = models.BigIntegerField(default=0, validators = [MinValueValidator(0)])
    minerals = models.BigIntegerField(default=0, validators = [MinValueValidator(0)])
    crystals = models.BigIntegerField(default=0, validators = [MinValueValidator(0)])
    ectrolium = models.BigIntegerField(default=0, validators = [MinValueValidator(0)])

    # Current resource production/decay, calculated in process_tick
    energy_production = models.IntegerField(default=0)
    energy_decay = models.IntegerField(default=0)
    energy_interest = models.IntegerField(default=0) # wookies only
    energy_income = models.IntegerField(default=0)
    mineral_production = models.IntegerField(default=0)
    mineral_interest = models.IntegerField(default=0) # wookies only
    mineral_income = models.IntegerField(default=0)
    crystal_production = models.IntegerField(default=0)
    crystal_decay = models.IntegerField(default=0)
    crystal_interest = models.IntegerField(default=0) # wookies only
    crystal_income = models.IntegerField(default=0)
    ectrolium_production = models.IntegerField(default=0)
    ectrolium_interest = models.IntegerField(default=0) # wookies only
    ectrolium_income = models.IntegerField(default=0)

    # Misc info that must be recalculated
    num_planets = models.IntegerField(default=0) # number of planets, will get calculated
    population = models.IntegerField(default=0)
    networth = models.BigIntegerField(default=1)
    buildings_upkeep = models.IntegerField(default=0) # stored as a positive number
    units_upkeep = models.IntegerField(default=0) # stored as a positive number
    portals_upkeep = models.IntegerField(default=0) # stored as a positive number
    population_upkeep_reduction = models.IntegerField(default=0)

    total_solar_collectors = models.IntegerField(default=0) # all of these are across all planets (which is why its in status and not planet)
    total_fission_reactors = models.IntegerField(default=0)
    total_mineral_plants = models.IntegerField(default=0)
    total_crystal_labs = models.IntegerField(default=0)
    total_refinement_stations = models.IntegerField(default=0)
    total_cities = models.IntegerField(default=0)
    total_research_centers = models.IntegerField(default=0)
    total_defense_sats = models.IntegerField(default=0)
    total_shield_networks = models.IntegerField(default=0)
    total_portals = models.IntegerField(default=1)
    total_buildings = models.IntegerField(default=1)

    # Readiness
    fleet_readiness = models.IntegerField(default=0)
    psychic_readiness = models.IntegerField(default=0)
    agent_readiness = models.IntegerField(default=0)

    # Research (names might seem verbose but it makes various spots in the code way less confusing to read)
    research_percent_military = models.IntegerField(default=0) # stored as integer, in percentage points
    research_percent_construction = models.IntegerField(default=0)
    research_percent_tech = models.IntegerField(default=0)
    research_percent_energy = models.IntegerField(default=0)
    research_percent_population = models.IntegerField(default=0)
    research_percent_culture = models.IntegerField(default=0)
    research_percent_operations = models.IntegerField(default=0)
    research_percent_portals = models.IntegerField(default=0)

    research_points_military = models.BigIntegerField(default=0)
    research_points_construction = models.BigIntegerField(default=0)
    research_points_tech = models.BigIntegerField(default=0)
    research_points_energy = models.BigIntegerField(default=0)
    research_points_population = models.BigIntegerField(default=0)
    research_points_culture = models.BigIntegerField(default=0)
    research_points_operations = models.BigIntegerField(default=0)
    research_points_portals = models.BigIntegerField(default=0)

    alloc_research_military = models.IntegerField(default=16) # stored as integer, in percentage points
    alloc_research_construction = models.IntegerField(default=12)
    alloc_research_tech = models.IntegerField(default=12)
    alloc_research_energy = models.IntegerField(default=12)
    alloc_research_population = models.IntegerField(default=12)
    alloc_research_culture = models.IntegerField(default=12)
    alloc_research_operations = models.IntegerField(default=12)
    alloc_research_portals = models.IntegerField(default=12)

    current_research_funding = models.BigIntegerField(default=0)

    # Fleet related
    long_range_attack_percent = models.IntegerField(default=200)
    air_vs_air_percent = models.IntegerField(default=200)
    ground_vs_air_percent = models.IntegerField(default=200)
    ground_vs_ground_percent = models.IntegerField(default=200)
    class PostAttackOrder(models.IntegerChoices):
        STATION_ON_PLANET = 0
        WAIT_IN_SYSTEM    = 1
        RECALL_TO_MAIN    = 2
    post_attack_order = models.IntegerField(choices=PostAttackOrder.choices, default=2)


# When a new User is created, automatically create an associated UserStatus and main fleet
def new_user_post_save(sender, instance, created, **kwargs):
    if created:
        UserStatus.objects.create(user=instance)
        Fleet.objects.create(owner=instance, main_fleet=True) # this is the only time a main fleet is created
        # TODO assign home planet here, based on some index stored the number of current players in the round
post_save.connect(new_user_post_save, sender=User)


class Construction(models.Model): # a single type of building under construction
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    planet = models.ForeignKey(Planet, on_delete=models.CASCADE)
    n = models.IntegerField() # number of them
    ticks_remaining = models.IntegerField()

    # Building type enumeration
    class BuildingTypes(models.TextChoices): # must match the short_label in buildings class
        SC = 'SC', _('Solar Collectors')
        FR = 'FR', _('Fission Reactors')
        MP = 'MP', _('Mineral Plants')
        CL = 'CL', _('Crystal Laboratories')
        RS = 'RS', _('Refinement Stations')
        CT = 'CT', _('Cities')
        RC = 'RC', _('Research Centers')
        DS = 'DS', _('Defense Satellites')
        SN = 'SN', _('Shield Networks')
        PL = 'PL', _('Portal')
    building_type = models.CharField(max_length=2, choices=BuildingTypes.choices)


class Fleet(models.Model):
    owner = models.ForeignKey(User, null=True, blank=True, default=None, on_delete=models.SET_NULL) # if owner is removed from game set back to null
    main_fleet = models.BooleanField(default=False) # should only be 1 per user, assigned only at user creation
    on_planet = models.ForeignKey(Planet, null=True, blank=True, default=None, on_delete=models.SET_NULL) # planet object if stationed, or None
    ticks_remaining = models.IntegerField(default=0) # for traveling

    # Order (if fleet is being sent somewhere)
    class CommandOrder(models.IntegerChoices):
        ATTACK_PLANET     = 0
        STATION_ON_PLANET = 1
        MOVE_TO_SYSTEM    = 2
    command_order = models.IntegerField(choices=CommandOrder.choices, default=0)

    # Destination coords for when its traveling
    x = models.IntegerField(null=True, blank=True, default=None)
    y = models.IntegerField(null=True, blank=True, default=None)

    # Number of each type of unit
    bomber      = models.IntegerField(default=0, verbose_name="Bombers")
    fighter     = models.IntegerField(default=0, verbose_name="Fighters")
    transport   = models.IntegerField(default=0, verbose_name="Transports")
    cruiser     = models.IntegerField(default=0, verbose_name="Cruisers")
    carrier     = models.IntegerField(default=0, verbose_name="Carriers")
    soldier     = models.IntegerField(default=0, verbose_name="Soldiers")
    droid       = models.IntegerField(default=0, verbose_name="Droids")
    goliath     = models.IntegerField(default=0, verbose_name="Goliaths")
    phantom     = models.IntegerField(default=0, verbose_name="Phantoms")
    wizard      = models.IntegerField(default=0, verbose_name="Psychics")
    agent       = models.IntegerField(default=0, verbose_name="Agents")
    ghost       = models.IntegerField(default=0, verbose_name="Ghost Ships")
    exploration = models.IntegerField(default=0, verbose_name="Exploration Ships")



class UnitConstruction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    n = models.IntegerField() # number of them
    ticks_remaining = models.IntegerField()
    unit_type = models.CharField(max_length=11) # exploration is longest name, so 11 chars is enough



class RoundStatus(models.Model):
    galaxy_size = models.IntegerField(default=100)
    tick_number = models.IntegerField(default=0)


class Relations(models.Model):
    # When an empire declares a relation, its id number goes to the empire1 field, and the 
    # other empire's id goes to empire2 field
    empire1 = models.ForeignKey(Empire, related_name='empire1', on_delete=models.SET_NULL, blank=True, null=True, default=None)
    empire2 = models.ForeignKey(Empire, related_name='empire2', on_delete=models.SET_NULL, blank=True, null=True, default=None)
    class RelationTypes(models.TextChoices): 
        AO = 'AO', _('Alliance offered')
        W = 'W', _('War declared')
        A = 'A', _('Alliance')
        NO = 'NO', _('Non agression pact offered')
        NC = 'NC', _('Non agression pact cancelled')
        PC = 'PC', _('Permanent non agression pact cancelled')
        N = 'N', _('Non agression pact') 
    relation_type = models.CharField(max_length=2, choices=RelationTypes.choices)
    relation_length = models.IntegerField(blank=True, null=True, default=None)
    relation_creation_tick = models.IntegerField(default=0)
    relation_cancel_tick = models.IntegerField(default=0)
    relation_remaining_time = models.IntegerField(default=0)




