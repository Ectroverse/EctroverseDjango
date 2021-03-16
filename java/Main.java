import java.sql.*;
import java.util.*;
import java.time.Clock; 
import java.time.Instant; 
import java.util.concurrent.*;
//import java.util.Arrays.*;

public class Main
{
	//some constants temporarily written here, fetch them from app/constants.py later
    private static final int total_units = 13;
	private static final int population_size_factor  = 20;
	private static final double energy_decay_factor = 0.005;
	private static final double crystal_decay_factor = 0.02;
	private static final int upkeep_solar_collectors = 0;
	private static final int upkeep_fission_reactors = 20;
	private static final int upkeep_mineral_plants = 2;
	private static final int upkeep_crystal_labs = 2;
	private static final int upkeep_refinement_stations = 2;
	private static final int upkeep_cities = 4;
	private static final int upkeep_research_centers = 1;
	private static final int upkeep_defense_sats = 4;
	private static final int upkeep_shield_networks = 16;
	private static final int networth_per_building = 8;
	private static final int building_production_solar = 12;
	private static final int building_production_fission = 40;
	private static final int building_production_mineral = 1;
	private static final int building_production_crystal = 1;
	private static final int building_production_ectrolium = 1;
	private static final int building_production_cities = 1000;
	private static final int building_production_research = 6;
	private static final double [] unit_upkeep = {2.0, 1.6, 3.2, 12.0, 18.0, 0.4, 0.6, 2.8, 0.0, 0.8, 0.8, 2.4, 60.0};
	
	static final HashMap<String,HashMap<String, Double>> race_info_list = new HashMap<>();
	/* HK = 'HK', _('Harks')
        MT = 'MT', _('Manticarias')
        FH = 'FH', _('Foohons')
        SB = 'SB', _('Spacebornes')
        DW = 'DW', _('Dreamweavers')
        WK = 'WK', _('Wookiees')*/
	static final HashMap<String, Double> harks = new HashMap<>();
	static final HashMap<String, Double> manticarias = new HashMap<>();
	static final HashMap<String, Double> foohons = new HashMap<>();
	static final HashMap<String, Double> spacebournes = new HashMap<>();
	static final HashMap<String, Double> dreamweavers = new HashMap<>();
	static final HashMap<String, Double> wookiees = new HashMap<>();
	static final HashMap<String, String> buildingsNames = new HashMap<>();
	
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
	wookiees.put("race_special_resource_private static final interest",   1.005);
	
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
	
	private static final String [][] researchNames = {
		{"research_points_military", "research_bonus_military", "alloc_research_military", "research_max_military", "research_percent_military"},
		{"research_points_construction", "research_bonus_construction", "alloc_research_construction", "research_max_construction", "research_percent_construction"},
		{"research_points_tech", "research_bonus_tech", "alloc_research_tech", "research_max_tech", "research_percent_tech"},
		{"research_points_energy", "research_bonus_energy", "alloc_research_energy", "research_max_energy", "research_percent_energy"},
		{"research_points_population", "research_bonus_population", "alloc_research_population", "research_max_population", "research_percent_population" },
		{"research_points_culture", "research_bonus_culture", "alloc_research_culture", "research_max_culture", "research_percent_culture"},
		{"research_points_operations", "research_bonus_operations", "alloc_research_operations", "research_max_operations", "research_percent_operations"},
		{"research_points_portals", "research_bonus_portals", "alloc_research_portals", "research_max_portals", "research_percent_portals"},
		};
	
	private static final double [] units_upkeep_costs = {2.0, 1.6, 3.2, 12.0, 18.0, 0.4, 0.6, 2.8, 0.0, 0.8, 0.8, 2.4, 60.0};
	
	private static final double [] units_nw = {4,3,5,12,14,1,1,4,7,2,2,6,30};
	
	private static final String [] unit_names = {"bomber", "fighter", "transport", "cruiser", "carrier", "soldier", "droid", "goliath", "phantom", "wizard", "agent", "ghost", "exploration"};
	
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
		long startTime = System.nanoTime();
		long connectionTime = 0;
		
