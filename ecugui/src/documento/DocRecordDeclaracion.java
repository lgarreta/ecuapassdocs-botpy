package documento;

import java.io.IOException;
import org.json.simple.parser.ParseException;

public class DocRecordDeclaracion extends DocRecord {
	// Constructor for records after cloud processing
	public DocRecordDeclaracion (DocRecord docRecord) throws ParseException, IOException {
		super ("declaracion", docRecord.docFilepath, docRecord.jsonFilepath);
		
		// Main fields from defaults
		mainFields = super.getMainFields ();
	}
}
