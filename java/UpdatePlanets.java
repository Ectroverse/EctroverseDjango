package org.ectroverse.processtick;

import java.sql.*;
import java.util.*;
import static org.ectroverse.processtick.Constants.*;

public class UpdatePlanets{
	
	private final String planetStatusUpdateQuery = "UPDATE \"PLANET\"  SET" +
	" protection = ? ," + //1
	" overbuilt = ? ," + //2
	" overbuilt_percent = ? ," + //3
	" solar_collectors = ? ," + //4
	" fission_reactors = ? ," + //5
	" mineral_plants = ? ," + //6
	" crystal_labs = ? ," + //7
	" refinement_stations = ? , " + //8
	" cities = ? ," + //9
	" research_centers = ? ," + //10
	" defense_sats = ? ," + //11
	" shield_networks = ? ," + //12
	" portal = ? ," + //13
	" portal_under_construction = ? ," + //14
	" total_buildings = ? ," + //15
	" buildings_under_construction = ? " + //16
	" WHERE id = ?" ; //17
	PreparedStatement planetsUpdateStatement;
	
	private long population;
	private long networth;
	private int num_planets;
	private long cmdTickProduction_solar ;
	private long cmdTickProduction_fission;
	private int cmdTickProduction_mineral;
	private int cmdTickProduction_crystal;
	private int cmdTickProduction_ectrolium;
	private int cmdTickProduction_research;
	
	private int [] totalBuildings;
	private int [] totalBuildingsBuilt;

	private Connection connection;
	private Statement statement;
	private HashMap<Integer, HashMap<String, Integer>> jobs;
	
	public UpdatePlanets(Connection connection) throws Exception{   
		//we call the class constructor only once in process tick because we wasnt to keep the planetsUpdateStatement while iterating users
		this.connection = connection;
		statement = connection.createStatement();
		planetsUpdateStatement = connection.prepareStatement(planetStatusUpdateQuery);
		//update construction jobs on all planets
		jobs = execute_jobs(connection);
	}
	
