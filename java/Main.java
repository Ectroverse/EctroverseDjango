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
 		statTime = System.nanoTime();
		ResultSet resultSet = statement.executeQuery("SELECT * FROM app_userstatus");
		resultTime = System.nanoTime();
		//System.out.println(resultSet);
		 String compiledQuery = "INSERT INTO app_userstatus(id, fleet_readiness)" +
                " VALUES" + "(?, ?)";
        	preparedStatement = connection.prepareStatement(compiledQuery);
		 
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
		System.out.println(Arrays.toString(inserted));
	}
	catch (Exception e) {
            System.out.println("exception " +  e.getMessage());
        }
	     
	long endTime = System.nanoTime();
    	System.out.println("connection time " + (double)(endTime - executeBatchTime)/1_000_000_000.0);
	System.out.println((double)(endTime-startTime)/1_000_000_000.0);
    }
}
