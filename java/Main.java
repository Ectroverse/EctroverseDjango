import java.sql.*;

public class Main
{


     public static void main(String[] args) {
	long startTime = System.nanoTime();
	long connectionTime = 0;
	long statTime = 0;
	long resultTime = 0;
	long printTime = 0;
         try {
	 	//long startTime = System.nanoTime();
		Connection con = DriverManager.getConnection("jdbc:postgresql://ectroversedjango_db_1:5432/djangodatabase", "dbadmin", "pass");
		connectionTime = System.nanoTime();
		Statement statement = con.createStatement();
 		statTime = System.nanoTime();
		ResultSet resultSet = statement.executeQuery("SELECT * FROM app_userstatus");
		resultTime = System.nanoTime();
		//System.out.println(resultSet);
		while(resultSet.next()){
			String name = resultSet.getString("user_name");
			String race = resultSet.getString("race");
			//int age = resultSet.getInt("user");
		System.out.println(name + " " + race + " ");

		
		}
		printTime = System.nanoTime();
	}
	catch (Exception e) {
            System.out.println("exception " +  e.getMessage());
        }
	long endTime = System.nanoTime();
    	System.out.println("connection time " + (double)(connectionTime - startTime)/1_000_000_000.0);
 	System.out.println("stat time " + (double)(endTime- statTime)/1_000_000_000.0);
	System.out.println("result time " + (double)(endTime- resultTime)/1_000_000_000.0);
	System.out.println("print time " + (double)(endTime- resultTime)/1_000_000_000.0);
	System.out.println((double)(endTime-startTime)/1_000_000_000.0);
    }
}
