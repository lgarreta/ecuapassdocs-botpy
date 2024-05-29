
package main;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class Test {
	public static void main (String[] args) {
		String text = "CPI-NTA-ECCO004314.pdf";
		String substring = "A";
		String regex = substring + "\\b";

		Pattern pattern = Pattern.compile (regex);
		Matcher matcher = pattern.matcher (text);

		if (matcher.find())
			System.out.println ("Found exact substring: " + matcher.group ());
		else
			System.out.println ("Exact substring not found.");

	}
	
}
