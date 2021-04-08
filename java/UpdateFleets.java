package org.ectroverse.processtick;

import java.sql.*;
import java.util.*;
import static org.ectroverse.processtick.Constants.*;

public class UpdateFleets {

	private final String fleetsUpdateQuery =
	"UPDATE app_fleet SET" +	
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
	
	private final String fleetMergeQuery = 
	"UPDATE app_fleet SET" +
	" bomber = ?" + //1
	" , fighter = ? "+ //2
	" , transport = ? "+ //3
	" , cruiser = ? " + //4
	" , carrier = ? " + //5
	" , soldier = ? " + //6
	" , droid = ? " + //7
	" , goliath = ? "+ //8
	" , phantom = ? " + //9
	" , wizard = ? " + //10
	" , agent = ? " + //11
	" , ghost = ? "+ //12
	" , exploration = ? "+ //13
	" WHERE id = ?"; //14
	
	String fleetStationQuery = "UPDATE app_fleet SET" +
	" bomber = ?" + //1
	" , fighter = ? "+ //2
	" , transport = ? "+ //3
	" , cruiser = ? " + //4
	" , carrier = ? " + //5
	" , soldier = ? " + //6
	" , droid = ? " + //7
	" , goliath = ? "+ //8
	" , phantom = ? " + //9
	" , wizard = ? " + //10
	" , agent = ? " + //11
	" , ghost = ? "+ //12
	" , exploration = ? "+ //13
	" , on_planet_id = ? "+ //14
	" , command_order = 8 "+
	" WHERE id = ?"; //16
	
	private final String phantomsUpdateQuery =
	"UPDATE app_fleet SET" +
	" phantom = ? " + //1
	" WHERE id = ?"; //1
	
	String fleetsDeleteUpdateQuery = "DELETE FROM app_fleet WHERE id = ?";
	
	String emptyFleetsDelete = "DELETE FROM app_fleet WHERE " + 
	"bomber = 0 AND fighter = 0 AND transport = 0 AND cruiser = 0 AND carrier = 0 AND soldier = 0 AND droid = 0 AND " + 
	"goliath = 0 AND phantom = 0 AND wizard = 0 AND agent = 0 AND ghost = 0 and exploration = 0 AND main_fleet = false";
	
	private PreparedStatement fleetsUpdateStatement;
	private PreparedStatement fleetMergeUpdateStatement;
	private PreparedStatement fleetStationUpdateStatement; 
	private PreparedStatement fleetPhantomsUpdateStatement; 
	private PreparedStatement fleetsDeleteUpdateStatement;
	private Connection connection;
	private Statement statement;
	private Statement statement2;
	private int total_built_units;
	private int userID;
	private int empireID;
	private int tickNumber;
	private UpdateNews addNews;
	PreparedStatement userStatusUpdateStatement;
	
	public UpdateFleets(Connection connection, UpdateNews addNews) throws Exception{
		this.connection = connection;
		this.addNews = addNews; 
		statement = connection.createStatement();
		statement2 = connection.createStatement();
		fleetsUpdateStatement = connection.prepareStatement(fleetsUpdateQuery); 
		fleetMergeUpdateStatement = connection.prepareStatement(fleetMergeQuery); 
		fleetStationUpdateStatement = connection.prepareStatement(fleetStationQuery); 
		fleetPhantomsUpdateStatement = connection.prepareStatement(phantomsUpdateQuery); 
		fleetsDeleteUpdateStatement = connection.prepareStatement(fleetsDeleteUpdateQuery); 
	}
	
	public void addNewUser(int userID, int empireID, int tickNumber, PreparedStatement userStatus) throws Exception{
		this.userID = userID;
		this.empireID = empireID;
		this.tickNumber = tickNumber;
		total_built_units = 0;
		this.userStatusUpdateStatement = userStatus;
	}
	
