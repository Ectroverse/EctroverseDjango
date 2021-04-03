package org.ectroverse.processtick;

import java.sql.*;
import java.util.*;
import static org.ectroverse.processtick.Constants.*;

class UpdateNews {
	
	private final String buildingNewsUpdateQuery = "INSERT INTO app_news " +
	" ( user1_id, empire1_id, news_type, date_and_time, is_personal_news, " + 
	" is_empire_news, is_read, tick_number, extra_info ) " +
	" SELECT  ?, ?, 'BB',  ?, true, false, false, ?, ?  ";
	PreparedStatement buildingNewsUpdateStatement; 
	
	private Connection connection;
	private Statement statement;
	
	public UpdateNews(Connection connection) throws Exception{    
		this.connection = connection;
		statement = connection.createStatement();
		buildingNewsUpdateStatement = connection.prepareStatement(buildingNewsUpdateQuery); 
	}
	
	public void createBuildingNews(int userID, int empireId, int tickNumber, String builtBuildings) throws Exception{
		java.util.Date utilDate = new java.util.Date();
		java.sql.Timestamp sqlTS = new java.sql.Timestamp(utilDate.getTime());

		buildingNewsUpdateStatement.setInt(1, userID);
		buildingNewsUpdateStatement.setInt(2, empireId);
		buildingNewsUpdateStatement.setTimestamp(3, sqlTS);
		buildingNewsUpdateStatement.setInt(4, tickNumber);
		buildingNewsUpdateStatement.setString(5, builtBuildings);
		buildingNewsUpdateStatement.addBatch();				
	}
	
	public void executeBuildingNews() throws Exception{
		buildingNewsUpdateStatement.executeBatch();
	}
}