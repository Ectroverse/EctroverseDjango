import java.sql.*;
import java.util.*;

public class Main
{


    public static void main(String[] args) {
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
	   	ArrayList<String> columns = new ArrayList<>(rsmd.getColumnCount());
	  	for(int i = 0; i < rsmd.getColumnCount(); i++){
			columns.add(rsmd.getColumnName(i));
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

		 ArrayList<HashMap<Integer, Integer>> users = new ArrayList<>();
		 //loop over users
		while(resultSet.next()){
			int userID = resultSet.getInt("user_id");
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
			HashMap<String,String> row = new HashMap<String, String>(columns.size());
			for(String col : columns) {
			    row.put(col, resultSet.getInt(col));
			}
			System.out.println(row);
			users.add(row);
		}
		 
		 
		
		 /*for(Integer user: users){	   
			ResultSet planets = statement.executeQuery("SELECT * FROM \"PLANET\" WHERE id = " + userID);
			
			
			//loop over planets of each user
			while(planets.next()){
				/*int id = planets.getInt("id");
				int max_population = planets.getInt("max_population");
				int size = planets.getInt("size");
				int total = size * 4 ;

				preparedStatement.setInt(4, id);
				preparedStatement.setInt(3, 2435345);
				preparedStatement.setInt(2, 345);
				preparedStatement.setInt(1, total+2);
				preparedStatement.addBatch();*/

				//# Update Population
			        /*planet.max_population = (planet.size * population_size_factor)
				planet.max_population += (planet.cities * building_production_cities)
				planet.max_population *= (1.00 + 0.01 * status.research_percent_population)
		
			}
		}*/
		 

		 
		
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