	public void updateFleetBuild(HashMap<String, Integer> unitsBuilt) throws Exception{
		
		for(int i = 1; i <= unit_names.length; i++){
			fleetsUpdateStatement.setLong(i, unitsBuilt.getOrDefault(unit_names[i-1],0));
			total_built_units += unitsBuilt.getOrDefault(unit_names[i-1],0);
		}
		if (total_built_units > 0) {
			addNews.createfleetBuildingNews(userID, empireID, unitsBuilt);
			userStatusUpdateStatement.setInt(56, 1); //set button flag for header menu
		}
		
		fleetsUpdateStatement.setInt(14, userID);
		fleetsUpdateStatement.addBatch();
	}

	public void updateFleetsMerge() throws Exception{
		ResultSet mergingFleets = statement.executeQuery("SELECT * FROM app_fleet WHERE (command_order = 3 OR command_order = 4) AND owner_id = " + userID + 
			" AND ticks_remaining = 0;");
			
		HashMap<String, LinkedList<Integer>> fleetMarge = new HashMap<>();
		
		while(mergingFleets.next()){
			String p = "x" + mergingFleets.getInt("x") + ":y" + mergingFleets.getInt("y");
			if (!fleetMarge.containsKey(p))
				fleetMarge.put(p, new LinkedList<Integer>());
			fleetMarge.get(p).add(mergingFleets.getInt("id"));
		}
			
		for(Map.Entry<String, LinkedList<Integer>> entry : fleetMarge.entrySet()){
			String planet = entry.getKey();
			LinkedList<Integer> idList = entry.getValue();
			if (idList.size() > 1){
				long [] unit = new long[unit_names.length];
				int firstId = idList.getFirst();
				for (Integer id : idList) {
					ResultSet fleet = statement.executeQuery("SELECT * FROM app_fleet WHERE id = " + id + ";");
					fleet.next();
					for(int i =0; i < unit_names.length; i++){
						unit[i] += fleet.getLong(unit_names[i]);
					}
					if (id != firstId)
						statement.execute("DELETE FROM app_fleet WHERE id = " + id + ";");
				}
				for(int i =0; i < unit_names.length; i++){
					fleetMergeUpdateStatement.setLong(i+1, unit[i]);
				}
				fleetMergeUpdateStatement.setInt(unit_names.length+1 , firstId);
				fleetMergeUpdateStatement.addBatch();
				addNews.createfleetMergeNews(userID, empireID, unit, planet);
				System.out.println("merged!");
				userStatusUpdateStatement.setInt(58, 2); //set military flag green for the header menu
			}
		}
	}

	public void updateReturnedFleets(long [] returnFleets) throws Exception{
		boolean returnedUnits = false;
		for(int i = 0; i < unit_names.length; i++){
			fleetsUpdateStatement.setLong(i+1, returnFleets[i]);
			if (returnFleets[i] > 0)
				returnedUnits = true;
		}
		fleetsUpdateStatement.setInt(14, userID);
		fleetsUpdateStatement.addBatch();
		
		if (returnedUnits) {
			addNews.createfleetReturnNews(userID, empireID, returnFleets);
			userStatusUpdateStatement.setInt(58, 2);
		}
	}
	