		Connection tmpCon = null;
		try{
			tmpCon = DriverManager.getConnection("jdbc:postgresql://ectroversedjango_db_1:5432/djangodatabase", "dbadmin", "admin12345");
			connectionTime = System.nanoTime();
		}
		catch (Exception e) {
			try{
				tmpCon.rollback();
			}
			catch (Exception ex) {
				System.out.println("exception " +  ex.getMessage());
			}
			System.out.println("exception " +  e.getMessage());
			System.out.println("Connection with postgres DB not established, aborting." );
			System.exit(0);
		}
		final Connection con = tmpCon;
		
		System.out.println("connection time " + (double)(connectionTime - startTime)/1_000_000_000.0 + " sec.");
		
		ScheduledExecutorService s = Executors.newSingleThreadScheduledExecutor();
		Calendar calendar = Calendar.getInstance();
		Runnable scheduledTask = new Runnable() {
			public void run() {
				processTick(con);
			}
		};
		
		//use this for 10 second tick
		long millistoNext = secondsToFirstOccurence10(calendar);	
		s.scheduleAtFixedRate(scheduledTask, millistoNext, 10*1000, TimeUnit.MILLISECONDS);
		
		//use this for 10 minute tick
		// long millistoNext = secondsToFirstOccurence600(calendar);	
		// s.scheduleAtFixedRate(scheduledTask, millistoNext, 600*1000, TimeUnit.MILLISECONDS);
	}	
    
	private static void processTick(Connection con){
		long startTime = 0;
		long resultTime = 0;
		long executeBatchTime = 0;
		long jobsUpdate1 = 0;
		long jobsUpdate2 = 0;
		long planetsUpdate1 = 0;
		long planetsUpdate2 = 0;
		long userUpdate1 = 0;
		long userUpdate2 = 0;
		long test1 = 0;
		long test2 = 0;
		
		try {
		con.setAutoCommit(false);
	 	startTime = System.nanoTime();
		Statement statement = con.createStatement();
		//statement.executeQuery("BEGIN; ");
		//test1 = System.nanoTime();
		statement.execute("LOCK TABLE \"PLANET\", app_roundstatus, app_userstatus, app_construction IN ACCESS EXCLUSIVE MODE;");

		
		/*
		 try (Statement statement = conn.createStatement()) {
		  statement.execute("BEGIN");
		  try {
			// use statement ...
			statement.execute("COMMIT");
		  }
		  catch (SQLException failure) {
			statement.execute("ROLLBACK");
		  }
		}*/
		
		//update tick number
		ResultSet resultSet = statement.executeQuery("SELECT tick_number FROM app_roundstatus");
		resultSet.next();
		int tick_nr = resultSet.getInt("tick_number");
		
		statement.executeUpdate("UPDATE app_roundstatus SET tick_number = " + (tick_nr + 1) );
		
		//update construction jobs	
		jobsUpdate1 = System.nanoTime();
		HashMap<Integer, HashMap<String, Integer>> jobs = execute_jobs(con);
		jobsUpdate2 = System.nanoTime();
		//update units jobs
		 
		//update fleets
		 
		resultSet = statement.executeQuery("SELECT * FROM app_userstatus");
	   	ResultSetMetaData rsmd = resultSet.getMetaData();
	   	ArrayList<String []> columns = new ArrayList<>(rsmd.getColumnCount());
		
		//test2 = System.nanoTime();
		//System.out.println("Construction jobs update: " + (double)(test2-test1)/1_000_000_000.0 + " sec.");
		 
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
			" buildings_under_construction = ? " + //18
			 
		 	" WHERE id = ?" ; //19
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
			" energy_income              = ? ," + //46
			" mineral_income              = ? ," + //47
			" crystal_income              = ? ," + //48
			" ectrolium_income              = ? ," + //49
			" energy                  = ? ," + //50
			" minerals                = ? ," + //51
			" crystals                = ? ," + //52
			" ectrolium               = ? ," + //53
			" networth                = ? ," + //54
			" num_planets = ? " + //55

			" WHERE id = ?" ; //56 wow what a long string :P
		 PreparedStatement userStatusUpdateStatement = con.prepareStatement(userStatusUpdateQuery); //mass update, much faster
		 
		 
		String planetStatusUpdateQuery2 = "UPDATE \"PLANET\"  SET" +
			" current_population = ? "+	 //1		 
			" WHERE id = ?"  ; //2
		PreparedStatement planetsUpdateStatement2 = con.prepareStatement(planetStatusUpdateQuery2); 
			
		 //loop over users to get their stats
		while(resultSet.next()){

			if(resultSet.getInt("networth") == 0){
				//System.out.println("networth was null");
				continue;
			}

			//check if the players empire is null
			resultSet.getInt("empire_id");
		 	if (resultSet.wasNull()){
				//System.out.println("empire was null");
		   		continue;
			}
			int id = resultSet.getInt("id");
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

		//loops over users to uodate their stats and planets --main loop!
		 for(int j = 0; j < usersInt.size(); j++){
			HashMap<String,Integer> rowInt = usersInt.get(j);
			HashMap<String,Long> rowLong  = usersLong.get(j);
			int userID = rowInt.get("user_id");
			userStatusUpdateStatement.setInt(56, userID);
			String race = usersRace.get(userID);
			HashMap<String, Double> race_info = race_info_list.get(race);
			

			 //System.out.println(race_info);

			int fr = Math.min(rowInt.get("fleet_readiness")+2, rowInt.get("fleet_readiness_max"));
			userStatusUpdateStatement.setInt(1, fr);
			int pr = Math.min(rowInt.get("psychic_readiness")+2, rowInt.get("psychic_readiness_max"));
			userStatusUpdateStatement.setInt(2, pr);
			int ar = Math.min(rowInt.get("agent_readiness")+2, rowInt.get("agent_readiness_max"));
			userStatusUpdateStatement.setInt(3, ar);

			test1 = System.nanoTime();

			ResultSet portalstSet = statement.executeQuery("SELECT * FROM \"PLANET\" WHERE portal = TRUE AND id = " + userID );
			
			test2 = System.nanoTime();
			System.out.println("Select portals: " + (double)(test2-test1)/1_000_000_000.0 + " sec.");
			
			 //this may be quite slow with a lot of portals and planets, could optimize this later
			LinkedList<Planet> portals = new LinkedList<>();
			
			
			while(portalstSet.next()){
				Planet planet = new Main().new Planet(resultSet.getInt("x"), resultSet.getInt("y"), resultSet.getInt("i"));
				portals.add(planet);
			}


			long population = 0;
			long networth = 0;
			int num_planets = 0;
			long cmdTickProduction_solar = 0;
			long cmdTickProduction_fission = 0;
			int cmdTickProduction_mineral = 0;
			int cmdTickProduction_crystal = 0;
			int cmdTickProduction_ectrolium = 0;
			//long cmdTickProduction_cities = 0;
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
			int total_portals = portals.size();
			
			test1 = System.nanoTime();
			resultSet = statement.executeQuery("SELECT * FROM \"PLANET\" WHERE owner_id = " + userID);
			test2 = System.nanoTime();
			System.out.println("Select planets: " + (double)(test2-test1)/1_000_000_000.0 + " sec.");
			
			rsmd = resultSet.getMetaData();
			int colNumber = rsmd.getColumnCount();
			
			int[] colTypes = new int[colNumber];
			System.out.println("=================================");
			for (int i = 0; i < colNumber; i++) {
				//colTypes[i] = rsmd.getColumnType(i + 1);
				//System.out.print(i + " " + rsmd.getColumnName(i+1) + " colTypes[i]: " + colTypes[i] + " " );
			}
			System.out.println("=================================!");

	
			test1 = System.nanoTime();	
System.out.println("test00");			
			//loop over planets of each user
			while(resultSet.next()){
				num_planets++;
System.out.println("test0");				
				Object[] rowValues = new Object[colNumber];
				for (int i = 0; i < colNumber; i++) {
					 //rowValues[i] = getValueByType(i + 1, colTypes[i], resultSet);
				}
System.out.println("test01");
				int planetID = (resultSet.getInt("id"));
				planetsUpdateStatement.setInt(19, planetID);
				
				HashMap<String, Integer> buildgsBuiltFromJobs = null;
				
				//System.out.println("jobs" + jobs + " planetID " + planetID);
				
				if(jobs.containsKey(planetID))
					buildgsBuiltFromJobs = jobs.get(planetID);
				else
					buildgsBuiltFromJobs = new HashMap<>();

				//Update Population
				
				int max_population = (resultSet.getInt("size") * population_size_factor);
				max_population += (resultSet.getInt("cities") * building_production_cities);
				max_population *= (1.00 + 0.01 * rowInt.get("research_percent_population"));
				planetsUpdateStatement.setInt(2, max_population);
System.out.println("test1");
				//planet.current_population += int(np.ceil(planet.current_population * race_info["pop_growth"] * (1.00 + 0.01 * status.research_percent_population) * 0.75**nInfection))
				//planet.current_population = min(planet.max_population, planet.current_population)
				
				int current_population  = (int) Math.ceil(resultSet.getInt("current_population") * race_info.get("pop_growth")*(1.00 + 0.01 * rowInt.get("research_percent_population")));
				current_population = Math.min(current_population, max_population);;
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
													portals, rowInt.get("research_percent_portals")) ));
				}
System.out.println("test2");
				//System.out.println("buildgsBuiltFromJobs" + buildgsBuiltFromJobs);
				//update planets buildings
				int solar_collectors = resultSet.getInt("solar_collectors") + buildgsBuiltFromJobs.getOrDefault("solar_collectors",0);
				int fission_reactors = resultSet.getInt("fission_reactors") + buildgsBuiltFromJobs.getOrDefault("fission_reactors",0);
				int mineral_plants = resultSet.getInt("mineral_plants") + buildgsBuiltFromJobs.getOrDefault("mineral_plants",0);
				int crystal_labs = resultSet.getInt("crystal_labs") + buildgsBuiltFromJobs.getOrDefault("crystal_labs",0);
				int refinement_stations = resultSet.getInt("refinement_stations") + buildgsBuiltFromJobs.getOrDefault("refinement_stations",0);
				int cities = resultSet.getInt("cities") + buildgsBuiltFromJobs.getOrDefault("cities",0);
				int research_centers = resultSet.getInt("research_centers") + buildgsBuiltFromJobs.getOrDefault("research_centers",0);
				int defense_sats = resultSet.getInt("defense_sats") + buildgsBuiltFromJobs.getOrDefault("defense_sats",0);
				int shield_networks = resultSet.getInt("shield_networks") + buildgsBuiltFromJobs.getOrDefault("shield_networks",0);
				
				boolean portal = resultSet.getBoolean("portal") || (buildgsBuiltFromJobs.getOrDefault("portal",0) == 1 ? true : false);
				
				planetsUpdateStatement.setInt(6, solar_collectors );
				planetsUpdateStatement.setInt(7, fission_reactors );
				planetsUpdateStatement.setInt(8, mineral_plants);
				planetsUpdateStatement.setInt(9, crystal_labs);
				planetsUpdateStatement.setInt(10, refinement_stations);
				planetsUpdateStatement.setInt(11, cities);
				planetsUpdateStatement.setInt(12, research_centers);
				planetsUpdateStatement.setInt(13, defense_sats);
				planetsUpdateStatement.setInt(14, shield_networks);	
				planetsUpdateStatement.setBoolean(15, portal);	
				if (portal)
					planetsUpdateStatement.setBoolean(16, false);	
				else
					planetsUpdateStatement.setBoolean(16, resultSet.getBoolean("portal_under_construction"));	//keep the initial value
System.out.println("test3");				
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
				total_portals += (portal == true? 1 : 0);
				
				int total_buildings = solar_collectors + 
					fission_reactors + mineral_plants +
					crystal_labs + refinement_stations +
					cities + research_centers +
					defense_sats + shield_networks +
					(portal == true? 1 : 0);
				
				networth += total_buildings * networth_per_building;
				
                networth += (resultSet.getInt("bonus_solar") * 1.25);
                networth += (resultSet.getInt("bonus_mineral")  * 1.45);
                networth += (resultSet.getInt("bonus_crystal") * 2.25);
                networth += (resultSet.getInt("bonus_ectrolium") * 1.65);
                networth += (resultSet.getInt("bonus_fission") * 5.0);

                networth += (resultSet.getInt("size") * 1.75);
				
				
				planetsUpdateStatement.setInt(17, total_buildings);
System.out.println("test4");				
				int buildingsUnderConstr = resultSet.getInt("buildings_under_construction");
				planetsUpdateStatement.setInt(18, buildingsUnderConstr - total_buildings);
				
				//update player production
				cmdTickProduction_solar += (building_production_solar * solar_collectors) * (1 + resultSet.getInt("bonus_solar")/100.0);
				cmdTickProduction_fission += (building_production_fission  * fission_reactors) * (1 + resultSet.getInt("bonus_fission")/100.0);
				cmdTickProduction_mineral += (building_production_mineral   * mineral_plants) * (1 + resultSet.getInt("bonus_mineral")/100.0);
				cmdTickProduction_crystal += (building_production_crystal    * crystal_labs) * (1 + resultSet.getInt("bonus_crystal")/100.0);
				cmdTickProduction_ectrolium += (building_production_ectrolium    * refinement_stations) * (1 + resultSet.getInt("bonus_ectrolium")/100.0);
				//cmdTickProduction_cities += building_production_cities * cities;
				cmdTickProduction_research += building_production_research * research_centers;
				
				double overbuilt = (double)(calc_overbuild(resultSet.getInt("size"), total_buildings + resultSet.getInt("buildings_under_construction")));
                double overbuilt_percent = (double)((overbuilt-1.0)*100); 
				
				planetsUpdateStatement.setDouble(4, overbuilt);
				planetsUpdateStatement.setDouble(5, overbuilt_percent);
				//add planet only if something has changed
System.out.println("test5");				
				planetsUpdateStatement2.setInt(1,current_population+1);
				planetsUpdateStatement2.setInt(2, planetID);
			
				planetsUpdateStatement2.addBatch();
System.out.println("test6");
				//planetsUpdateStatement.addBatch();
			}
			test2 = System.nanoTime();
			System.out.println("planet loop: " + (double)(test2-test1)/1_000_000_000.0 + " sec.");

			//update planets
			userStatusUpdateStatement.setInt(55, num_planets);
			
			//update population
			userStatusUpdateStatement.setLong(4, population);
			
			//update reseach
			int artibonus = 0;
			double racebonus = 0;
			if (race.equals("FH"))
				racebonus = 1.0;

			long totalRcPoints = 0;

			for(int i = 0; i < researchNames.length; i++){				
				long rc = (long) (rowLong.get(researchNames[i][0]) +  1.2 * race_info.get(researchNames[i][1])  * rowInt.get(researchNames[i][2]) * 
				(100.0 *cmdTickProduction_research + rowLong.get("current_research_funding")/10 + artibonus) / 10000.0 + 
				1.2 * (racebonus * rowLong.get("population") / (600.0*100.0) ));
				
				rc = Math.max(0, rc);
				totalRcPoints += rc;
				userStatusUpdateStatement.setLong(15 + i, rc);
				Double raceMax = race_info.getOrDefault(researchNames[i][3], 200.0);
				long nw = rowLong.get("networth");
				int rcPercent = (int) (raceMax * (1.0 - Math.exp(rc / (-10.0 * nw))));
				int currPercent = (int) (Math.ceil(rowInt.get(researchNames[i][4])));
				
				if (currPercent > rcPercent)
					userStatusUpdateStatement.setInt(24 + i, currPercent - 1);
				else
					userStatusUpdateStatement.setInt(24 + i, currPercent + 1);
			}
			long current_research_funding  = rowLong.get("current_research_funding") * 9 / 10;
			userStatusUpdateStatement.setLong(23, current_research_funding);

			//update energy income
			//race_special_solar_15
			long energyProduction = (long)(cmdTickProduction_solar * race_info.getOrDefault("race_special_solar_15", 1.0));
			energyProduction += cmdTickProduction_fission;
			double energyResearchFactor = 1.0 + 0.01* race_info.getOrDefault("energy_production", 1.0);
			energyProduction = (long) (energyProduction * energyResearchFactor);
			userStatusUpdateStatement.setLong(32, energyProduction);
			
			//energy decay
			long lastTickEnergy = rowLong.get("energy");
			long energyDecay = (long) (Math.max(0,lastTickEnergy * energy_decay_factor));
			userStatusUpdateStatement.setLong(33, energyDecay);
			
			//energy interest
			long energy_interest = (long) (rowLong.get("energy") * race_info.getOrDefault("race_special_resource_interest", 0.0));
			userStatusUpdateStatement.setLong(42, energy_interest);
		
			//buildings upkeep
			long buildings_upkeep = 
            (long) (total_solar_collectors * upkeep_solar_collectors * energyResearchFactor +
            total_fission_reactors * upkeep_fission_reactors * energyResearchFactor +
            total_mineral_plants * upkeep_mineral_plants +
            total_crystal_labs * upkeep_crystal_labs +
            total_refinement_stations * upkeep_refinement_stations +
            total_cities * upkeep_cities +
            total_research_centers * upkeep_research_centers +
            total_defense_sats * upkeep_defense_sats +
            total_shield_networks * upkeep_shield_networks);
			userStatusUpdateStatement.setLong(34, buildings_upkeep);
			//units upkeep
			//get unit amounts
			long [] unitsSums = new long[total_units];
			Statement statement2 = con.createStatement();
			
			for(int z = 0; z < unit_names.length; z++){
				
				String s = unit_names[z];
				String query = "SELECT SUM(" + s + ") FROM app_fleet WHERE id = " + userID;
				ResultSet result = statement2.executeQuery(query);
				result.next();
				unitsSums[z] = result.getLong("sum"); 
			}

			long units_upkeep = 0;
			for(int i = 0; i < total_units; i++) {
				units_upkeep += (long)(units_upkeep_costs[i] * unitsSums[i]);
				networth += (long)(unitsSums[i] * units_nw[i]);
			}
			userStatusUpdateStatement.setLong(35, units_upkeep);
			
			//portals upkeep
			int portals_upkeep = (int)(Math.max(0, (Math.pow(Math.max(1, total_portals) - 1, 1.2736) * 10000.0 / (1.0 + rowInt.get("research_percent_culture")/100.0))));
			userStatusUpdateStatement.setInt(37, portals_upkeep);

			//population upkeep reduction		
			long population_upkeep_reduction = population / 35;
			population_upkeep_reduction = Math.min(population_upkeep_reduction, buildings_upkeep + units_upkeep + portals_upkeep);
			userStatusUpdateStatement.setLong(36, population_upkeep_reduction);
			
			//update resources income
			//energy
			long energy_income = energyProduction - energyDecay + energy_interest - units_upkeep - portals_upkeep + population_upkeep_reduction;
			userStatusUpdateStatement.setLong(46, energy_income);

			//minerals
		    int mineral_production = (int) (race_info.get("mineral_production") * cmdTickProduction_mineral);
		    int mineral_decay = 0;
		    int mineral_interest = (int) (rowLong.get("minerals") * race_info.getOrDefault("race_special_resource_interest", 0.0));
		    int mineral_income = mineral_production - mineral_decay + mineral_interest;
		    userStatusUpdateStatement.setInt(38, mineral_production);
		    userStatusUpdateStatement.setInt(43, mineral_interest);
		    userStatusUpdateStatement.setInt(47, mineral_income);

		    //crystals
    	    int crystal_production = (int) (race_info.get("crystal_production") * cmdTickProduction_crystal);
    	    int crystal_decay = (int) (Math.max(0.0,rowLong.get("crystals") * crystal_decay_factor));
    	    int crystal_interest = (int) (rowLong.get("crystals") * race_info.getOrDefault("race_special_resource_interest", 0.0));
    	    int crystal_income = crystal_production - crystal_decay + crystal_interest;
    	    userStatusUpdateStatement.setInt(39, crystal_production);
    	    userStatusUpdateStatement.setInt(40, crystal_decay);
    	    userStatusUpdateStatement.setInt(44, crystal_interest);
    	    userStatusUpdateStatement.setInt(48, crystal_income);
			
    	    //ectrolium		    	    
    	    int ectrolium_production = (int) (race_info.get("ectrolium_production") * cmdTickProduction_ectrolium);
    	    int ectrolium_decay = 0;
    	    int ectrolium_interest =(int) (rowLong.get("ectrolium") * race_info.getOrDefault("race_special_resource_interest", 0.0));
    	    int ectrolium_income = ectrolium_production + ectrolium_decay + ectrolium_interest;
    	    userStatusUpdateStatement.setInt(41, ectrolium_production);
    	    userStatusUpdateStatement.setInt(45, ectrolium_interest);
    	    userStatusUpdateStatement.setInt(49, ectrolium_income);
    	    
    	    //update total resources
    	    userStatusUpdateStatement.setLong(50, Math.max(0, rowLong.get("energy") + energy_income));
    	    userStatusUpdateStatement.setLong(51, Math.max(0, rowLong.get("minerals") + mineral_income));
    	    userStatusUpdateStatement.setLong(52, Math.max(0,rowLong.get("crystals") + crystal_income));
    	    userStatusUpdateStatement.setLong(53, Math.max(0,rowLong.get("ectrolium") + ectrolium_income));
					
			//update research funding
			userStatusUpdateStatement.setLong(25, (long) Math.max(0, rowLong.get("current_research_funding") * 0.9 ) );	
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
			
			//update networth
			networth += population * 0.005;
			networth += (0.001 * totalRcPoints);
			userStatusUpdateStatement.setLong(54, networth);
			userStatusUpdateStatement.addBatch();
		}
	
		planetsUpdate1 = System.nanoTime();
		//planetsUpdateStatement.executeBatch();
		planetsUpdateStatement2.executeBatch();
		planetsUpdate2 = System.nanoTime();
		
		userUpdate1 = System.nanoTime();
		userStatusUpdateStatement.executeBatch();
		userUpdate2 = System.nanoTime();
		con.commit();
		}
		catch (Exception e) {
				
				System.out.println("exception " +  e.getMessage());
		}
			 
		long endTime = System.nanoTime();
		
		Clock clock = Clock.systemDefaultZone();
		Instant instant = clock.instant();
		System.out.println("Tick completion time: " + instant);	
		System.out.println("Construction jobs update: " + (double)(jobsUpdate2-jobsUpdate1)/1_000_000_000.0 + " sec.");
		System.out.println("Planets update: " + (double)(planetsUpdate2-planetsUpdate1)/1_000_000_000.0 + " sec.");
		System.out.println("Users update: " + (double)(userUpdate2-userUpdate1)/1_000_000_000.0 + " sec.");
		System.out.println("Total time: " + (double)(endTime-startTime)/1_000_000_000.0 + " sec.");
		System.out.println("");
	}
	
    private static double calc_overbuild(int size, int buildings) {
    	return 0;
    }
	
	private static double battlePortalCalc(int x, int y, LinkedList<Planet> portals, int portalResearch){
		double cover = 0;
		for (Planet portal : portals){
		    double d = Math.sqrt(Math.pow((x-portal.posX),2) + Math.pow((y-portal.posY),2));
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
			e.printStackTrace();
        }
		
		return planetJobsCombined;
	}
	
	
	private static long secondsToFirstOccurence10(Calendar calendar) {
    int seconds = calendar.get(Calendar.SECOND);
    int millis = calendar.get(Calendar.MILLISECOND);
    int secondsToNextTenSeconds = 10 - seconds % 10 -1;
    int millisToNextSecond = 1000 - millis;
    return secondsToNextTenSeconds*1000 + millisToNextSecond;
	}
	
	private static long secondsToFirstOccurence600(Calendar calendar) {
	int minutes = calendar.get(Calendar.MINUTE);
    int seconds = calendar.get(Calendar.SECOND);
    int millis = calendar.get(Calendar.MILLISECOND);
	int minutesToNextTenMinutes = 10 - minutes % 10 -1;
    int secondsToNextMinute = 60 - seconds -1;
    int millisToNextSecond = 1000 - millis;
    return minutesToNextTenMinutes*60*1000 + secondsToNextMinute*1000 + millisToNextSecond;
	}

	private static Object getValueByType(int columnIndex, int columnType, ResultSet queryResult) throws SQLException {
		switch (columnType) {
			case Types.CHAR:
			case Types.NCHAR:
			case Types.VARCHAR:
			case Types.NVARCHAR:
				return queryResult.getString(columnIndex);
			case Types.INTEGER:
				return queryResult.getInt(columnIndex);
			case Types.TIMESTAMP:
				return queryResult.getTimestamp(columnIndex);
			case Types.DATE:
				return queryResult.getDate(columnIndex);
			default:
				return queryResult.getDouble(columnIndex);
		}
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
