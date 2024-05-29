package workers;

import documento.DocModel;
import documento.DocRecord;
import main.Controller;
import main.MainController;
import main.Utils;
import java.io.BufferedInputStream;
import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.PrintWriter;
import java.net.HttpURLConnection;
import java.net.Socket;
import java.net.URI;
import java.net.URISyntaxException;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Enumeration;
import java.util.List;
import java.util.concurrent.ExecutionException;
import java.util.jar.JarEntry;
import java.util.jar.JarFile;
import java.util.logging.Level;
import java.util.logging.Logger;
import javax.swing.JOptionPane;
import javax.swing.SwingWorker;
import widgets.TopMessageDialog;

/*
 * Execute command line app with parameters. Outputs are sent to controller to
 * show them in both console and view.
 */
public class ServerWorkerSockets extends SwingWorker {

	Controller controller;
	DocModel docModel;
	Socket socket;
	PrintWriter writer;
	BufferedReader reader;

	String serverUrl; // Server address and entry point
	int portNumber;      // Connection port

	ArrayList<String> commandList; // Command line as list

	public ServerWorkerSockets (Controller controller, DocModel docModel) {
		this.controller = controller;
		this.docModel = docModel;
	}

	public void initSocket (int portNumber) throws IOException {
		this.portNumber = portNumber;
		this.socket = new Socket ("localhost", 8888);
		OutputStream out = socket.getOutputStream ();
		writer = new PrintWriter (out, true);

		// Receive response from Python server
		InputStream in = socket.getInputStream ();
		reader = new BufferedReader (new InputStreamReader (in));
	}

	public void closeSocket () throws IOException {
		writer.close ();
		reader.close ();
		socket.close ();
	}

	//-----------------------------------------------------------------	
	// Create command list according to the OS, service, and parameters
	//--------------------------------------------------------	-------
	public void createExecutableCommand () {
		String OS = System.getProperty ("os.name").toLowerCase ();
		String separator = OS.contains ("windows") ? "\\" : "/";

		// For testing: python .py, for production: windows .exe
		String exeProgram = "ecuapass_server" + separator + "ecuapass_server_sockets.exe";
		String pyProgram = "ecuserver" + separator + "ecuapass_server_sockets.py";

		String command = "";
		if (OS.contains ("windows"))
			if (DocModel.runningPath.contains ("test")) {
				command = Paths.get (docModel.runningPath, pyProgram).toString ();
				commandList = new ArrayList<> (Arrays.asList ("cmd.exe", "/c", "python", command));
			} else {
				command = Paths.get (docModel.runningPath, exeProgram).toString ();
				commandList = new ArrayList<> (Arrays.asList (command));
			}
		else {
			command = Paths.get (docModel.runningPath, pyProgram).toString ();
			commandList = new ArrayList<> (Arrays.asList ("python3", command));
		}
	}

// Send message to server to start a process using data
	public boolean startProcess (String service, String data1, String data2) {
		try {
			this.initSocket (portNumber);
			
			controller.out ("Starting process:%s:%s:%s".format (service, data1, data2));
			// Send request to Python server
			String requestString = "" + service + " " + data1 + " " + data2;
			writer.println (requestString);          // "REQUEST ARG1 ARG2"

			String response = reader.readLine ();
			System.out.println ("Response from Python server: " + response);
			this.closeSocket ();
		} catch (IOException ex) {
			Logger.getLogger (ServerWorkerSockets.class.getName ()).log (Level.SEVERE, null, ex);
		}
		return true;

	}

// Copy input files in 'DocModel' to new working dir with new docType name
	public void copyDocsToProjectsDir (ArrayList<DocRecord> records) {
		docModel.createFolder (docModel.projectsPath);

		for (DocRecord record : records) {
			// Copy source document image
			File docFilepath = new File (record.docFilepath);
			File destFilepath = new File (docModel.projectsPath, record.docTypeFilename);
			Utils.copyFile (docFilepath.toString (), destFilepath.toString ());

			// Copy cache document in pickle file
			File docCacheFilepath = new File (Utils.getResultsFile (record.docFilepath, "CACHE.pkl"));
			record.docFilepath = destFilepath.toString ();
			if (docCacheFilepath.exists ()) {
				destFilepath = new File (docModel.projectsPath, docCacheFilepath.getName ());
				Utils.copyFile (docCacheFilepath.toString (), destFilepath.toString ());
			}
		}
	}

	// Copy emmbeded resources  (programs and images) to temporal dir
	public boolean copyResourcesToTempDir () {
		docModel.createFolder (docModel.temporalPath + "/" + "resources");
		if (this.copyResourcesFromJarToTempDir ())
			controller.out ("CLIENTE: Copiando recursos desde un JAR.");
		else if (this.copyResourcesFromPathToTempDir ())
			controller.out ("CLIENTE: Copiando recursos desde un PATH.");
		else {
			JOptionPane.showMessageDialog (null, "No se pudieron copiar los recursos necesarios para la ejecución!");
			return false;
		}
		return true;
	}

