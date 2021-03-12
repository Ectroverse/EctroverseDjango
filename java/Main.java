import java.sql.*;
import java.util.*;

public class Main
{
	
	class Planet{
		int posX;
		int posY;
		int posZ;
		
		public Planet(int x, int y, int z){
			this.posX = x;
			this.posY = y;
			this.posZ = z;
		}
	}


    public static void main(String[] args) {
	//some constants temporarily written here, fetch them from app/constants.py later
	int population_size_factor  = 20;
	double energy_decay_factor = 0.005;
	double crystal_decay_factor = 0.02;
	int upkeep_solar_collectors = 0;
	int upkeep_fission_reactors = 20;
	int upkeep_mineral_plants = 2;
	int upkeep_crystal_labs = 2;
	int upkeep_refinement_stations = 2;
	int upkeep_cities = 4;
	int upkeep_research_centers = 1;
	int upkeep_defense_sats = 4;
	int upkeep_shield_networks = 16;
	int networth_per_building = 8;
	int building_production_solar = 12;
	int building_production_fission = 40;
	int building_production_mineral = 1;
	int building_production_crystal = 1;
	int building_production_ectrolium = 1;
	int building_production_cities = 1000;
	int building_production_research = 6;
	double [] unit_upkeep = {2.0, 1.6, 3.2, 12.0, 18.0, 0.4, 0.6, 2.8, 0.0, 0.8, 0.8, 2.4, 60.0};
	HashMap<String,HashMap<String, Double>> race_info_list = new HashMap<>();
	/* HK = 'HK', _('Harks')
        MT = 'MT', _('Manticarias')
        FH = 'FH', _('Foohons')
        SB = 'SB', _('Spacebornes')
        DW = 'DW', _('Dreamweavers')
        WK = 'WK', _('Wookiees')*/
	HashMap<String, Double> harks = new HashMap<>();
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
	race_info_list.put("HK",harks);
	HashMap<String, Double> manticarias = new HashMap<>();
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
	race_info_list.put("MT",manticarias);
	HashMap<String, Double> foohons = new HashMap<>();
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
	race_info_list.put("FH",foohons);
	HashMap<String, Double> spacebournes = new HashMap<>();
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
	race_info_list.put("SB",spacebournes);
	HashMap<String, Double> dreamweavers = new HashMap<>();
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
	race_info_list.put("DW",dreamweavers);
	HashMap<String, Double> wookiees = new HashMap<>();
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
	race_info_list.put("WK",wookiees);
	    
	HashMap<String, String> buildingsNames = new HashMap<>();
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
	
	String [][] researchNames = {
		{"research_points_military", "research_bonus_military", "alloc_research_military", "research_max_military", "research_percent_military "},
		{"research_points_construction", "research_bonus_construction", "alloc_research_construction", "research_max_construction", "research_percent_construction"},
		{"research_points_tech ", "research_bonus_tech ", "alloc_research_tech ", "research_max_tech", "research_percent_tech"},
		{"research_points_energy", "research_bonus_energy", "alloc_research_energy", "research_max_energy", "research_percent_energy"},
		{"research_points_population", "research_bonus_population", "alloc_research_population", "research_max_population", "research_percent_population" },
		{"research_points_culture", "research_bonus_culture", "alloc_research_culture", "research_max_culture", "research_percent_culture"},
		{"research_points_operations", "research_bonus_operations", "alloc_research_operations", "research_max_operations", "research_percent_operations"},
		{"research_points_portals", "research_bonus_portals", "alloc_research_portals", "research_max_portals", "research_percent_portals"},
	};
	

	long startTime = System.nanoTime();
	long connectionTime = 0;
	long statTime = 0;
	long resultTime = 0;
	long executeBatchTime = 0;
	long jobsUpdate1 = 0;
	long jobsUpdate2 = 0;
	long planetsUpdate1 = 0;
	long planetsUpdate2 = 0;
	long userUpdate1 = 0;
	long userUpdate2 = 0;
	
	
    try {
	 	//long startTime = System.nanoTime();
		Connection con = DriverManager.getConnection("jdbc:postgresql://ectroversedjango_db_1:5432/djangodatabase", "dbadmin", "pass");
		connectionTime = System.nanoTime();
		Statement statement = con.createStatement();
		
		//update construction jobs	
		
		jobsUpdate1 = System.nanoTime();
		HashMap<Integer, HashMap<String, Integer>> jobs = execute_jobs(con);
		jobsUpdate2 = System.nanoTime();
		//update units jobs
		 
		//update fleets
		 
		ResultSet resultSet = statement.executeQuery("SELECT * FROM app_userstatus");
	   	ResultSetMetaData rsmd = resultSet.getMetaData();
	   	ArrayList<String []> columns = new ArrayList<>(rsmd.getColumnCount());
		 
		 //put user table into list with hash maps, as we cannot use nested resultSet
	  	for(int i = 1; i <= rsmd.getColumnCount(); i++){
			String [] arr = new String[2];
			arr[0] = rsmd.getColumnName(i);
			arr[1] = rsmd.getColumnClassName(i);
			//System.out.println(Arrays.toString(arr));
			columns.add(arr);
		 }
		 
		 //System.out.println(columns);
		 ArrayList<HashMap<String, Integer>> usersInt = new ArrayList<>();
		 ArrayList<HashMap<String, Long>> usersLong = new ArrayList<>();
		 HashMap<Integer, String> usersRace = new HashMap<>();

		 String planetStatusUpdateQuery = "UPDATE \"PLANET\"  SET" +
			" current_population = ? ,"+ //1
			" max_population = ? ," + //2
			" protection = ? ," + //3
			" overbuilt = ? ," + //4
			" overbuilt_percent = ? ," + //5
			" solar_collectors = ? ," + //6
			" fission_reactors = ? ," + //7
			" mineral_plants = ? ," + //8
			" crystal_labs = ? ," + //9
			" refinement_stations = ? , " + //10
			" cities = ? ," + //11
			" research_centers = ? ," + //12
			" defense_sats = ? ," + //13
			" shield_networks = ? ," + //14
			" portal = ? ," + //15
			" portal_under_construction = ? ," + //16
			" total_buildings = ? ," + //17
			" buildings_under_construction = ? ," + //18
			 
		 	"WHERE id = ?" ; //19
		 PreparedStatement planetsUpdateStatement = con.prepareStatement(planetStatusUpdateQuery); //mass update, much faster

		 String userStatusUpdateQuery = "UPDATE app_userstatus SET "+
			" fleet_readiness  = ? ," +  //1
			" psychic_readiness  = ? ," + //2
			" agent_readiness  = ? ," + //3
			" population   = ? ," + //4
			" total_solar_collectors  = ? ," + //5
			" total_fission_reactors  = ? ," + //6
			" total_mineral_plants  = ? ," + //7
			" total_crystal_labs  = ? ," + //8
			" total_refinement_stations   = ? ," + //9
			" total_cities  = ? ," + //10
			" total_research_centers   = ? ," + //11
			" total_defense_sats    = ? ," + //12
			" total_shield_networks   = ? ," + //13
			" total_portals  = ? ," + //14
			" research_points_military   = ? ," + //15
			" research_points_construction   = ? ," + //16
			" research_points_tech   = ? ," + //17
			" research_points_energy    = ? ," + //18
			" research_points_population   = ? ," + //19
			" research_points_culture    = ? ," + //20
			" research_points_operations   = ? ," + //21
			" research_points_portals    = ? ," + //22
			" current_research_funding    = ? ," + //23
			" research_percent_military   = ? ," + //24
			" research_percent_construction    = ? ," + //25
			" research_percent_tech            = ? ," + //26
			" research_percent_energy          = ? ," + //27
			" research_percent_population      = ? ," + //28
			" research_percent_culture         = ? ," + //29
			" research_percent_operations      = ? ," + //30
			" research_percent_portals         = ? ," + //31
			" energy_production          = ? ," + //32
			" energy_decay          = ? ," + //33
			" buildings_upkeep          = ? ," + //34
			" units_upkeep          = ? ," + //35
			" population_upkeep_reduction           = ? ," + //36
			" portals_upkeep           = ? ," + //37
			" mineral_production           = ? ," + //38
			" crystal_production            = ? ," + //39
			" crystal_decay            = ? ," + //40
			" ectrolium_production             = ? ," + //41
			" energy_interest              = ? ," + //42
			" mineral_interest              = ? ," + //43
			" crystal_interest              = ? ," + //44
			" ectrolium_interest              = ? ," + //45
			" energy                  = ? ," + //46
			" minerals                = ? ," + //47
			" crystals                = ? ," + //48
			" ectrolium               = ? ," + //49
			" networth                = ? ," + //50

			"WHERE id = ?" ; //51 wow what a long string :P
		 PreparedStatement userStatusUpdateStatement = con.prepareStatement(userStatusUpdateQuery); //mass update, much faster



		 //loop over users to get their stats
		while(resultSet.next()){

			if(resultSet.getInt("networth") == 0){
				System.out.println("networth was null");
				continue;
			}

			//check if the players empire is null
			resultSet.getInt("empire_id");
		 	if (resultSet.wasNull()){
				System.out.println("empire was null");
		   		continue;
			}
			int id = resultSet.getInt("networth");
			String race = resultSet.getString("race");
			usersRace.put(id, race);

			HashMap<String,Integer> rowInt = new HashMap<>(columns.size());
			HashMap<String,Long> rowLong = new HashMap<>(columns.size());
			for(String[] col : columns) {
				if(col[1].equals("java.lang.Integer"))
			    		rowInt.put(col[0], resultSet.getInt(col[0]));
				else if(col[1].equals("java.lang.Long"))
			    		rowLong.put(col[0], resultSet.getLong(col[0]));
			}
			//System.out.println(rowInt);
			//System.out.println(rowLong);
			usersInt.add(rowInt);
			usersLong.add(rowLong);
		}

		//loops over users to uodate their stats and planets
		 for(int i = 0; i < usersInt.size(); i++){
			HashMap<String,Integer> rowInt = usersInt.get(i);
			HashMap<String,Long> rowLong  = usersLong.get(i);
			int userID = rowInt.get("user_id");
			HashMap<String, Double> race_info = race_info_list.get(usersRace.get(userID));

			 //System.out.println(race_info);

			int fr = Math.min(rowInt.get("fleet_readiness")+2, rowInt.get("fleet_readiness_max"));
			userStatusUpdateStatement.setInt(1, fr);
			int pr = Math.min(rowInt.get("psychic_readiness")+2, rowInt.get("psychic_readiness_max"));
			userStatusUpdateStatement.setInt(2, pr);
			int ar = Math.min(rowInt.get("agent_readiness")+2, rowInt.get("agent_readiness_max"));
			userStatusUpdateStatement.setInt(3, ar);

			
			portalstSet = statement.executeQuery("SELECT * FROM \"PLANET\" WHERE portal = TRUE AND id = " + userID );
			 //this may be quite slow with a lot of portals and planets, could optimize this later
			LinkedList<Planet> portals = new LinkedList<>();
			
			
			while(resultSet.next()){
				Planet planet = new Planet(resultSet.getInt("x"), resultSet.getInt("y"), resultSet.getInt("i"));
				portals.add(planet);
			}
			
			resultSet = statement.executeQuery("SELECT * FROM \"PLANET\" WHERE id = " + userID);

			long population = 0;
			int num_planets = 0;
			long cmdTickProduction_solar = 0;
			long cmdTickProduction_fission = 0;
			int cmdTickProduction_mineral = 0;
			int cmdTickProduction_crystal = 0;
			int cmdTickProduction_ectrolium = 0;
			long cmdTickProduction_cities = 0;
			int cmdTickProduction_research = 0;

			int total_solar_collectors = 0;
			int total_fission_reactors = 0;
			int total_mineral_plants = 0;
			int total_crystal_labs = 0;
			int total_refinement_stations = 0;
			int total_cities = 0;
			int total_research_centers = 0;
			int total_defense_sats = 0;
			int total_shield_networks = 0;
			int total_portals = 0;


			//loop over planets of each user
			while(resultSet.next()){
				num_planets++;
				int planetID = (resultSet.getInt("id"));
				planetsUpdateStatement.setInt(19, planetID);
				
				HashMap<String, Integer> buildgsBuiltFromJobs = null;
				
				if(jobs.containsKey(planetID))
					buildgsBuiltFromJobs = jobs.get(planetID);
				else
					buildgsBuiltFromJobs = new HashMap<>();

				//Update Population
				int max_population = (resultSet.getInt("size") * population_size_factor);
				max_population += (resultSet.getInt("cities") * building_production_cities);
				max_population *= (1.00 + 0.01 * rowInt.get("research_percent_population"));
				planetsUpdateStatement.setInt(2, max_population);
				
				//planet.current_population += int(np.ceil(planet.current_population * race_info["pop_growth"] * (1.00 + 0.01 * status.research_percent_population) * 0.75**nInfection))
				//planet.current_population = min(planet.max_population, planet.current_population)
				
				int current_population  = Math.ceil(resultSet.getInt("current_population") * race_info.get("pop_growth")*(1.00 + 0.01 * rowInt.get(research_percent_population)));
				current_population = Math.min(current_population, max_population);
				planetsUpdateStatement.setInt(1, current_population);
				
				//add planets population to total population
				population += current_population;
				
				//update portal coverage
				if(resultSet.getBoolean("portal") == true)
					planetsUpdateStatement.setInt(3, 100);
				else{
					if(portals.size() == 0)
						planetsUpdateStatement.setInt(3, 0);
					else
						planetsUpdateStatement.setInt(3, (int)(100.0 * battlePortalCalc(resultSet.getInt("x"), resultSet.getInt("y"), 
													portals, rowInt.get(research_percent_portals)) ));
				}
				
				//update planets buildings
				int solar_collectors = resultSet.getInt("solar_collectors") + buildgsBuiltFromJobs.getOrDefault(solar_collectors,0);
				int fission_reactors = resultSet.getInt("fission_reactors") + buildgsBuiltFromJobs.getOrDefault(fission_reactors,0);
				int mineral_plants = resultSet.getInt("mineral_plants") + buildgsBuiltFromJobs.getOrDefault(mineral_plants,0);
				int crystal_labs = resultSet.getInt("crystal_labs") + buildgsBuiltFromJobs.getOrDefault(crystal_labs,0);
				int refinement_stations = resultSet.getInt("refinement_stations") + buildgsBuiltFromJobs.getOrDefault(refinement_stations,0);
				int cities = resultSet.getInt("cities") + buildgsBuiltFromJobs.getOrDefault(cities,0);
				int research_centers = resultSet.getInt("research_centers") + buildgsBuiltFromJobs.getOrDefault(research_centers,0);
				int defense_sats = resultSet.getInt("defense_sats") + buildgsBuiltFromJobs.getOrDefault(defense_sats,0);
				int shield_networks = resultSet.getInt("shield_networks") + buildgsBuiltFromJobs.getOrDefault(shield_networks,0);
				
				boolean portals = resultSet.getBoolean("portal") || (buildgsBuiltFromJobs.getOrDefault(portal,0) == 1 ? true : false);
				
				planetsUpdateStatement.setInt(6, solar_collectors );
				planetsUpdateStatement.setInt(7, fission_reactors );
				planetsUpdateStatement.setInt(8, mineral_plants);
				planetsUpdateStatement.setInt(9, crystal_labs);
				planetsUpdateStatement.setInt(10, refinement_stations);
				planetsUpdateStatement.setInt(11, cities);
				planetsUpdateStatement.setInt(12, research_centers);
				planetsUpdateStatement.setInt(13, defense_sats);
				planetsUpdateStatement.setInt(14, shield_networks);	
				planetsUpdateStatement.setBoolean(15, portals);	
				
				if (buildgsBuiltFromJobs.getOrDefault(portal,0) == 1 )
					planetsUpdateStatement.setBoolean(16, false);	
				else
					planetsUpdateStatement.setString(16, "portal_under_construction");	//keep the initial value
				
				// Add buildings to running total for player
				total_solar_collectors += solar_collectors;
				total_fission_reactors += fission_reactors;
				total_mineral_plants += mineral_plants;
				total_crystal_labs += crystal_labs;
				total_refinement_stations += refinement_stations;
				total_cities += cities;
				total_research_centers +=research_centers;
				total_defense_sats += defense_sats;
				total_shield_networks += shield_networks;
				total_portals += portals;
				
				int total_buildings = solar_collectors + 
					fission_reactors + mineral_plants +
					crystal_labs + refinement_stations +
					cities + research_centers +
					defense_sats + defense_sats +
					portal;
				
				planetsUpdateStatement.setInt(17, total_buildings);
				
				int buildingsUnderConstr = resultSet.getInt("buildings_under_construction");
				planetsUpdateStatement.setInt(18, buildingsUnderConstr - total_buildings);
				
				//update player production
				cmdTickProduction_solar += (building_production_solar * solar_collectors) * (1 + resultSet.getInt("bonus_solar")/100.0);
				cmdTickProduction_fission += (building_production_fission  * fission_reactors)) * (1 + resultSet.getInt("bonus_fission")/100.0);
				cmdTickProduction_mineral += (building_production_mineral   * mineral_plants) * (1 + resultSet.getInt("bonus_mineral")/100.0);
				cmdTickProduction_crystal += (building_production_crystal    * crystal_labs) * (1 + resultSet.getInt("bonus_crystal")/100.0);
				cmdTickProduction_ectrolium += (building_production_ectrolium    * refinement_stations) * (1 + resultSet.getInt("bonus_ectrolium")/100.0);
				cmdTickProduction_cities += building_production_cities * cities;
				cmdTickProduction_research += building_production_research * research_centers;
				
				double overbuilt = calc_overbuild(resultSet.getInt("size"), total_buildings + resultSet.getInt("buildings_under_construction"));
                double overbuilt_percent = (overbuilt-1.0)*100; 
				
				planetsUpdateStatement.setDouble(4, overbuilt);
				planetsUpdateStatement.setDouble(5, overbuilt_percent);
				
				planetsUpdateStatement.addBatch();
			}
			
			//update reseach
			int artibonus = 0;
			int racebonus = 0;
			if (race.equals("FH"))
				racebonus = 1.5;

			for(int i = 0; i < researchNames.length; i++){
				long rc = usersLong.get(researchNames[0]) + (long) 1.2 * race_info.get(researchNames[1])  * usersInt.get(researchNames[2]) * 
				(100.0 *cmdTickProduction_research + usersLong.get("current_research_funding") + artibonus) / 10000.0 + 
				1.2 * (racebonus * usersLong.get("population") / (600.0*100.0) );
				rc = Math.max(0, rc[i] );
				userStatusUpdateStatement.setLong(17 + i, rc);
				
				"research_max_portals"
				int raceMax = race_info.getOrDefault(researchNames[3], 200);
				int nw = usersLong.get("networth");
				int rcPercent = (int) raceMax * (1.0 - Math.exp(rc / (-10.0 * nw))));
				int currPercent = race_info.get(researchNames[4]);
				if (currPercent > rcPercent)
					userStatusUpdateStatement.setInt(26 + i, currPercent - 1);
				else
					userStatusUpdateStatement.setInt(26 + i, currPercent + 1);
			}
			
			
			
			//update research funding
			userStatusUpdateStatement.setInt(25, Math.max(0, usersLong.get("current_research_funding") * 0.9 ) );
					
			//update total buildings
			userStatusUpdateStatement.setInt(5, total_solar_collectors);
			userStatusUpdateStatement.setInt(6, total_fission_reactors);
			userStatusUpdateStatement.setInt(7, total_mineral_plants);
			userStatusUpdateStatement.setInt(8, total_crystal_labs);
			userStatusUpdateStatement.setInt(9, total_refinement_stations);
			userStatusUpdateStatement.setInt(10, total_cities);
			userStatusUpdateStatement.setInt(11, total_research_centers);
			userStatusUpdateStatement.setInt(12, total_defense_sats);
			userStatusUpdateStatement.setInt(13, total_shield_networks);
			userStatusUpdateStatement.setInt(14, total_portals);
			
			userStatusUpdateStatement.addBatch();
		}
		
