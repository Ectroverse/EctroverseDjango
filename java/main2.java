import java.util.*;
import java.time.*;
import java.util.concurrent.*;

public class main2
{
	
	static final HashMap<String, String> buildingsNames = new HashMap<>();
	
	static {
	buildingsNames.put( "SC", "solar_collectors");
	}
	
	public static void main(String[] args) {
			
	ScheduledExecutorService s = Executors.newSingleThreadScheduledExecutor();
	Calendar calendar = Calendar.getInstance();
	Runnable scheduledTask = new Runnable() {
		
		public void run() {
			System.out.println("test");
			task();
		}
	};
	
	long millistoNext = secondsToFirstOccurence(calendar);
	System.out.println("millistoNext: " + millistoNext);	
	s.scheduleAtFixedRate(scheduledTask, millistoNext, 10*1000, TimeUnit.MILLISECONDS);
	}
	
	private static void task(){
		Clock clock = Clock.systemDefaultZone();
		Instant instant = clock.instant();
		System.out.println("Current time: " + instant);	
	}
	
	private static long secondsToFirstOccurence(Calendar calendar) {
    int seconds = calendar.get(Calendar.SECOND);
    int millis = calendar.get(Calendar.MILLISECOND);
    int secondsToNextTenSeconds = 10 - seconds % 10 -1;
    int millisToNextTenSecond = 1000 - millis;
    return secondsToNextTenSeconds*1000 + millisToNextTenSecond;
	}
}