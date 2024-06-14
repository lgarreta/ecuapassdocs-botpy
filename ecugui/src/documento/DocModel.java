package documento;

import main.Controller;
import main.Utils;
import java.io.File;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Locale;

public class DocModel {

	ArrayList<DocRecord> selectedRecords;             // Invoice files selected for processing
	ArrayList<DocRecord> processedRecords;         // Invoice files "rightly" processed
	public DocRecord currentRecord = null;
	
	public static String projectsPath;  // Global dir for save and open all projects
	public static String workingPath;  // Current dir of the project
	public static String runningPath;     // Application start running dir
	public static String temporalPath; // Dir for resources 
	public static String resourcesPath;
	public static String companyName; // Name of the company for selecting document cloud models
	public static String companiesString;
	; // Piped companies with document cloud models
	public static String ecuapassdocsURL = "https://ecuapassdocs-test.up.railway.app/";
	public static String codebiniURL = "https://byza.corebd.net/";
	public static String ecuapassURL = "https://ecuapass.aduana.gob.ec/";
	public static boolean SHOW_DOCS_BUTTONS = false;

	public DocModel () {
		selectedRecords = new ArrayList<> ();
		processedRecords = new ArrayList<> ();
	}

	public void initGlobalPaths () {
		projectsPath = this.getProjectsDir ();
		workingPath = projectsPath;
		temporalPath = this.getTemporalDir (workingPath);
		runningPath = Utils.convertToOSPath (System.getProperty ("user.dir"));
		resourcesPath = Utils.getResourcePath (this, "");
		companiesString = "BYZA|NTA|BOTERO|SYTSA|SILOGISTICA";
	}

	public void printGlobalPaths (Controller controller) {
		controller.out (">>> Projects dir: " + projectsPath);
		controller.out (">>> Working dir: " + workingPath);
		controller.out (">>> Temporal dir: " + temporalPath);
		controller.out (">>> Running dir: " + runningPath);
		controller.out (">>> Resources dir: " + resourcesPath);
	}

	public String getTemporalDir (String workingDir) {
		String osTempDir = Utils.convertToOSPath (System.getProperty ("java.io.tmpdir"));
		//String pathName = Utils.convertToOSPath (Paths.get (workingDir).getFileName ().toString ());
		String pathName = "tmp-cartaportes";
		String path = Paths.get (osTempDir, pathName).toString ();
		return Utils.convertToOSPath (path);
	}

	// Dir for current user sesion 
	public String getProjectsDir () {
		String relativePath = Paths.get ("Documents", "Ecuapassdocs").toString ();
		Path absolutePath = Paths.get (System.getProperty ("user.home"), relativePath);
		String path = absolutePath.toString ();
		return Utils.convertToOSPath (path);
	}

	// Create dir in "Documents" for results using current time
	public String getWorkingDir (String projectsDir) {
		LocalDateTime now = LocalDateTime.now ();			// Get the current date and time
		// Define the desired date and time format with Spanish month names
		DateTimeFormatter formatter = DateTimeFormatter.ofPattern ("dd-MMMM-yyyy-HH_mm_ss", new Locale ("es"));
		String timestamp = now.format (formatter);			// Format the current date and time to a string
		String path = Paths.get (projectsDir, timestamp).toString ();		// Create a File object representing the new folder
		return (Utils.convertToOSPath (path));
	}

	// Create folder given the absolute path
	public void createFolder (String folderName) {
		File folder = new File (folderName);
		if (folder.exists () == false)
			if (folder.mkdirs () == false)
				System.out.println (">>> Error al crear la carpeta: " + folder.toString ());
	}

	public ArrayList<DocRecord> getSelectedRecords () {
		return (selectedRecords);
	}

	public ArrayList<DocRecord> getProcessedRecords () {
		return (processedRecords);
	}

	public void addProcessedRecord (DocRecord record) {
		processedRecords.add (record);
	}

	public void addSelectedRecord (DocRecord record) {
		selectedRecords.add (record);
	}

	//  Check if file was previously added
	public boolean existsFile (File file) {
		String filename = file.getName ();
		for (DocRecord rec : selectedRecords) {
			String recFilename = new File (rec.docFilepath).getName ();
			if (recFilename.equals (filename))
				return true;
		}
		return false;
	}

	public boolean existsRecord (DocRecord docRecord) {
		String docFilepath = docRecord.docFilepath;
		return (existsFile (new File (docFilepath)));
	}

	public void removeAllFiles () {
		selectedRecords.clear ();
	}

	// Get files, not dirs, from list of files from current directory
	public File[] getFilesOnly (File[] allFiles) {
		ArrayList<File> allFilesArray = new ArrayList ();
		for (File file : allFiles) {
			if (file.isFile ())
				allFilesArray.add (file);
		}
		File allFilesOnly[] = new File[allFilesArray.size ()];
		return (allFilesArray.toArray (allFilesOnly));
	}
}
