package documento;

import java.io.IOException;
import org.json.simple.parser.ParseException;

public class DocRecordCartaporte extends DocRecord {
	// Constructor for records after cloud processing
	public DocRecordCartaporte (DocRecord docRecord) throws ParseException, IOException {
		super ("cartaporte", docRecord.docFilepath, docRecord.jsonFilepath);
		
		// Main fields from defaults
		mainFields = super.getMainFields ();
	}
}
