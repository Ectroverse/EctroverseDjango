package org.ectroverse.processtick;
import java.util.*;

public final class Constants {	
	
	//some constants temporarily written here, fetch them from app/constants.py later
	public static final int news_delete_ticks = 288; //teo days in 10min server
    public static final int total_units = 13;
	public static final int population_size_factor  = 200;
	public static final double energy_decay_factor = 0.005;
	public static final double crystal_decay_factor = 0.02;
	public static final int upkeep_solar_collectors = 0;
	public static final int upkeep_fission_reactors = 20;
	public static final int upkeep_mineral_plants = 2;
	public static final int upkeep_crystal_labs = 2;
	public static final int upkeep_refinement_stations = 2;
	public static final int upkeep_cities = 4;
	public static final int upkeep_research_centers = 1;
	public static final int upkeep_defense_sats = 4;
	public static final int upkeep_shield_networks = 16;
	public static final int networth_per_building = 8;
	public static final int building_production_solar = 12;
	public static final int building_production_fission = 40;
	public static final int building_production_mineral = 1;
	public static final int building_production_crystal = 1;
	public static final int building_production_ectrolium = 1;
	public static final int building_production_cities = 10000;
	public static final int building_production_research = 6;
	public static final double [] unit_upkeep = {2.0, 1.6, 3.2, 12.0, 18.0, 0.4, 0.6, 2.8, 0.0, 0.8, 0.8, 2.4, 60.0};
	
	public static final HashMap<String,HashMap<String, Double>> race_info_list = new HashMap<>();
	/* HK = 'HK', _('Harks')
        MT = 'MT', _('Manticarias')
        FH = 'FH', _('Foohons')
        SB = 'SB', _('Spacebornes')
        DW = 'DW', _('Dreamweavers')
        WK = 'WK', _('Wookiees')*/
	public static final HashMap<String, Double> harks = new HashMap<>();
	public static final HashMap<String, Double> manticarias = new HashMap<>();
	public static final HashMap<String, Double> foohons = new HashMap<>();
	public static final HashMap<String, Double> spacebournes = new HashMap<>();
	public static final HashMap<String, Double> dreamweavers = new HashMap<>();
	public static final HashMap<String, Double> wookiees = new HashMap<>();
	public static final HashMap<String, String> buildingsNames = new HashMap<>();
	
