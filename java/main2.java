import java.util.*;
import java.time.*;
import java.util.concurrent.*;
import java.sql.*;
import java.util.*;

public class main2
{

	

	public static void main(String[] args) {
		int building_production_cities = 1000;
		int population_size_factor  = 20;
		

		
			String createSP = "CREATE OR REPLACE PROCEDURE updatePlanets( "
							+ " p_id IN \"PLANET\".ID%TYPE, pop_rc DOUBLE PRECISION, race_pop_growth DOUBLE PRECISION, user_id IN \"PLANET\".ID%TYPE)"
							+ "LANGUAGE SQL"
							+ " AS $$"
							+ " UPDATE \"PLANET\" SET max_population = (" + 
							+ building_production_cities + " * cities +  size * " + population_size_factor + ") *pop_rc WHERE owner_id = user_id;" 
							+ " UPDATE \"PLANET\" SET current_population = "
							+ "least(current_population * pop_rc * race_pop_growth, max_population) WHERE owner_id = user_id;" 
							+ " $$;";
				
			String runSP = "CALL updatePlanets(?, ?, ?, ?); ";
		
			Connection conn = null;
			try{
				conn = DriverManager.getConnection("jdbc:postgresql://ectroversedjango_db_1:5432/djangodatabase", "dbadmin", "admin12345");


				
				Statement statement = conn.createStatement();
				
				String dropProcedure ="DROP FUNCTION IF EXISTS updatePlanets(integer, double);";
				statement.execute(dropProcedure);
				
				CallableStatement callableStatement = conn.prepareCall(runSP); 

				// create or replace stored procedure
				statement.execute(createSP);

				callableStatement.setInt(1, 1565);
				callableStatement.setDouble(2, 1.5);
				callableStatement.setDouble(3, 1.1);
				callableStatement.setInt(4, 2);
				/*callableStatement.registerOutParameter(2, java.sql.Types.VARCHAR);
				callableStatement.registerOutParameter(3, Types.DECIMAL);
				callableStatement.registerOutParameter(4, java.sql.Types.DATE);*/

				// run it
				callableStatement.executeUpdate();

				/*String name = callableStatement.getString(2);
				BigDecimal salary = callableStatement.getBigDecimal(3);
				Timestamp createdDate = callableStatement.getTimestamp(4);*/
				
				//int size = callableStatement.getInt(1);
				//System.out.println(size);

			}
			catch (Exception e) {

				System.out.println("exception " +  e.getMessage());
				System.out.println("Connection with postgres DB not established, aborting." );
				System.exit(0);
			}
			
			
			

				
			
	}
}