		planetsUpdate1 = System.nanoTime();
		planetsUpdateStatement.executeBatch();
		planetsUpdate2 = System.nanoTime();
		
		userUpdate1 = System.nanoTime();
		userStatusUpdateStatement.executeBatch();
		userUpdate2 = System.nanoTime();

	}
	catch (Exception e) {
            System.out.println("exception " +  e.getMessage());
        }
	     
	long endTime = System.nanoTime();
		
	System.out.println("connection time " + (double)(connectionTime - startTime)/1_000_000_000.0 + " sec.");
	System.out.println("Construction jobs update: " + (double)(jobsUpdate2-jobsUpdate1)/1_000_000_000.0 + " sec.");
	System.out.println("Planets update: " + (double)(planetsUpdate2-planetsUpdate1)/1_000_000_000.0 + " sec.");
	System.out.println("Users update: " + (double)(userUpdate2-userUpdate1)/1_000_000_000.0 + " sec.");
	System.out.println("Total time: "(double)(endTime-startTime)/1_000_000_000.0 + " sec.");
    }
	
	private double battlePortalCalc(int x, int y, LinkedList<Planet> portals, int portalResearch){
		double cover = 0
		for (Planet portal : portals){
		    double d = Math.sqrt(Math.pow((x-portal.x),2) + Math.pow((y-portal.y),2));
		    cover = Math.max(0, 1.0 - Math.sqrt(d/(7.0*(1.0 + 0.01*portalResearch))));
		}
		return cover;
	}
	
	private static HashMap<Integer, HashMap<String, Integer>> execute_jobs (Connection con){
		
		HashMap<String, String> buildingsNames = new HashMap<>();
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
		HashMap<Integer, HashMap<String, Integer>> planetJobsCombined = new HashMap<>();
		
		try{
			String planetjobsUpdateQuery = "UPDATE app_construction SET " +
				" ticks_remaining  = ? " + //1
				" WHERE id = ? " ; //2
			PreparedStatement updateJobsTicks = con.prepareStatement(planetjobsUpdateQuery);	
			
			String deleteJobsQuery = "DELETE FROM app_construction WHERE id = ?";
			PreparedStatement deleteJobs = con.prepareStatement(deleteJobsQuery);	
			
			
			
			Statement statement = con.createStatement();
			ResultSet resultSet = statement.executeQuery("SELECT * FROM app_construction");
			
			while(resultSet.next()){
				int ticksRemaining = resultSet.getInt("ticks_remaining");
				System.out.println("ticksRemaining" + ticksRemaining);
				int jobID = resultSet.getInt("id");
				if(ticksRemaining <= 1){
					String building = buildingsNames.get(resultSet.getString("building_type"));
					int numberBuilt = resultSet.getInt("n");
					int planetID = resultSet.getInt("planet_id");
					if (!planetJobsCombined.containsKey(planetID)){
						planetJobsCombined.put(planetID, new HashMap<String, Integer>());
					}
					HashMap<String, Integer> tmp = planetJobsCombined.get(planetID);
					if (!tmp.containsKey(building)){
						tmp.put(building, 0);
					}
					tmp.put(building, tmp.get(building) + numberBuilt);
					deleteJobs.setInt(1, jobID);
					deleteJobs.addBatch();
				}
				else{
					System.out.println("ticksRemaining" + ticksRemaining + " jobID " + jobID );
					updateJobsTicks.setInt(1, ticksRemaining-1);
					updateJobsTicks.setInt(2, jobID);
					updateJobsTicks.addBatch();
				}
			}
			
			updateJobsTicks.executeBatch();
			deleteJobs.executeBatch();
		}
		catch (Exception e) {
			
            System.out.println("exception " +  e.getMessage());
        }
		
		return planetJobsCombined;
	}
	
}