	static {
	harks.put("pop_growth", 0.8*0.02);
	harks.put("research_bonus_military",    1.2);
	harks.put("research_bonus_construction", 1.2);
	harks.put("research_bonus_tech",         1.2);
	harks.put("research_bonus_energy",       1.2);
	harks.put("research_bonus_population",   1.2);
	harks.put("research_bonus_culture",      0.6);
	harks.put("research_bonus_operations",   1.2);
	harks.put("research_bonus_portals",      1.2);
	harks.put("energy_production",    0.9);
	harks.put("mineral_production",   1.0);
	harks.put("crystal_production",   1.25);
	harks.put("ectrolium_production",   1.0);
	harks.put("travel_speed",   1.4*2.0);
	
	race_info_list.put("HK",harks);
	
	manticarias.put("pop_growth", 0.9*0.02);
	manticarias.put("research_bonus_military",    0.9);
	manticarias.put("research_bonus_construction", 0.9);
	manticarias.put("research_bonus_tech",         0.9);
	manticarias.put("research_bonus_energy",       0.9);
	manticarias.put("research_bonus_population",   0.9);
	manticarias.put("research_bonus_culture",      1.8);
	manticarias.put("research_bonus_operations",   0.9);
	manticarias.put("research_bonus_portals",      0.9);
	manticarias.put("energy_production",    1.4);
	manticarias.put("mineral_production",   1.0);
	manticarias.put("crystal_production",   1.0);
	manticarias.put("ectrolium_production",   1.0);
	manticarias.put("race_special_solar_15",   1.15);
	manticarias.put("travel_speed",   1.0*2.0);
	
	race_info_list.put("MT",manticarias);
	
	foohons.put("pop_growth", 0.8*0.02);
	foohons.put("research_bonus_military",    1.5);
	foohons.put("research_bonus_construction", 1.5);
	foohons.put("research_bonus_tech",         1.5);
	foohons.put("research_bonus_energy",       1.5);
	foohons.put("research_bonus_population",   1.5);
	foohons.put("research_bonus_culture",      1.5);
	foohons.put("research_bonus_operations",   1.5);
	foohons.put("research_bonus_portals",      1.5);
	foohons.put("energy_production",    0.8);
	foohons.put("mineral_production",   1.0);
	foohons.put("crystal_production",   1.0);
	foohons.put("ectrolium_production",   1.2);
	foohons.put("travel_speed",   1.0*2.0);
	
	race_info_list.put("FH",foohons);

	spacebournes.put("pop_growth", 1.2*0.02);
	spacebournes.put("research_bonus_military",    1.1);
	spacebournes.put("research_bonus_construction", 1.1);
	spacebournes.put("research_bonus_tech",         0.6);
	spacebournes.put("research_bonus_energy",       1.1);
	spacebournes.put("research_bonus_population",   1.1);
	spacebournes.put("research_bonus_culture",      1.1);
	spacebournes.put("research_bonus_operations",   1.1);
	spacebournes.put("research_bonus_portals",      1.1);
	spacebournes.put("energy_production",    1.3);
	spacebournes.put("mineral_production",   1.0);
	spacebournes.put("crystal_production",   1.0);
	spacebournes.put("ectrolium_production",   1.0);
	spacebournes.put("travel_speed",   1.8*2.0);
	
	race_info_list.put("SB",spacebournes);

	dreamweavers.put("pop_growth", 1.1*0.02);
	dreamweavers.put("research_bonus_military",    1.4);
	dreamweavers.put("research_bonus_construction", 1.4);
	dreamweavers.put("research_bonus_tech",         2.8);
	dreamweavers.put("research_bonus_energy",       1.4);
	dreamweavers.put("research_bonus_population",   1.4);
	dreamweavers.put("research_bonus_culture",      1.4);
	dreamweavers.put("research_bonus_operations",   1.4);
	dreamweavers.put("research_bonus_portals",      1.4);
	dreamweavers.put("energy_production",    0.8);
	dreamweavers.put("mineral_production",   1.0);
	dreamweavers.put("crystal_production",   1.0);
	dreamweavers.put("ectrolium_production",   1.0);
	dreamweavers.put("travel_speed",   1.0*2.0);
	
	race_info_list.put("DW",dreamweavers);
	
	wookiees.put("pop_growth", 1.2*0.02);
	wookiees.put("research_bonus_military",    1.0);
	wookiees.put("research_bonus_construction", 2.0);
	wookiees.put("research_bonus_tech",         1.0);
	wookiees.put("research_bonus_energy",       1.0);
	wookiees.put("research_bonus_population",   2.0);
	wookiees.put("research_bonus_culture",      1.0);
	wookiees.put("research_bonus_operations",   1.0);
	wookiees.put("research_bonus_portals",      2.0);
	wookiees.put("energy_production",    0.7);
	wookiees.put("mineral_production",   1.25);
	wookiees.put("crystal_production",   1.25);
	wookiees.put("ectrolium_production",   1.0);
	wookiees.put("race_special_resource_public static final interest",   1.005);
	wookiees.put("travel_speed",   1.6*2.0);
	
	race_info_list.put("WK",wookiees);
	
	buildingsNames.put( "SC", "solar_collectors");
	buildingsNames.put( "FR", "fission_reactors");
	buildingsNames.put( "MP", "mineral_plants");
	buildingsNames.put( "CL", "crystal_labs");
	buildingsNames.put( "RS", "refinement_stations");
	buildingsNames.put( "CT", "cities");
	buildingsNames.put( "RC", "research_centers");
	buildingsNames.put( "DS", "defense_sats");
	buildingsNames.put( "SN", "shield_networks");
	buildingsNames.put( "PL", "portal");
	}
	
	public static final String [][] researchNames = {
		{"research_points_military", "research_bonus_military", "alloc_research_military", "research_max_military", "research_percent_military"},
		{"research_points_construction", "research_bonus_construction", "alloc_research_construction", "research_max_construction", "research_percent_construction"},
		{"research_points_tech", "research_bonus_tech", "alloc_research_tech", "research_max_tech", "research_percent_tech"},
		{"research_points_energy", "research_bonus_energy", "alloc_research_energy", "research_max_energy", "research_percent_energy"},
		{"research_points_population", "research_bonus_population", "alloc_research_population", "research_max_population", "research_percent_population" },
		{"research_points_culture", "research_bonus_culture", "alloc_research_culture", "research_max_culture", "research_percent_culture"},
		{"research_points_operations", "research_bonus_operations", "alloc_research_operations", "research_max_operations", "research_percent_operations"},
		{"research_points_portals", "research_bonus_portals", "alloc_research_portals", "research_max_portals", "research_percent_portals"},
		};
	
	public static final double [] units_upkeep_costs = {2.0, 1.6, 3.2, 12.0, 18.0, 0.4, 0.6, 2.8, 0.0, 0.8, 0.8, 2.4, 60.0};
	
	public static final double [] units_nw = {4,3,5,12,14,1,1,4,7,2,2,6,30};
	
	public static final String [] unit_names = {"bomber", "fighter", "transport", "cruiser", "carrier", "soldier", "droid", "goliath", "phantom", "wizard", "agent", "ghost", "exploration"};
	public static final String [] unit_labels = {"Bombers","Fighters","Transports","Cruisers","Carriers","Soldiers","Droids","Goliaths","Phantoms","Psychics","Agents","Ghost Ships","Exploration Ships"};

}