	public boolean copyResourcesFromJarToTempDir () {
		try {
			String resourceDirPath = "/resources"; // Specify the resource directory path within the JAR
			// Get the JAR file containing the resources
			File jarFile = new File (this.getClass ().getProtectionDomain ().getCodeSource ().getLocation ().toURI ());
			JarFile jar = new JarFile (jarFile);

			Enumeration<JarEntry> entries = jar.entries (); // Get a list of resource file and directory names
			while (entries.hasMoreElements ()) {
				JarEntry entry = entries.nextElement ();
				String entryName = entry.getName ();

				if (entryName.startsWith ("resources")) {  // Check if the entry is in the specified resource directory
					Path destinationPath = Paths.get (docModel.temporalPath, "resources", entryName.substring (resourceDirPath.length ()));
					if (entry.isDirectory ())
						Files.createDirectories (destinationPath); // This is a directory, so create it in the destination
					else // This is a file, so copy it to the destination
						try (InputStream inputStream = jar.getInputStream (entry)) {
						Files.copy (inputStream, destinationPath, StandardCopyOption.REPLACE_EXISTING);
					}
				}
			}
			jar.close ();
		} catch (IOException | URISyntaxException ex) {
			System.out.println ("--- ERROR copiando recursos desde JAR");
			return false;
		}
		return true;
	}

	public boolean copyResourcesFromPathToTempDir () {
		try {
			String resourceDir = "resources/";// Specify the resource directory path within the JAR			
			ClassLoader classLoader = this.getClass ().getClassLoader ();// Get a reference to the current class loader			
			URL resourceUrl = classLoader.getResource (resourceDir);// Get the URL of the resource directory
			if (resourceUrl == null)
				System.out.println ("SERVER: Carpeta de recursos no encontrada: " + resourceDir);
			else {
				URI uri = resourceUrl.toURI ();
				Path resourcePath = Paths.get (uri);// Convert the URL to a Path		
				Files.walk (resourcePath)// Walk the directory and collect all resource names
					.forEach (filePath -> {
						if (filePath.equals (resourcePath) == false) {
							Path relativePath = resourcePath.relativize (filePath);
							Path destinationPath = Paths.get (docModel.temporalPath, resourceDir, relativePath.toString ());
							if (Files.isDirectory (destinationPath))
								destinationPath.toFile ().mkdir ();
							else
							try {
								Files.copy (filePath, destinationPath, StandardCopyOption.REPLACE_EXISTING);
							} catch (IOException ex) {
								Logger.getLogger (this.getClass ().getName ()).log (Level.SEVERE, null, ex);
							}
						}
					}
					);
			}
		} catch (URISyntaxException | IOException ex) {
			System.out.println ("--- ERROR copiando recursos desde TEMP");
			ex.printStackTrace ();
			return false;
		}
		return true;
	}

	@Override
	protected String doInBackground () throws Exception {
		System.out.println (">> Ejecutándose en background...");
		this.createExecutableCommand ();
		if (this.copyResourcesToTempDir () == false)
			return ("ERROR: No se pudo copiar recursos.");

		controller.out ("CLIENTE: Ejecutándose el servidor: " + commandList);
		ProcessBuilder processBuilder;
		processBuilder = new ProcessBuilder (commandList);
		processBuilder.redirectErrorStream (true);
		//processBuilder.directory (new File (this.serverHomePath));
		Process p = processBuilder.start ();
		String lastLine = "";
		try {
			BufferedInputStream bis = new BufferedInputStream (p.getInputStream ());
			BufferedReader stdout = new BufferedReader (new InputStreamReader (bis, "UTF-8"));
			String stdoutLine = "";
			while ((stdoutLine = stdout.readLine ()) != null) {
				lastLine = stdoutLine;
				publish (stdoutLine);
			}
		} catch (IOException e) {
			e.printStackTrace ();
			p.getInputStream ().close ();
		}
		// Return last line to check if script successfully ended
		return (lastLine);
	}

	@Override
	protected void process (List chunks) {
			// Handle intermediate results received during thread execution
			for (Object obj : chunks) {
				String statusMsg = obj.toString ();
				controller.out (statusMsg);
				if (statusMsg.contains ("Server is running on port")) {
					this.portNumber = Integer.parseInt (statusMsg.split ("::")[1].trim ());
					//this.initSocket (portNumber);
					controller.onServerRunning (portNumber);
				} else if (statusMsg.contains ("Análisis exitoso del documento")) {
					String docFilename = statusMsg.split ("'")[1].trim ();
					controller.onEndProcessing (docFilename, "EXITO");
				} else if (statusMsg.contains ("ALERTA:")) {
					statusMsg = statusMsg.split ("ALERTA:")[1];
					TopMessageDialog dialog = new TopMessageDialog (controller.getMainView (), statusMsg);
					dialog.setVisible (true);
				} else if (statusMsg.contains ("FEEDBACK:")) {  // Server sends feedback
					String docFilepath = statusMsg.split ("'")[1];
					controller.onSendFeedback (docFilepath);
				}
			} 
	}

	@Override
	protected void done () {
		try {
			// Called when the background thread finishes execution
			System.out.println (">>> Servidor finalizado...");
			String statusMsg = (String) get ();
			System.out.println (statusMsg);

		} catch (InterruptedException | ExecutionException ex) {
			Logger.getLogger (ServerWorker.class
				.getName ()).log (Level.SEVERE, null, ex);
		}
	}

	public static void main (String[] args) {
		try {
			MainController ctr = new MainController ();
			ServerWorkerSockets rw = new ServerWorkerSockets (new Controller (), new DocModel ());
			rw.execute ();

		} catch (Exception ex) {
			Logger.getLogger (ServerWorker.class
				.getName ()).log (Level.SEVERE, null, ex);
		}
	}
}
