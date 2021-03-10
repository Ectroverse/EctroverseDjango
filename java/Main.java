import java.sql.*;

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
		ResultSet users = statement.executeQuery("SELECT * FROM app_userstatus");
		 
		 
		 String compiledQuery2 = "UPDATE \"PLANET\" SET max_population = ? "+
		  " current_population = ?" +
		  " protection = ?" +
		 "WHERE id = ?" ;
		 PreparedStatement preparedStatement = con.prepareStatement(compiledQuery2); //mass update, much faster
		 
		 //loop over users
		while(users.next()){
			int userID = users.getInt("user_id");
			if(users.getInt("networth") == 0){
				System.out.println("networth was null");
				continue;
			}
			
			//check if the players empire is null
			users.getInt("empire_id");
		 	if (users.wasNull()){
				System.out.println("empire was null");
		   		continue;
			}
			   
			   
		/*	ResultSet planets = statement.executeQuery("SELECT * FROM \"PLANET\" WHERE id = " + userID);
			
			
			//loop over planets of each user
			while(planets.next()){
				int id = planets.getInt("id");
				int max_population = planets.getInt("max_population");
				int size = planets.getInt("size");
				int total = size * 4 ;

				preparedStatement.setInt(4, id);
				preparedStatement.setInt(3, 2435345);
				preparedStatement.setInt(2, 345);
				preparedStatement.setInt(1, total+2);
				preparedStatement.addBatch();

				//# Update Population
			        planet.max_population = (planet.size * population_size_factor)
				planet.max_population += (planet.cities * building_production_cities)
				planet.max_population *= (1.00 + 0.01 * status.research_percent_population)
		
			}*/
		}
		 

		 
		
		long t0 = System.nanoTime();
		
		long t1 = System.nanoTime();
		preparedStatement.executeBatch();
		long t2= System.nanoTime();
		System.out.println("planets execution 1: " + (double)(t1 - t0)/1_000_000_000.0);
		System.out.println("planets execution 2: " + (double)(t2 - t1)/1_000_000_000.0);
	}
	catch (Exception e) {
            System.out.println("exception " +  e.getMessage());
        }
	     
	long endTime = System.nanoTime();
	
    	System.out.println("connection time " + (double)(connectionTime - startTime)/1_000_000_000.0);
    	
    	System.out.println((double)(endTime-startTime)/1_000_000_000.0);
    }
}
