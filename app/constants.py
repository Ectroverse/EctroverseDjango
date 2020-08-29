####################
# Resource Related #
####################

resource_names = ["Energy",
                  "Mineral",
                  "Crystal",
                  "Ectrolium",
                  "Time",
                  "Population"]

energy_decay_factor = 0.005
crystal_decay_factor = 0.02




####################
# Building Related #
####################

# One option I could do is switch from using a list to using a dict, like building_names.solar or something, which might make the code a little more readable

#            energy, mineral, crystal, endurium, time
building_costs = [[120, 10,  0,  1,  4],
                  [450, 20, 12,  8, 14],
                  [200,  0,  0,  2,  8],
                  [350,  8,  0, 12,  6],
                  [400, 36,  4,  0, 12],
                  [300, 30,  0,  2, 10],
                  [100,  5,  5,  5,  8],
                  [400, 35, 20, 40, 16],
                  [2000, 10, 60, 30, 24],
                  [8000, 200, 500, 400, 128]] # portal

required_building_tech = [0, 100, 0, 0, 0, 0, 0, 110, 140, 0]

upkeep_solar_collectors = 0.0
upkeep_fission_reactors = 20.0
upkeep_mineral_plants = 2.0
upkeep_crystal_labs = 2.0
upkeep_refinement_stations = 2.0
upkeep_cities = 4.0
upkeep_research_centers = 1.0
upkeep_defense_sats = 4.0
upkeep_shield_networks = 16.0

networth_per_building = 8 # can always break it out into separate buildings later, but it was all 8's in the current C code

building_production_solar = 12
building_production_fission = 40
building_production_mineral = 1
building_production_crystal = 1
building_production_ectrolium = 1
building_production_cities = 1000
building_production_research = 6

population_size_factor = 20

################
# Unit Related #
################

#           energy, mineral, crystal, endurium, time
unit_costs = [[250,  15,  0,  5,  6], # bombers
              [150,  10,  0,  3,  5], # fighters
              [600,  35, 10, 10,  8], # transports
              [1600, 90,  0, 45, 12], # cruisers
              [2000,160, 15, 20, 12], # carriers
              [100,   0,  0,  1,  3], # soldiers
              [50,    5,  0,  1,  2], # droids
              [350,  20,  8, 10,  4], # goliaths
              [ -1,  -1, -1, -1, -1], # phantoms
              [150,   0, 10,  0,  5], # psychics
              [150,   0,  0, 10,  5], # agents
              [200,   8, 60,  5,  7], # ghost ships
              [5000, 50,  0, 50,  4]] # explors

required_unit_tech = [60, 0, 0, 40, 20, 0, 80, 120, 0,   0, 0, 160, 0]

unit_upkeep = [2.0, 1.6, 3.2, 12.0, 18.0, 0.4, 0.6, 2.8, 0.0, 0.8, 0.8, 2.4, 60.0]

#             not sure these correspond to phase of battle, speed, networth
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

unit_labels = ["Bombers","Fighters","Transports","Cruisers","Carriers","Soldiers","Droids","Goliaths","Phantoms","Psychics","Agents","Ghost Ships","Exploration Ships"]

# Build dictionary that will store all our unit info
unit_info = {}
# Order of this list much match the data above. Might as well store the order in the dict for reference in views
unit_info["unit_list"] = ['bomber','fighter','transport','cruiser','carrier','soldier','droid','goliath','phantom','wizard','agent','ghost','exploration']
for i, unit in enumerate(unit_info["unit_list"]):
    unit_info[unit] = {}
    unit_info[unit]['cost'] = unit_costs[i]
    unit_info[unit]['required_tech'] = required_unit_tech[i]
    unit_info[unit]['upkeep'] = unit_upkeep[i]
    unit_info[unit]['stats'] = unit_stats[i]
    unit_info[unit]['label'] = unit_labels[i]
    unit_info[unit]['i'] = i

##########################################
# Global game settings from evconfig.ini #
##########################################

stockpile = 0
settings_num_value = 1 # still not sure what this is


###################
# Race Attributes #
###################