	public void updateUserPlanets(int userID, int empireID, HashMap<String,Integer> userIntValues, HashMap<String, Double> race_info,
									LinkedList<Planet> portals, UpdateNews updateNews, PreparedStatement userStatusUpdateStatement)
									throws Exception{
		population = 0;
		networth = 0;
		num_planets = 0;
		cmdTickProduction_solar = 0;
		cmdTickProduction_fission = 0;
		cmdTickProduction_mineral = 0;
		cmdTickProduction_crystal = 0;
		cmdTickProduction_ectrolium = 0;
		cmdTickProduction_research = 0;
		
		totalBuildings = new int [20];
		totalBuildingsBuilt = new int [20];
		
		ResultSet resultSet = statement.executeQuery("SELECT * FROM \"PLANET\" WHERE owner_id = " + userID);
		ResultSetMetaData rsmd = resultSet.getMetaData();
		rsmd = resultSet.getMetaData();
		
		int colNumber = rsmd.getColumnCount();
		int[] colTypes = new int[colNumber];
		
		//so we don't have to search colums everytime later on or if the model is changed we will still be able to find them
		int [] colLocation  = new int [31];
		for (int i = 0; i < colNumber; i++) {
			colTypes[i] = rsmd.getColumnType(i + 1);
			switch (rsmd.getColumnName(i+1)){
				case "current_population": colLocation[0] = i; break;
				case "max_population": colLocation[1] = i; break;
				case "protection": colLocation[2] = i; break;
				case "overbuilt": colLocation[3] = i; break;
				case "overbuilt_percent": colLocation[4] = i; break;
				case "solar_collectors": colLocation[5] = i; break;
				case "fission_reactors": colLocation[6] = i; break;
				case "mineral_plants": colLocation[7] = i; break;
				case "crystal_labs": colLocation[8] = i; break;
				case "refinement_stations": colLocation[9] = i; break;
				case "cities": colLocation[10] = i; break;
				case "research_centers": colLocation[11] = i; break;
				case "defense_sats": colLocation[12] = i; break;
				case "shield_networks": colLocation[13] = i; break;
				case "portal": colLocation[14] = i; break;
				case "portal_under_construction": colLocation[15] = i; break;
				case "total_buildings": colLocation[16] = i; break; 
				case "buildings_under_construction": colLocation[17] = i; break;
				case "id": colLocation[18] = i; break;
				case "size": colLocation[19] = i; break;
				case "x": colLocation[20] = i; break;
				case "y": colLocation[21] = i; break;
				case "bonus_solar": colLocation[22] = i; break;
				case "bonus_mineral": colLocation[23] = i; break;
				case "bonus_crystal": colLocation[24] = i; break;
				case "bonus_ectrolium": colLocation[25] = i; break;
				case "bonus_fission": colLocation[26] = i; break;
				default:;
			}
		}
		
		//execute stored procedure -- update planets population
		String runSP = "CALL updatePlanets(?, ?, ?); ";
		
		CallableStatement callableStatement = connection.prepareCall(runSP); 
		callableStatement.setDouble(1, (1.00 + 0.01 * userIntValues.get("research_percent_population"))); //research factor
		callableStatement.setDouble(2, race_info.get("pop_growth")); //race bonus for pop growth

		callableStatement.setInt(3, userID); //user id
		callableStatement.executeUpdate();

		while(resultSet.next()){
			num_planets++;
			
			//put results into an array, use objects because the results have different types
			Object[] rowValues = new Object[colNumber];
			for (int i = 0; i < colNumber; i++) {
				 rowValues[i] = HelperFunctions.getValueByType(i + 1, colTypes[i], resultSet);
			}
			
			int planetID = (int)rowValues[colLocation[18]]; 

			HashMap<String, Integer> buildgsBuiltFromJobs = null;

			if(jobs.containsKey(planetID))
				buildgsBuiltFromJobs = jobs.get(planetID);
			else
				buildgsBuiltFromJobs = new HashMap<>();
					
			//add planets population to total population
			population += (int)rowValues[colLocation[0]];

			//update portal coverage
			int portalCoverage = 0;
			if((boolean)rowValues[colLocation[14]] == true)
				portalCoverage = 100;
				
			else{
				if(portals.size() == 0)
					portalCoverage = 0;
				else
					portalCoverage = (int)(100.0 * HelperFunctions.battlePortalCalc((int)rowValues[colLocation[20]], (int)rowValues[colLocation[21]], 
												portals, userIntValues.get("research_percent_portals")) );
			}

			//update planets buildings
			int solar_collectors = (int)rowValues[colLocation[5]] + buildgsBuiltFromJobs.getOrDefault("solar_collectors",0);
			int fission_reactors = (int)rowValues[colLocation[6]] + buildgsBuiltFromJobs.getOrDefault("fission_reactors",0);
			int mineral_plants = (int)rowValues[colLocation[7]] + buildgsBuiltFromJobs.getOrDefault("mineral_plants",0);
			int crystal_labs = (int)rowValues[colLocation[8]] + buildgsBuiltFromJobs.getOrDefault("crystal_labs",0);
			int refinement_stations = (int)rowValues[colLocation[9]] + buildgsBuiltFromJobs.getOrDefault("refinement_stations",0);
			int cities = (int)rowValues[colLocation[10]] + buildgsBuiltFromJobs.getOrDefault("cities",0);
			int research_centers = (int)rowValues[colLocation[11]] + buildgsBuiltFromJobs.getOrDefault("research_centers",0);
			int defense_sats = (int)rowValues[colLocation[12]] + buildgsBuiltFromJobs.getOrDefault("defense_sats",0);
			int shield_networks = (int)rowValues[colLocation[13]] + buildgsBuiltFromJobs.getOrDefault("shield_networks",0);
			
			boolean portal = (boolean)rowValues[colLocation[14]] || (buildgsBuiltFromJobs.getOrDefault("portal",0) == 1 ? true : false);
			
			totalBuildingsBuilt[0] += buildgsBuiltFromJobs.getOrDefault("solar_collectors",0);
			totalBuildingsBuilt[1] += buildgsBuiltFromJobs.getOrDefault("fission_reactors",0);
			totalBuildingsBuilt[2] += buildgsBuiltFromJobs.getOrDefault("mineral_plants",0);
			totalBuildingsBuilt[3] += buildgsBuiltFromJobs.getOrDefault("crystal_labs",0);
			totalBuildingsBuilt[4] += buildgsBuiltFromJobs.getOrDefault("refinement_stations",0);
			totalBuildingsBuilt[5] += buildgsBuiltFromJobs.getOrDefault("cities",0);
			totalBuildingsBuilt[6] += buildgsBuiltFromJobs.getOrDefault("research_centers",0);
			totalBuildingsBuilt[7] +=  buildgsBuiltFromJobs.getOrDefault("defense_sats",0);
			totalBuildingsBuilt[8] += buildgsBuiltFromJobs.getOrDefault("shield_networks",0);
			totalBuildingsBuilt[9] += buildgsBuiltFromJobs.getOrDefault("portal",0);
				
			// Add buildings to running total for player
			totalBuildings[0] += solar_collectors;
			totalBuildings[1] += fission_reactors;
			totalBuildings[2] += mineral_plants;
			totalBuildings[3] += crystal_labs;
			totalBuildings[4] += refinement_stations;
			totalBuildings[5] += cities;
			totalBuildings[6] += research_centers;
			totalBuildings[7] += defense_sats;
			totalBuildings[8] += shield_networks;
			totalBuildings[9] += (portal == true? 1 : 0);

			int total_buildings = solar_collectors + 
				fission_reactors + mineral_plants +
				crystal_labs + refinement_stations +
				cities + research_centers +
				defense_sats + shield_networks +
				(portal == true? 1 : 0);
			
			networth += total_buildings * networth_per_building;
			networth += (int)rowValues[colLocation[22]] * 1.25;
			networth += (int)rowValues[colLocation[23]] * 1.45;
			networth += (int)rowValues[colLocation[24]] * 2.25;
			networth += (int)rowValues[colLocation[25]] * 1.65;
			networth += (int)rowValues[colLocation[26]] * 5.0;
			networth += (int)rowValues[colLocation[19]] * 1.75; //size
			int buildingsUnderConstr = (int)rowValues[colLocation[17]] - (total_buildings - (int)rowValues[colLocation[16]]); //total new - total old, change it!! might not work when raze
			buildingsUnderConstr = Math.max(0 , buildingsUnderConstr);
			
			//update player production
			cmdTickProduction_solar += (building_production_solar * solar_collectors) * (1 + (int)rowValues[colLocation[22]] /100.0);
			cmdTickProduction_fission += (building_production_fission  * fission_reactors) * (1 + (int)rowValues[colLocation[26]] /100.0);
			cmdTickProduction_mineral += (building_production_mineral   * mineral_plants) * (1 + (int)rowValues[colLocation[23]] /100.0);
			cmdTickProduction_crystal += (building_production_crystal    * crystal_labs) * (1 + (int)rowValues[colLocation[24]]/100.0);
			cmdTickProduction_ectrolium += (building_production_ectrolium    * refinement_stations) * (1 + (int)rowValues[colLocation[25]]/100.0);
			//cmdTickProduction_cities += building_production_cities * cities;
			cmdTickProduction_research += building_production_research * research_centers;
			
			double overbuilt = (double)(HelperFunctions.calc_overbuild((int)rowValues[colLocation[19]], total_buildings + buildingsUnderConstr));
			double overbuilt_percent = (double)((overbuilt-1.0)*100); 

			//add planet only if something has changed
			if (//current_population != (int)rowValues[colLocation[0]] ||
				//max_population != (int)rowValues[colLocation[1]] ||
				portalCoverage != (int)rowValues[colLocation[2]] ||
				overbuilt != (double)rowValues[colLocation[3]] ||
				overbuilt_percent != (double)rowValues[colLocation[4]] ||
				solar_collectors != (int)rowValues[colLocation[5]] ||
				fission_reactors != (int)rowValues[colLocation[6]] ||
				mineral_plants != (int)rowValues[colLocation[7]] ||
				crystal_labs != (int)rowValues[colLocation[8]] ||
				refinement_stations != (int)rowValues[colLocation[9]] ||
				cities != (int)rowValues[colLocation[10]] ||
				research_centers != (int)rowValues[colLocation[11]] ||
				defense_sats != (int)rowValues[colLocation[12]] ||
				shield_networks != (int)rowValues[colLocation[13]] ||
				portal != (boolean)rowValues[colLocation[14]] ||
				total_buildings != (int)rowValues[colLocation[16]] ||
				buildingsUnderConstr != (int)rowValues[colLocation[17]] 
			)
			{
				//System.out.println("updating planet nr:" + planetID);
				//planetsUpdateStatement.setInt(1, current_population);
				//planetsUpdateStatement.setInt(2, max_population);
				planetsUpdateStatement.setInt(1, portalCoverage);
				planetsUpdateStatement.setDouble(2, overbuilt);
				planetsUpdateStatement.setDouble(3, overbuilt_percent);
				planetsUpdateStatement.setInt(4, solar_collectors );
				planetsUpdateStatement.setInt(5, fission_reactors );
				planetsUpdateStatement.setInt(6, mineral_plants);
				planetsUpdateStatement.setInt(7, crystal_labs);
				planetsUpdateStatement.setInt(8, refinement_stations);
				planetsUpdateStatement.setInt(9, cities);
				planetsUpdateStatement.setInt(10, research_centers);
				planetsUpdateStatement.setInt(11, defense_sats);
				planetsUpdateStatement.setInt(12, shield_networks);	
				planetsUpdateStatement.setBoolean(13, portal);	
				if (portal)
					planetsUpdateStatement.setBoolean(14, false);	
				else
					planetsUpdateStatement.setBoolean(14, resultSet.getBoolean("portal_under_construction"));	//keep the initial value
				planetsUpdateStatement.setInt(15, total_buildings);
				planetsUpdateStatement.setInt(16, buildingsUnderConstr);
				planetsUpdateStatement.setInt(17, planetID);

				planetsUpdateStatement.addBatch();
			}
		}
		
		//add building news if something was actually built
		int totalBuilt = 0;
		for(int i = 0; i < totalBuildingsBuilt.length; i++){
			totalBuilt += totalBuildingsBuilt[i];
		}
		if (totalBuilt != 0 ){
			userStatusUpdateStatement.setInt(56, 1);
			String builtBuildings = "These building constructions were finished : \n";
			for (int i = 0; i < building_names.length; i++){
				if (totalBuildingsBuilt[i] != 0 )
					builtBuildings += building_names[i] + ": " + totalBuildingsBuilt[i] + "\n";
			}
			updateNews.createBuildingNews(userID, empireID, builtBuildings);
		}
	}
	
	public void UpdatePlanetsExecute() throws Exception{
		planetsUpdateStatement.executeBatch();
	}

	public long getNetworth(){
		return networth;
	}
	
	public int getNumPlanets(){
		return num_planets;
	}
	
	public long getPopulation(){
		return population;
	}
	
	public int getResearchProduction(){
		return cmdTickProduction_research;
	}
	
	public long getEnergyProduction(int resource){
		switch(resource){
			case(0): //solar
				return cmdTickProduction_solar;
			case(1): //fission
				return cmdTickProduction_fission;
		}
		return 0;
	}
	
	public int getResourceProduction(int resource){
		switch(resource){
			case(0): //mineral
				return cmdTickProduction_mineral;
			case(1): //crystals
				return cmdTickProduction_crystal;
			case(2): //ectrolium
				return cmdTickProduction_ectrolium;
		}
		return 0;
	}
	
	public int getTotalBuildings(int resource){
		return totalBuildings[resource];
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
	
}