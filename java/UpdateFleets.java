package org.ectroverse.processtick;

import java.sql.*;
import java.util.*;
import static org.ectroverse.processtick.Constants.*;

class UpdateFleets {

	private final String fleetsUpdateQuery = "UPDATE app_fleet SET" +	
	" bomber = bomber + ?" + //1
	" , fighter = fighter + ?" + //2
	" , transport = transport + ?" + //3
	" , cruiser = cruiser + ?" + //4
	" , carrier = carrier + ?" + //5
	" , soldier = soldier + ?" + //6
	" , droid = droid + ?" + //7
	" , goliath = goliath + ?" + //8
	" , phantom = phantom + ?" + //9
	" , wizard = wizard + ?" + //10
	" , agent = agent + ?" + //11
	" , ghost = ghost + ?" + //12
	" , exploration = exploration + ?" + //13
	" WHERE owner_id = ?" + //14
	" AND main_fleet = true;";
	
	private PreparedStatement fleetsUpdateStatement;
	private Connection connection;
	private Statement statement;
	private Statement statement2;
	private int total_built_units;
	private int userID;
	
	public UpdateFleets(Connection connection) throws Exception{
		this.connection = connection;
		statement = connection.createStatement();
		statement2 = connection.createStatement();
		fleetsUpdateStatement = connection.prepareStatement(fleetsUpdateQuery); 
	}
	
	public void addNewUser(int userID){
		this.userID = userID;
		total_built_units = 0;
	}
	
	public void updateFleetBuild(HashMap<String, Integer> unitsBuilt) throws Exception{
		
		for(int i = 1; i <= unit_names.length; i++){
			fleetsUpdateStatement.setLong(i, unitsBuilt.getOrDefault(unit_names[i-1],0));
			total_built_units += unitsBuilt.getOrDefault(unit_names[i-1],0);
		}
		fleetsUpdateStatement.setInt(14, userID);
		fleetsUpdateStatement.addBatch();
	}
	
	public void executeFleetBuildUpdate() throws Exception{
		fleetsUpdateStatement.executeBatch();
	}
	
	public void updateReturnedFleets(long [] returnFleets) throws Exception{
		for(int i = 0; i < unit_names.length; i++){
			fleetsUpdateStatement.setLong(i+1, returnFleets[i]);
		}
		fleetsUpdateStatement.setInt(14, userID);
		fleetsUpdateStatement.addBatch();
	}
	
	public int getTotalBuiltUnits(){
		return total_built_units;
	}

}