/* String userStatusUpdateQuery = "UPDATE app_userstatus SET "+
+			" fleet_readiness  = ? ," +  //1
+			" psychic_readiness  = ? ," + //2
+			" agent_readiness  = ? ," + //3
			" population   = ? ," + //4
+			" total_solar_collectors  = ? ," + //5
+			" total_fission_reactors  = ? ," + //6
+			" total_mineral_plants  = ? ," + //7
+			" total_crystal_labs  = ? ," + //8
+			" total_refinement_stations   = ? ," + //9
+			" total_cities  = ? ," + //10
+			" total_research_centers   = ? ," + //11
+			" total_defense_sats    = ? ," + //12
+			" total_shield_networks   = ? ," + //13
+			" total_portals  = ? ," + //14
+			" research_points_military   = ? ," + //17
+			" research_points_construction   = ? ," + //18
+			" research_points_tech   = ? ," + //19
+			" research_points_energy    = ? ," + //20
+			" research_points_population   = ? ," + //21
+			" research_points_culture    = ? ," + //22
+			" research_points_operations   = ? ," + //23
+			" research_points_portals    = ? ," + //24
+			" current_research_funding    = ? ," + //25
+			" research_percent_military   = ? ," + //26
+			" research_percent_construction    = ? ," + //27
+			" research_percent_tech            = ? ," + //28
+			" research_percent_energy          = ? ," + //29
+			" research_percent_population      = ? ," + //30
+			" research_percent_culture         = ? ," + //31
+			" research_percent_operations      = ? ," + //32
+			" research_percent_portals         = ? ," + //33
			" energy_production          = ? ," + //34
			" energy_decay          = ? ," + //35
			" buildings_upkeep          = ? ," + //36
			" units_upkeep          = ? ," + //37
			" population_upkeep_reduction           = ? ," + //38
			" portals_upkeep           = ? ," + //39
			" mineral_production           = ? ," + //40
			" crystal_production            = ? ," + //41
			" crystal_decay            = ? ," + //42
			" ectrolium_production             = ? ," + //43
			" energy_interest              = ? ," + //44
			" mineral_interest              = ? ," + //45
			" crystal_interest              = ? ," + //46
			" ectrolium_interest              = ? ," + //47
			" energy                  = ? ," + //48
			" minerals                = ? ," + //49
			" crystals                = ? ," + //50
			" ectrolium               = ? ," + //51
			" networth                = ? ," + //52

			"WHERE id = ?" ; //53 wow what a long string :P*/
