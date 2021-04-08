package org.ectroverse.processtick;

import java.sql.*;
import java.util.*;
import java.time.Clock; 
import java.time.Instant; 

public class HelperFunctions{
	
	public static double calc_overbuild(int size, int buildings) {
		if (buildings <= size) return 1.0;
    	return Math.pow((buildings/(double)size),2);
    }
	
	public static double battlePortalCalc(int x, int y, LinkedList<Planet> portals, int portalResearch){
		double cover = 0;
		for (Planet portal : portals){
		    double d = Math.sqrt(Math.pow((x-portal.x),2) + Math.pow((y-portal.y),2));
		    cover = Math.max(0, 1.0 - Math.sqrt(d/(7.0*(1.0 + 0.01*portalResearch))));
		}
		return cover;
	}
	
	public static long secondsToFirstOccurence10(Calendar calendar) {
    int seconds = calendar.get(Calendar.SECOND);
    int millis = calendar.get(Calendar.MILLISECOND);
    int secondsToNextTenSeconds = 10 - seconds % 10 -1;
    int millisToNextSecond = 1000 - millis;
    return secondsToNextTenSeconds*1000 + millisToNextSecond;
	}
	
	public static long secondsToFirstOccurence600(Calendar calendar) {
	int minutes = calendar.get(Calendar.MINUTE);
    int seconds = calendar.get(Calendar.SECOND);
    int millis = calendar.get(Calendar.MILLISECOND);
	int minutesToNextTenMinutes = 10 - minutes % 10 -1;
    int secondsToNextMinute = 60 - seconds -1;
    int millisToNextSecond = 1000 - millis;
    return minutesToNextTenMinutes*60*1000 + secondsToNextMinute*1000 + millisToNextSecond;
	}

	public static Object getValueByType(int columnIndex, int columnType, ResultSet queryResult) throws SQLException {
		switch (columnType) {
			case Types.CHAR:
			case Types.NCHAR:
			case Types.VARCHAR:
			case Types.NVARCHAR:
				return queryResult.getString(columnIndex);
			case Types.INTEGER:
				return queryResult.getInt(columnIndex);
			case Types.TIMESTAMP:
				return queryResult.getTimestamp(columnIndex);
			case Types.DATE:
				return queryResult.getDate(columnIndex);
			case Types.BOOLEAN:
				return queryResult.getBoolean(columnIndex);
			case Types.DOUBLE:
				return queryResult.getDouble(columnIndex);
			case Types.BIT:
				return queryResult.getBoolean(columnIndex);
			default:
				return queryResult.getString(columnIndex);
		}
	}
	
	
	public static Planet find_nearest_portal(double x, double y, LinkedList<Planet> portal_list){
		Planet portal = portal_list.getFirst();
		double min_dist = Math.pow(((double)portal.x - x),2) + 
							Math.pow(((double)portal.y - y),2);

		for (Planet p : portal_list){
			double dist = Math.pow(((double)p.x - x),2) + 
							Math.pow(((double)p.y - y),2);
			if (dist < min_dist){
				min_dist = dist;
				portal = p;
			}
		}
		return portal;
	}

	public static int find_travel_time(Planet portal, double current_position_x, double current_position_y, double speed){
		double min_dist = Math.sqrt(current_position_x - portal.x) + Math.sqrt(current_position_y - portal.y);
		return (int)(min_dist / speed);
	}

	public static double x_move_calc(double speed, int x, double current_position_x, int y, double current_position_y){
		double dist_x = (double)x - current_position_x;
		double dist_y = (double)y - current_position_y;
		if (dist_x == 0)
			return x;
		double move_x = speed / Math.sqrt(1.0 + Math.pow(dist_y/dist_x,2));

		if (x < current_position_x)
			return (current_position_x - move_x);
		else
			return (current_position_x + move_x);
	}

	public static double y_move_calc(double speed, int x, double current_position_x, int y, double current_position_y){
		double dist_x = (double)x - current_position_x;
		double dist_y = (double)y - current_position_y;
		if (dist_y == 0)
			return y;
		double move_y = speed / Math.sqrt(1.0 + Math.pow(dist_x/dist_y,2));

		if (y < current_position_y)
			return (current_position_y - move_y);
		else
			return (current_position_y + move_y);
	}
}