race_info_list = {
"Harks": {
    "pop_growth": 0.8*0.02,
    "military_attack": 1.4,
    "military_defence": 0.9,
    "travel_speed": 1.4*2.0,
    "research_bonus_military":     1.2,
    "research_bonus_construction": 1.2,
    "research_bonus_tech":         1.2,
    "research_bonus_energy":       1.2,
    "research_bonus_population":   1.2,
    "research_bonus_culture":      0.6,
    "research_bonus_operations":   1.2,
    "research_max_military": 250,   # defaults to 200
    "fighters_coeff":   1.2,        # defaults to 1.0
    "energy_production":    0.9, # defaults to 1.0
    "crystal_production":   1.25,
    "race_special": None, # TODO paste list somewhere of possible specials
    "op_list": ["Network Virus", "Infiltration", "Bio Infection", "Military Sabotage", "Nuke Planet", "Diplomatic Espionage"],
    "spell_list": ["Irradiate Ectrolium", "Incandescence", "Black Mist", "War Illusions"],
    "incantation_list": ["Portal Force Field", "Vortex Portal", "Energy Surge", "Call to Arms"]},
"Manticarias": {
    "pop_growth": 0.9*0.02,
    "military_attack": 0.7,
    "military_defence": 1.1,
    "travel_speed": 1.0*2.0,
    "research_bonus_military":     0.9,
    "research_bonus_construction": 0.9,
    "research_bonus_tech":         0.9,
    "research_bonus_energy":       0.9,
    "research_bonus_population":   0.9,
    "research_bonus_culture":      1.8,
    "research_bonus_operations":   0.9,
    "psychics_coeff": 1.4,
    "ghost_ships_coeff": 1.2,
    "energy_production": 1.4,
    "race_special": 'RACE_SPECIAL_SOLARP15',
    "op_list": ["Spy Target", "Observe Planet", "Energy Transfer", "Steal Resources"],
    "spell_list": ["Dark Web", "Black Mist", "War Illusions", "Psychic Assault", "Phantoms", "Enlightenment", "Grow Planet's Size"],
    "incantation_list": ["Planetary Shielding", "Mind Control"]},
"Foohons": {
    "pop_growth": 0.8*0.02,
    "military_attack": 1.2,
    "military_defence": 1.1,
    "travel_speed": 1.0*2.0,
    "research_bonus_military":     1.5,
    "research_bonus_construction": 1.5,
    "research_bonus_tech":         1.5,
    "research_bonus_energy":       1.5,
    "research_bonus_population":   1.5,
    "research_bonus_culture":      1.5,
    "research_bonus_operations":   1.5,
    "ghost_ships_coeff": 1.1,
    "energy_production": 0.8,
    "ectrolium_production": 1.2,
    "race_special": 'RACE_SPECIAL_POPRESEARCH',
    "op_list": ["Spy Target", "Observe Planet", "Infiltration", "Military Sabotage", "High Infiltration", "Planetary Beacon"],
    "spell_list": ["Irradiate Ectrolium", "Dark Web", "Incandescence", "Psychic Assault", "Enlightenment"],
    "incantation_list": ["Sense Artefact", "Survey System", "Vortex Portal", "Mind Control"]},
"Spacebornes": {
    "pop_growth": 1.2*0.02,
    "military_attack": 1.0,
    "military_defence": 1.2,
    "travel_speed": 1.8*2.0,
    "research_bonus_military":     1.1,
    "research_bonus_construction": 1.1,
    "research_bonus_tech":         0.6,
    "research_bonus_energy":       1.1,
    "research_bonus_population":   1.1,
    "research_bonus_culture":      1.1,
    "research_bonus_operations":   1.1,
    "research_max_energy": 250,
    "soldiers_coeff": 1.1,
    "droids_coeff": 1.1,
    "psychics_coeff": 0.7,
    "agents_coeff": 1.3,
    "energy_production": 1.3,
    "race_special": None,
    "op_list": ["Spy Target", "Observe Planet", "Network Virus", "Bio Infection", "Energy Transfer", "Nuke Planet", "Planetary Beacon", "Diplomatic Espionage", "Steal Resources"],
    "spell_list": ["Irradiate Ectrolium", "Incandescence", "Black Mist"],
    "incantation_list": ["Survey System", "Planetary Shielding"]},
"Dreamweavers": {
    "pop_growth": 1.1*0.02,
    "military_attack": 1.0,
    "military_defence": 0.7,
    "travel_speed": 1.0*2.0,
    "research_bonus_military":     1.4,
    "research_bonus_construction": 1.4,
    "research_bonus_tech":         2.8,
    "research_bonus_energy":       1.4,
    "research_bonus_population":   1.4,
    "research_bonus_culture":      1.4,
    "research_bonus_operations":   1.4,
    "research_max_military": 100,
    "research_max_construction": 250,
    "psychics_coeff": 1.5,
    "ghost_ships_coeff": 1.3,
    "energy_production": 0.8,
    "race_special": None,
    "op_list": ["Network Virus", "Bio Infection", "Energy Transfer", "Military Sabotage"],
    "spell_list": ["Irradiate Ectrolium", "Dark Web", "Incandescence", "Black Mist", "War Illusions", "Psychic Assault", "Phantoms", "Enlightenment", "Grow Planet's Size"],
    "incantation_list": ["Sense Artefact", "Portal Force Field", "Mind Control", "Energy Surge"]},
"Wookiees": {
    "pop_growth": 1.2*0.02,
    "military_attack": 0.9,
    "military_defence": 1.3,
    "travel_speed": 1.6*2.0,
    "research_bonus_military":     1.0,
    "research_bonus_construction": 2.0,
    "research_bonus_tech":         1.0,
    "research_bonus_energy":       1.0,
    "research_bonus_population":   2.0,
    "research_bonus_culture":      1.0,
    "research_bonus_operations":   1.0,
    "research_max_population": 250,
    "cruiser_coeff": 1.15,
    "ghost_ships_coeff": 1.15,
    "energy_production": 0.7,
    "mineral_production": 1.25,
    "crystal_production": 1.25,
    "race_special": 'RACE_SPECIAL_WOOKIEE',
    "op_list": ["Infiltration", "Nuke Planet", "Planetary Beacon", "Diplomatic Espionage", "Steal Resources"],
    "spell_list": ["Irradiate Ectrolium", "Incandescence", "War Illusions", "Grow Planet's Size"],
    "incantation_list": ["Sense Artefact", "Survey System", "Portal Force Field", "Call to Arms"]}}