	public void updateStationedFleets() throws Exception{
		ResultSet stationingFleets = statement.executeQuery("SELECT * FROM app_fleet WHERE command_order = 1 AND owner_id = " + userID + 
		" AND ticks_remaining = 0;");

		HashMap<Integer, LinkedList<Integer>> fleetStation = new HashMap<>();
		while(stationingFleets.next()){
			int x = stationingFleets.getInt("x");
			int y = stationingFleets.getInt("y") ;
			int i = stationingFleets.getInt("i");
			ResultSet planet = statement2.executeQuery("SELECT id, owner_id FROM \"PLANET\" WHERE x = "  +  x +
			" AND y = " + y +
			" AND i = " + i );
			
			long [] fleet = new long[unit_names.length];
			for(int j =0; j < unit_names.length; j++){
				fleet[j] += stationingFleets.getLong(unit_names[j]);
			}
			
			if (planet.next()){
				if (planet.getInt("owner_id") != userID){
					statement2.execute("UPDATE app_fleet SET command_order = 2 WHERE id = " + stationingFleets.getInt("id") + ";");
					addNews.createfleetStationNews(userID, empireID, fleet, 0, x, y, i);
					userStatusUpdateStatement.setInt(58, 3);
				}
				else{
					int p = planet.getInt("id");
					if (!fleetStation.containsKey(p))
						fleetStation.put(p, new LinkedList<Integer>());
					fleetStation.get(p).add(stationingFleets.getInt("id"));
					addNews.createfleetStationNews(userID, empireID, fleet, 1, x, y, i);
					userStatusUpdateStatement.setInt(58, 2);
				}
			}
			else{
				statement.execute("UPDATE app_fleet SET command_order = 2 WHERE id = " + stationingFleets.getInt("id") + ";");
				addNews.createfleetStationNews(userID, empireID, fleet, 2, x, y, i );
				userStatusUpdateStatement.setInt(58, 3);
			}
		}

		//Map.Entry<String, Object> entry : map.entrySet()
		for(Map.Entry<Integer, LinkedList<Integer>> entry : fleetStation.entrySet()){
			LinkedList<Integer> idList = entry.getValue();
			int pID = entry.getKey();
			if (idList.size() > 0){
				long [] unit = new long[unit_names.length];
				int firstId = idList.getFirst();
				for (Integer id : idList) {
					ResultSet fleet = statement.executeQuery("SELECT * FROM app_fleet WHERE id = " + id + ";");
					fleet.next();
					for(int i =0; i < unit_names.length; i++){
						unit[i] += fleet.getLong(unit_names[i]);
					}
					
					if (id != firstId)
						statement.execute("DELETE FROM app_fleet WHERE id = " + id + ";");
				}

				for(int i =0; i < unit_names.length; i++){
					fleetStationUpdateStatement.setLong(i+1, unit[i]);
				}
				fleetStationUpdateStatement.setInt(unit_names.length+1 , pID); //set planet id
				fleetStationUpdateStatement.setInt(unit_names.length+2 , firstId); //set fleet id
				fleetStationUpdateStatement.addBatch();
			}
			
		}
	}
	
	public void updatePhantomDecay(long networth) throws Exception{
		ResultSet phantomsResultSet = statement.executeQuery("SELECT id, phantom FROM app_fleet WHERE owner_id = " + userID + ";");
		ResultSet psychicsResultSet = statement2.executeQuery("SELECT wizard FROM app_fleet WHERE main_fleet = true AND owner_id = " + userID + ";");
		psychicsResultSet.next();
		double psychics = psychicsResultSet.getLong("wizard");
		while(phantomsResultSet.next()){
			long phantoms = phantomsResultSet.getLong("phantom");
			// calculate phantoms decay rate
			double phdecay = 0.20;
			double fa = phantoms /  psychics;
			if( fa < 0.05 ) {
				phdecay = 0.01;
			} else {
					fa = Math.pow( (1.0/0.05) * fa, 2.4 );
					phdecay = 0.01*fa;
				if( phdecay > 0.20 ) {
					phdecay = 0.20;
				}
			}
			phantoms = (long)(phantoms * (1 - phdecay));
			fleetPhantomsUpdateStatement.setLong(1, phantoms);
			fleetPhantomsUpdateStatement.setInt(2, phantomsResultSet.getInt("id"));
			fleetPhantomsUpdateStatement.addBatch();
		}
	}
	
	public void deleteEmptyFleets() throws Exception{
		statement.execute(emptyFleetsDelete);
	}
	
	public int getTotalBuiltUnits(){
		return total_built_units;
	}
	
	public void executeFleetsUpdate() throws Exception{
		fleetsUpdateStatement.executeBatch();
		fleetMergeUpdateStatement.executeBatch();
		fleetStationUpdateStatement.executeBatch();
		fleetPhantomsUpdateStatement.executeBatch();
	}

}