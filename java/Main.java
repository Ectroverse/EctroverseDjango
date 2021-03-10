import java.sql.*;
import java.util.*;

public class Main
{


    public static void main(String[] args) {
	//some constants temporarily written here, fetch them from app/constants.py later
	int population_size_factor  = 20;
	int energy_decay_factor = 0.005;
	int crystal_decay_factor = 0.02;
	int upkeep_solar_collectors = 0.0;
	int upkeep_fission_reactors = 20.0;
	int upkeep_mineral_plants = 2.0;
	int upkeep_crystal_labs = 2.0;
	int upkeep_refinement_stations = 2.0;
	int upkeep_cities = 4.0;
	int upkeep_research_centers = 1.0;
	int upkeep_defense_sats = 4.0;
	int upkeep_shield_networks = 16.0;
	int networth_per_building = 8;
	int building_production_solar = 12;
	int building_production_fission = 40;
	int building_production_mineral = 1;
	int building_production_crystal = 1;
	int building_production_ectrolium = 1;
	int building_production_cities = 1000;
	int building_production_research = 6;
	float [] unit_upkeep = {2.0, 1.6, 3.2, 12.0, 18.0, 0.4, 0.6, 2.8, 0.0, 0.8, 0.8, 2.4, 60.0};
	HashMap<String,HashMap<String, double>> race_info_list = new HashMap<>(); 
	HashMap<String, double> harks = new HashMap<>();
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
	race_info_list.put("Harks",harks);
	HashMap<String, double> manticarias = new HashMap<>();
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
	race_info_list.put("Manticarias",manticarias);  
	HashMap<String, double> foohons = new HashMap<>();
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
	race_info_list.put("Foohons",foohons);  
	HashMap<String, double> spacebournes = new HashMap<>();
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
	race_info_list.put("Spacebournes",spacebournes);  
	HashMap<String, double> dreamweavers = new HashMap<>();
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
	race_info_list.put("Dreamweavers",dreamweavers);  
	HashMap<String, double> wookiees = new HashMap<>();
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
	race_info_list.put("Wookiees",wookiees);  

		
	long startTime = System.nanoTime();
	long connectionTime = 0;
	long statTime = 0;
	long resultTime = 0;
	long executeBatchTime = 0;
         try {
	 	//long startTime = System.nanoTime();
		Connection con = DriverManager.getConnection("jdbc:postgresql://ectroversedjango_db_1:5432/djangodatabase", "dbadmin", "pass");
		connectionTime = System.nanoTime();
		
		Statement statement = con.createStatement();
 		/*statTime = System.nanoTime();
		ResultSet resultSet = statement.executeQuery("SELECT * FROM app_userstatus");
		resultTime = System.nanoTime();*/
		
		//System.out.println(resultSet);
		 /*String compiledQuery = "INSERT INTO app_userstatus(id, fleet_readiness)" +
                " VALUES" + "(?, ?)";
        	PreparedStatement preparedStatement = connection.prepareStatement(compiledQuery);
		 
		while(resultSet.next()){
			int id = resultSet.getInt("id")
			int fleet_readiness = resultSet.getInt("fleet_readiness")
				
			System.out.println(id);
			preparedStatement.setInt(1, id);
			preparedStatement.setInt(2, fleet_readiness+2);
			preparedStatement.addBatch();
		}
		executeBatchTime = System.nanoTime();
		int[] inserted = preparedStatement.executeBatch();
		System.out.println(Arrays.toString(inserted));*/
		ResultSet resultSet = statement.executeQuery("SELECT * FROM app_userstatus");
	   	ResultSetMetaData rsmd = resultSet.getMetaData();
	   	ArrayList<String []> columns = new ArrayList<>(rsmd.getColumnCount());
	  	for(int i = 1; i <= rsmd.getColumnCount(); i++){
			String [] arr = new String[2];
			arr[0] = rsmd.getColumnName(i);
			arr[1] = rsmd.getColumnClassName(i);
			System.out.println(Arrays.toString(arr));
			columns.add(arr);
		    }
		 System.out.println(columns);
		 
		 String planetStatusUpdateQuery = "UPDATE \"PLANET\"  SET" +
		  " max_population = ? "+
		  " current_population = ?" +
		  " protection = ?" +
		 "WHERE id = ?" ;
		  PreparedStatement planetsUpdateStatement = con.prepareStatement(planetStatusUpdateQuery); //mass update, much faster
		 
		 String userStatusUpdateQuery = "UPDATE app_userstatus SET "+
			" fleet_readiness  = ?" +  //1
			" psychic_readiness  = ?" + //2
			" agent_readiness  = ?" + //3
			" population   = ?" + //4
			" total_solar_collectors  = ?" + //5
			" total_fission_reactors  = ?" + //6
			" total_mineral_plants  = ?" + //7
			" total_crystal_labs  = ?" + //8
			" total_refinement_stations   = ?" + //9
			" total_cities  = ?" + //10
			" total_research_centers   = ?" + //11
			" total_defense_sats    = ?" + //12
			" total_shield_networks   = ?" + //13
			" total_portals  = ?" + //14
			" agent_readiness  = ?" + //15
			" population   = ?" + //16
			" research_points_military   = ?" + //17
			" research_points_construction   = ?" + //18
			" research_points_tech   = ?" + //19
			" research_points_energy    = ?" + //20
			" research_points_population   = ?" + //21
			" research_points_culture    = ?" + //22
			" research_points_operations   = ?" + //23
			" research_points_portals    = ?" + //24
			" current_research_funding    = ?" + //25
			" research_percent_military   = ?" + //26
			" research_percent_construction    = ?" + //27
			" research_percent_tech            = ?" + //28
			" research_percent_energy          = ?" + //29
			" research_percent_population      = ?" + //30
			" research_percent_culture         = ?" + //31
			" research_percent_operations      = ?" + //32
			" research_percent_portals         = ?" + //33
			" energy_production          = ?" + //34
			" energy_decay          = ?" + //35
			" buildings_upkeep          = ?" + //36
			" units_upkeep          = ?" + //37
			" population_upkeep_reduction           = ?" + //38
			" portals_upkeep           = ?" + //39
			" mineral_production           = ?" + //40
			" crystal_production            = ?" + //41
			" crystal_decay            = ?" + //42
			" ectrolium_production             = ?" + //43
			" energy_interest              = ?" + //44
			" mineral_interest              = ?" + //45
			" crystal_interest              = ?" + //46
			" ectrolium_interest              = ?" + //47
			" energy                  = ?" + //48
			" minerals                = ?" + //49
			" crystals                = ?" + //50
			" ectrolium               = ?" + //51
			" networth                = ?" + //52
			 
			"WHERE id = ?" ; //53 wow what a long string :P
		 PreparedStatement userStatusUpdateStatement = con.prepareStatement(userStatusUpdateQuery); //mass update, much faster

		 ArrayList<HashMap<String, Integer>> usersInt = new ArrayList<>();
		 ArrayList<HashMap<String, Long>> usersLong = new ArrayList<>();
		 //loop over users
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
			HashMap<String,Integer> rowInt = new HashMap<>(columns.size());
			HashMap<String,Long> rowLong = new HashMap<>(columns.size());
			for(String[] col : columns) {
				if(col[1].equals("java.lang.Integer"))
			    		rowInt.put(col[0], resultSet.getInt(col[0]));
				else if(col[1].equals("java.lang.Long"))
			    		rowLong.put(col[0], resultSet.getLong(col[0]));
			}
			System.out.println(rowInt);
			System.out.println(rowLong);
			usersInt.add(rowInt);
			usersLong.add(rowLong);
		}
		 
		 
		
		 for(int i = 0; i < usersInt.size(); i++){
			HashMap<String,Integer> rowInt = usersInt.get(i);
			HashMap<String,Long> rowLong  = usersLong.get(i);
				
			int userID = rowInt.get("user_id");
			
			int fr = Math.min(rowInt.get(fleet_readiness)+2, rowInt.get(fleet_readiness_max));
			userStatusUpdateStatement.setInt(1, fr); 
			int pr = Math.min(rowInt.get(psychic_readiness)+2, rowInt.get(psychic_readiness_max));
			userStatusUpdateStatement.setInt(2, pr); 
			int ar = Math.min(rowInt.get(agent_readiness)+2, rowInt.get(agent_readiness_max));
			userStatusUpdateStatement.setInt(2, ar); 
			 
			 /*for job in Construction.objects.filter(user=status.user.id):
                job.ticks_remaining -= 1
                if job.ticks_remaining <= 0:
                    if job.building_type == 'SC':
                        job.planet.solar_collectors += job.n
                    if job.building_type == 'FR':
                        job.planet.fission_reactors += job.n
                    if job.building_type == 'MP':
                        job.planet.mineral_plants += job.n
                    if job.building_type == 'CL':
                        job.planet.crystal_labs += job.n
                    if job.building_type == 'RS':
                        job.planet.refinement_stations += job.n
                    if job.building_type == 'CT':
                        job.planet.cities += job.n
                    if job.building_type == 'RC':
                        job.planet.research_centers += job.n
                    if job.building_type == 'DS':
                        job.planet.defense_sats += job.n
                    if job.building_type == 'SN':
                        job.planet.shield_networks += job.n
                    if job.building_type == 'PL':
                        job.planet.portal = True
                        job.planet.portal_under_construction = False
                    job.planet.buildings_under_construction -= job.n
                    job.planet.save()

                    # TODO ADD IT TO THE NEWS!

                    job.delete()
                else:
                    job.save()*/
			 
		/*
		   # Repeat for units
            main_fleet = Fleet.objects.get(owner=status.user.id, main_fleet=True) # should only ever be 1
            for job in UnitConstruction.objects.filter(user=status.user.id):
                job.ticks_remaining -= 1
                if job.ticks_remaining <= 0:
                    setattr(main_fleet, job.unit_type, getattr(main_fleet, job.unit_type) + job.n)
                    main_fleet.save()
                    # TODO ADD IT TO THE NEWS!
                    job.delete()
                else:
                    job.save()*/
			 
			 
			 
			ResultSet resultSet = statement.executeQuery("SELECT * FROM \"PLANET\" WHERE id = " + userID);
			 
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
			while(planets.next()){
				num_planets++;
				int max_population = (resultSet.getInt(size) * population_size_factor);
				max_population += (resultSet.getInt(cities) * building_production_cities);
				max_population *= (1.00 + 0.01 * rowInt.get("research_percent_population"));
				//Update Population
				
		
			}
		}
		 

		 
		
		/*long t0 = System.nanoTime();
		
		long t1 = System.nanoTime();
		preparedStatement.executeBatch();
		long t2= System.nanoTime();
		System.out.println("planets execution 1: " + (double)(t1 - t0)/1_000_000_000.0);
		System.out.println("planets execution 2: " + (double)(t2 - t1)/1_000_000_000.0);*/
	}
	catch (Exception e) {
            System.out.println("exception " +  e.getMessage());
        }
	     
	long endTime = System.nanoTime();
	
    	System.out.println("connection time " + (double)(connectionTime - startTime)/1_000_000_000.0);
    	
    	System.out.println((double)(endTime-startTime)/1_000_000_000.0);
    }
}
