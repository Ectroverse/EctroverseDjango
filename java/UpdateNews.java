package org.ectroverse.processtick;

import java.sql.*;
import java.util.*;
import static org.ectroverse.processtick.Constants.*;

public class UpdateNews {
	
	private final String buildingNewsUpdateQuery = "INSERT INTO app_news " +
	" ( user1_id, empire1_id, news_type, date_and_time, is_personal_news, " + 
	" is_empire_news, is_read, tick_number, extra_info ) " +
	" SELECT  ?, ?, 'BB',  ?, true, false, false, ?, ?  ";
	private PreparedStatement buildingNewsUpdateStatement; 
	
	private final String fleetsNewsUpdateQuery = "INSERT INTO app_news " +
	" ( user1_id, empire1_id, news_type, date_and_time, is_personal_news, " + 
	" is_empire_news, is_read, tick_number, extra_info ) " +
	" SELECT  ?, ?, 'UB',  ?, true, false, false, ?, ?  ";
	private PreparedStatement fleetsNewsUpdateStatement;
	
	private final String fleetsReturnNewsUpdateQuery = "INSERT INTO app_news " +
	" ( user1_id, empire1_id, news_type, date_and_time, is_personal_news, " + 
	" is_empire_news, is_read, tick_number, extra_info ) " +
	" SELECT  ?, ?, 'FJ',  ?, true, false, false, ?, ?  ";
	private PreparedStatement fleetsReturnNewsUpdateStatement; 
	
	private final String fleetsMergeNewsUpdateQuery = "INSERT INTO app_news " +
	" ( user1_id, empire1_id, news_type, date_and_time, is_personal_news, " + 
	" is_empire_news, is_read, tick_number, extra_info ) " +
	" SELECT  ?, ?, 'FM',  ?, true, false, false, ?, ?  ";
	private PreparedStatement fleetsMergeNewsUpdateStatement; 
	
	private final String fleetsStationNewsUpdateQuery = "INSERT INTO app_news " +
	" ( user1_id, empire1_id, news_type, date_and_time, is_personal_news, " + 
	" is_empire_news, is_read, tick_number, fleet1, extra_info ) " +
	" SELECT  ?, ?, ?,  ?, true, false, false, ?, ?, ?  ";
	private PreparedStatement fleetsStationNewsUpdateStatement; 
	
	private Connection connection;
	private Statement statement;
	private int tickNumber;
	
	public UpdateNews(Connection connection, int tickNumber) throws Exception{    
		this.connection = connection;
		statement = connection.createStatement();
		buildingNewsUpdateStatement = connection.prepareStatement(buildingNewsUpdateQuery); 
		fleetsNewsUpdateStatement = connection.prepareStatement(fleetsNewsUpdateQuery);
		fleetsReturnNewsUpdateStatement = connection.prepareStatement(fleetsReturnNewsUpdateQuery); 
		fleetsMergeNewsUpdateStatement = connection.prepareStatement(fleetsMergeNewsUpdateQuery); 
		fleetsStationNewsUpdateStatement = connection.prepareStatement(fleetsStationNewsUpdateQuery); 
		this.tickNumber = tickNumber;
	}
	
	public void createBuildingNews(int userID, int empireId, String builtBuildings) throws Exception{
		java.util.Date utilDate = new java.util.Date();
		java.sql.Timestamp sqlTS = new java.sql.Timestamp(utilDate.getTime());

		buildingNewsUpdateStatement.setInt(1, userID);
		buildingNewsUpdateStatement.setInt(2, empireId);
		buildingNewsUpdateStatement.setTimestamp(3, sqlTS);
		buildingNewsUpdateStatement.setInt(4, tickNumber);
		buildingNewsUpdateStatement.setString(5, builtBuildings);
		buildingNewsUpdateStatement.addBatch();				
	}
	
	public void createfleetBuildingNews(int userID, int empireId, HashMap<String, Integer> unitsBuilt) throws Exception{
				
		java.util.Date utilDate = new java.util.Date();
		java.sql.Timestamp sqlTS = new java.sql.Timestamp(utilDate.getTime());
		
		fleetsNewsUpdateStatement.setInt(1, userID);
		fleetsNewsUpdateStatement.setInt(2, empireId);
		fleetsNewsUpdateStatement.setTimestamp(3, sqlTS);
		fleetsNewsUpdateStatement.setInt(4, tickNumber);
		
		String builtFleets = "These units constructions were finished : ";
		for(int i = 0; i < unit_names.length; i++){
			if ( unitsBuilt.getOrDefault(unit_names[i],0) > 0)
				builtFleets += "\n " + unit_labels[i] + " " +  unitsBuilt.getOrDefault(unit_names[i],0);
		}

		fleetsNewsUpdateStatement.setString(5, builtFleets);
		fleetsNewsUpdateStatement.addBatch();
		
	}
	
