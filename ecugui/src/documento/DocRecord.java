package documento;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.io.Writer;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;
import java.util.TreeSet;
import java.util.logging.Level;
import java.util.logging.Logger;
import main.Utils;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;

public class DocRecord {

	public String docType;
	public String docFilepath;
	public String jsonFilepath;
	public String docTypeFilename;
	public String docFilename;

	public Map<String, Object> mainFields;

	public DocRecord () {
	}

	// Contructor used before processing files
	public DocRecord (String docFilepath) {
		this.docFilepath = docFilepath;
		this.jsonFilepath = null;
		this.mainFields = null;
		setDocType (Utils.getDocumentTypeFromPDF (docFilepath));

	}

	public DocRecord (String docFilepath, String docType) {
		this.docFilepath = docFilepath;
		this.jsonFilepath = null;
		this.mainFields = null;
		setDocType (docType);
	}

	// Constructor used after processing files
	public DocRecord (String docType, String docFilepath, String jsonFilepath) throws ParseException, IOException {
		this (docFilepath, docType);
		this.docType = docType.toUpperCase ();
		this.jsonFilepath = jsonFilepath;
		this.mainFields = this.getMainFields ();
	}
	
	public String getEcufieldsFile () {
		return this.jsonFilepath;
	} 

	public void setDocType (String docType) {
		this.docType = docType;
		String docPrefix = "NONE";
		docFilename = new File (docFilepath).getName ();
		String prefixFilename = docFilename.split ("-")[0];
		if (prefixFilename.toUpperCase ().matches ("CPI|MCI|DCL"))
			this.docTypeFilename = docFilename;
		else {
			switch (this.docType) {
				case "CARTAPORTE":
					docPrefix = "CPI";
					break;
				case "MANIFIESTO":
					docPrefix = "MCI";
					break;
				case "DECLARACION":
					docPrefix = "DCL";
					break;
			}
			this.docTypeFilename = docPrefix + "-" + docFilename;
		}
	}

	// Get main fields from procesed file
	public Map getMainFields () throws ParseException, IOException {
		mainFields = new HashMap ();
		// Load JSON mainFields to class mainFields
		JSONParser parser = new JSONParser ();
		try {
			// Get values for record view
			Object obj = parser.parse (new FileReader (jsonFilepath));
			JSONObject jsonObject = (JSONObject) obj;
			Set<String> keys = new TreeSet (jsonObject.keySet ());
			mainFields = getFieldsFromJson (jsonObject);
		} catch (IOException | ParseException ex) {
			throw ex;
		}
		return mainFields;
	}

	public Map getFieldsFromJson (JSONObject json) {
		Map fields = new HashMap ();
		Set<String> keys = new TreeSet (json.keySet ());
		for (String k : keys) {
			String value = json.get (k) == null ? "" : json.get (k).toString ();
			fields.put (k, value);
		}
		return (fields);
	}

	@Override
	public String toString () {
		String out = "docType: " + docType + "\n"
			+ "	docFilepath: " + docFilepath + "\n"
			+ "	jsonFilepath: " + jsonFilepath + "\n"
			+ "	docTypeFilename: " + docTypeFilename + "\n"
			+ "	docFilename: " + docFilename + "\n";
		return out;
	}

	
	
	// Return document info: filepath or mainFields after processed
	
	public String toStringFull () {
		StringBuilder str = new StringBuilder ();

		if (this.jsonFilepath == null)
			str.append (String.format ("DocRecord: docType: %s, docTypeFilename: %s, docFilepath: %s", docType, docTypeFilename, docFilepath));
		else {
			TreeSet<String> keys = new TreeSet (mainFields.keySet ());
			for (String k : keys) {
				str.append (k + ":" + mainFields.get (k) + "\n");
			}
		}
		return (str.toString ());
	}

	public TreeSet<String> getMainKeysSorted () {
		TreeSet<String> ts = new TreeSet (mainFields.keySet ());
		return (ts);
	}

	public void update (String key, String text) {
		String value = text.equals ("") ? null : text;
		mainFields.put (key, value);
	}

	// Write record mainfields to json file
	public void writeToJsonFile (String jsonFilepath) {
		JsonParser jsonParser = new JsonParser ();

		try (FileReader fileReader = new FileReader (jsonFilepath); BufferedReader bufferedReader = new BufferedReader (
			new InputStreamReader (new FileInputStream (jsonFilepath), "UTF-8"))) {
			JsonObject jsonObject = (JsonObject) jsonParser.parse (fileReader).getAsJsonObject ();
			TreeSet<String> keysSet = new TreeSet (jsonObject.keySet ());
			for (String key : keysSet) {
				jsonObject.addProperty (key, (String) mainFields.get (key));
			}
			// Step 3: Write the updated JSON object back to the file
			Gson gson = new GsonBuilder ()
				.setPrettyPrinting ()
				.serializeNulls ()
				.create ();
			try (OutputStream os = new FileOutputStream (jsonFilepath); Writer writer = new OutputStreamWriter (os, "UTF-8")) {
				// Serialize the object to JSON and write it to the file with UTF-8 encoding
				gson.toJson (jsonObject, writer);
			}
		} catch (IOException ex) {
			Logger.getLogger (DocRecord.class.getName ()).log (Level.SEVERE, null, ex);
		}
	}
}
