package org.ectroverse.processtick;

public final class Settings {	
	String connectionPath = "jdbc:postgresql://ectroversedjango_db_1:5432/djangodatabase"; //specify your db connection, e.g. jdbc:postgresql://ectroversedjango_db_1:5432/djangodatabase
	String dbUserName = "dbadmin"; //your database username
	String dbPass = "admin12345"; //your database password
	int tickTime = 10; //specify in tick time in seconds
}