	public void createfleetReturnNews(int userID, int empireId, long [] returnFleets) throws Exception{
		java.util.Date utilDate = new java.util.Date();
		java.sql.Timestamp sqlTS = new java.sql.Timestamp(utilDate.getTime());
		fleetsReturnNewsUpdateStatement.setInt(1, userID);
		fleetsReturnNewsUpdateStatement.setInt(2, empireId);
		fleetsReturnNewsUpdateStatement.setTimestamp(3, sqlTS);
		fleetsReturnNewsUpdateStatement.setInt(4, tickNumber);

		String builtFleets = "These units have joined main fleet : ";
		for(int i = 0; i < unit_names.length; i++){
			if (returnFleets[i] > 0)
				builtFleets += "\n " + unit_labels[i] + " " +  returnFleets[i];
		}
		
		fleetsReturnNewsUpdateStatement.setString(5, builtFleets);
		fleetsReturnNewsUpdateStatement.addBatch();
	}
	
	public void createfleetMergeNews(int userID, int empireId, long [] fleets, String planet) throws Exception{
		java.util.Date utilDate = new java.util.Date();
		java.sql.Timestamp sqlTS = new java.sql.Timestamp(utilDate.getTime());
		fleetsMergeNewsUpdateStatement.setInt(1, userID);
		fleetsMergeNewsUpdateStatement.setInt(2, empireId);
		fleetsMergeNewsUpdateStatement.setTimestamp(3, sqlTS);
		fleetsMergeNewsUpdateStatement.setInt(4, tickNumber);

		String mergedFleets = "These units: " ;
		for(int i = 0; i < unit_names.length; i++){
			if (fleets[i] > 0)
				mergedFleets += "\n " + unit_labels[i] + " " +  fleets[i];
		}
		mergedFleets += " have merged at planet: " + planet;
		
		fleetsMergeNewsUpdateStatement.setString(5, mergedFleets);
		fleetsMergeNewsUpdateStatement.addBatch();
	}
	
	public void createfleetStationNews(int userID, int empireID, long [] fleets, 
										int success, int x, int y, int i) throws Exception{
		java.util.Date utilDate = new java.util.Date();
		java.sql.Timestamp sqlTS = new java.sql.Timestamp(utilDate.getTime());
		fleetsStationNewsUpdateStatement.setInt(1, userID);
		fleetsStationNewsUpdateStatement.setInt(2, empireID);
		fleetsStationNewsUpdateStatement.setTimestamp(4, sqlTS);
		fleetsStationNewsUpdateStatement.setInt(5, tickNumber);

		String stationedFleets = "" ;
		for(int j = 0; j < unit_names.length; j++){
			if (fleets[j] > 0)
				stationedFleets += "\n " + unit_labels[j] + " " +  fleets[j];
		}
		
		String stationInfo = "";
		if (success == 0){
			fleetsStationNewsUpdateStatement.setString(3, "FU");
			stationInfo += " could not station at planet + " + x + ":" + y + "," + "i";
			stationInfo += " because it doesn't belong to you!";
		}
		if (success == 1){
			fleetsStationNewsUpdateStatement.setString(3, "FS");
			stationInfo += " successfully stationed on planet: " + x + ":" + y + "," + i + "!";
		}
		if (success == 2){
			fleetsStationNewsUpdateStatement.setString(3, "FU");
			stationInfo += " could not station at planet: " + x + ":" + y + "," + i;
			stationInfo += " because it doesn't exist!";
		}
		fleetsStationNewsUpdateStatement.setString(6, stationedFleets);
		fleetsStationNewsUpdateStatement.setString(7, stationInfo);
		fleetsStationNewsUpdateStatement.addBatch();
	}
		
	public void executeNews() throws Exception{
		buildingNewsUpdateStatement.executeBatch();
		fleetsNewsUpdateStatement.executeBatch();
		fleetsReturnNewsUpdateStatement.executeBatch();
		fleetsMergeNewsUpdateStatement.executeBatch();
		fleetsStationNewsUpdateStatement.executeBatch();
	}
}