package org.ectroverse.processtick;

public final class Settings {	
	public static final String connectionPath = "jdbc:postgresql://ectroversedjango_db_1:5432/djangodatabase"; //specify your db connection, e.g. jdbc:postgresql://ectroversedjango_db_1:5432/djangodatabase
	public static final String dbUserName = "dbadmin"; //your database username
	public static final String dbPass = "admin12345"; //your database password
	
	//specify in tick time in seconds
	//set them so they fit without a remainder either within a minute (e.g 10 second tick, but not 11)
	//or in an hour (5min tick, not 7)
	//otherwise you will have a harder time aligning the js ticking clock (shown ingame), which now is set to go from the start of every 10 seconds
	public static final int tickTime = 30; 
}