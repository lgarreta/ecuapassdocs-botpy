package documento;

import java.io.IOException;
import org.json.simple.parser.ParseException;

public class DocRecordManifiesto extends DocRecord {
	// Constructor for records after cloud processing
	public DocRecordManifiesto (DocRecord docRecord) throws ParseException, IOException {
		super ("manifiesto", docRecord.docFilepath, docRecord.jsonFilepath);
		
		// Main fields from defaults
		mainFields = super.getMainFields ();
	}
}
