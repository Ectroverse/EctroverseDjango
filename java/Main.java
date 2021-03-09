import java.sql.*;

public class Main
{


     public static void main(String[] args) {

         try {
	 	Connection con = DriverManager.getConnection("jdbc:postgresql://ectroversedjango_db_1:5432/djangodatabase", "dbadmin", "pass");
		Statement statement = con.createStatement();
 		ResultSet resultSet = statement.executeQuery("SELECT * FROM app_userstatus");
		System.out.println(resultSet);
		while(resultSet.next()){
			String name = resultSet.getString("user_name");
			String race = resultSet.getString("race");
			//int age = resultSet.getInt("user");
			System.out.println(name + " " + race + " ");

		
		}

	}
	catch (Exception e) {
            System.out.println("exception " +  e.getMessage());
        }
    }
}
