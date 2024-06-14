package workers;

import documento.DocModel;
import documento.DocRecord;
import java.awt.Frame;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import main.Controller;
import main.MainController;
import main.Utils;
import java.io.BufferedInputStream;
import java.io.BufferedReader;
import java.io.FileReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
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
import java.util.Timer;
import java.util.TimerTask;
import widgets.TopMessageDialog;

/*
 * Execute command line app with parameters. Outputs are sent to controller to
 * show them in both console and view.
 */
public class ServerWorker extends SwingWorker {

	Controller controller;
	DocModel docModel;
	String serverUrl = null; // Server address and entry point
	ArrayList<String> commandList; // Command line as list

	public ServerWorker (Controller controller, DocModel docModel) {
		this.controller = controller;
		this.docModel = docModel;
	}

	// Wait until port file is create by the server or shows error message
	public void waitServerUrl () {
		File urlFile = new File ("url_port.txt");
		Timer timer = new Timer ();
		long delay = 3000; // Check every 10 seconds (adjust as needed)

		TimerTask task = new TimerTask () {
			int elapsedTime = 0;

			@Override
			public void run () {
				if (urlFile.exists ()) {
					timer.cancel ();
					serverUrl = getServerUrl (); // Server address and entry point	
					controller.out ("URL JAVA CLIENT::" + serverUrl);
					controller.onServerRunning ();					
				} else {
					controller.out ("+++ Esperando archivo de puerto. Tiempo: " + elapsedTime);
					elapsedTime++;
					if (elapsedTime > 5) {
						timer.cancel ();
						JOptionPane.showMessageDialog (controller.getMainView (), "No se obtuvo archivo de puerto del servidor");
						controller.onWindowClosing ();
					}
				}
			}
		};
		timer.scheduleAtFixedRate (task, delay, delay);
	}	

	// OBSOLETE: Not used
	// Create the URL using a port number sent by the 'printx' server
	public String getServerUrl (int urlPortNumber) {
		serverUrl = String.format ("http://127.0.0.1:%s/start_processing", urlPortNumber);
		return serverUrl;
	}

	// Create the URL form port number in 'url_port.txt" file written by server
	public String getServerUrl () {
		String fileName = "url_port.txt";
		BufferedReader reader = null;
		int portNumber = 5000;
		try {
			reader = new BufferedReader (new FileReader (fileName));
			String line = reader.readLine (); // Read the first line
			reader.close ();
			if (line != null) {
				portNumber = Integer.parseInt (line); // Convert the string to an integer
				serverUrl = String.format ("http://127.0.0.1:%s/start_processing", portNumber);
			}
		} catch (NumberFormatException e) {
			System.out.println ("+++ The file does not contain a valid integer.");
		} catch (FileNotFoundException ex) {
			Logger.getLogger (ServerWorker.class.getName ()).log (Level.SEVERE, null, ex);
		} catch (IOException ex) {
			Logger.getLogger (ServerWorker.class.getName ()).log (Level.SEVERE, null, ex);
		}
		return serverUrl;
	}


// Send message to server to start a process using data
	public void startProcess (String service, String data1, String data2) {
		try {
			// Create URL and open connection
			if (this.serverUrl == null) {
				System.out.println  ("+++ URL no asignada");
				return;
			}
					
			URL url = new URL (this.serverUrl);
			HttpURLConnection connection = (HttpURLConnection) url.openConnection ();

			// Set up the connection for a POST request
			connection.setRequestMethod ("POST");
			connection.setRequestProperty ("Content-Type", "application/json; charset=UTF-8");
			connection.setDoOutput (true);

			// Create JSON payload and write it to the connection's output stream
			String formatStr = "{\"%s\":\"%s\", \"%s\":\"%s\", \"%s\":\"%s\"}";
			String jsonPayload = String.format (formatStr, "service", service, "data1", data1, "data2", data2);
			System.out.println ("+++ payload" + jsonPayload);
			try (OutputStream os = connection.getOutputStream ()) {
				byte[] input = jsonPayload.getBytes (StandardCharsets.UTF_8);
				os.write (input, 0, input.length);
			}
			
			new Thread (() -> {
				this.handleServerResponse (connection);
			}).start ();
		} catch (IOException ex) {
			ex.printStackTrace ();
			controller.out ("ALERTA: Servidor 'EcuServer' no responde..");
		}
	}

	// Handle the response from the server
	public boolean handleServerResponse (HttpURLConnection connection) {
		System.out.println  ("+++" + " Manejando la respuesta del servidor");
		try {
			int responseCode = connection.getResponseCode ();
			if (responseCode != HttpURLConnection.HTTP_OK) {
				System.out.println ("Error sending message to server!");
				return false;
			} else {
				// Read the response (optional)
				BufferedReader in = new BufferedReader (new InputStreamReader (connection.getInputStream ()));
				String line;
				while ((line = in.readLine ()) != null) {
					List<String> chunks = Arrays.asList (line);
					this.process (chunks);
				}
				in.close ();
				return true;

			}
		} catch (IOException ex) {
			ex.printStackTrace ();
		}
		return false;
	}

	@Override
// Handle server intermediate results received durint thread execution
	protected void process (List chunks) {
		for (Object obj : chunks) {
			String statusMsg = obj.toString ();
			controller.out  ("+++ statusMsg: " + statusMsg);			// Check if cloud process ended successfully
			if (statusMsg.contains ("EXITO")) {
				controller.onEndProcessing ("EXITO", statusMsg);
			} else if (statusMsg.contains ("ERROR")) {
				controller.onEndProcessing ("ERROR", statusMsg);
			}else if (statusMsg.contains ("Finalizando servidor Ecuapass")) {
				System.out.println (">>> CLIENTE: Finalizando servidor Ecuapass");
				System.exit (0);
			}else if (statusMsg.contains ("Documento no encontrado"))
				controller.onEndProcessing ("ERROR", statusMsg);
			else if (statusMsg.contains ("SERVER: ALERTA:")) {
				// Display to user'ALERTA' messages 
				statusMsg = statusMsg.split ("ALERTA:")[1];
				TopMessageDialog dialog = new TopMessageDialog (controller.getMainView (), statusMsg);
			} else if (statusMsg.contains ("SERVER: MENSAJE:")) {
				// Display to user'ALERTA' messages 
				// Hide the main frame
				controller.getMainView ().setState (Frame.ICONIFIED);
				statusMsg = statusMsg.split ("MENSAJE:")[1];
				TopMessageDialog dialog = new TopMessageDialog (controller.getMainView (), statusMsg);
			} else if (statusMsg.contains ("Server is running on port")) {
				String portString = statusMsg.split ("::")[1].trim ();
				int urlPortNumber = Integer.parseInt (portString);
				this.serverUrl = this.getServerUrl (urlPortNumber); // Server address and entry point	
				controller.onServerRunning ();
			} else if (statusMsg.contains ("FEEDBACK:")) {	// Server sends feedback
				String docFilepath = statusMsg.split ("'")[1];
				controller.onSendFeedback (docFilepath);
			} else if (statusMsg.contains ("Problemas procesando documento"))
				controller.onEndProcessing ("ERROR", statusMsg);
			else {
				controller.out ("Respuesta servidor no soportada");
			}
		}
	}

	// Copy input files in 'DocModel' to new working dir with new docType name
	public String copyDocToProjectsDir (DocRecord docRecord) {
		docModel.createFolder (DocModel.projectsPath);
		File sourceFilepath = new File (docRecord.docFilepath);
		File destFilepath = new File (DocModel.projectsPath, docRecord.docTypeFilename);
		Utils.copyFile (sourceFilepath.toString (), destFilepath.toString ());
		String docFilepath = Utils.convertToOSPath (destFilepath.toString ());
		return docFilepath;
	}

	// Copy emmbeded resources	(programs and images) to temporal dir
	public boolean copyResourcesToTempDir () {
		docModel.createFolder (docModel.temporalPath + "/" + "resources");
		if (this.copyResourcesFromJarToTempDir ())
			controller.out ("Copiando recursos desde un JAR.");
		else if (this.copyResourcesFromPathToTempDir ())
			controller.out ("Copiando recursos desde un PATH.");
		else {
			JOptionPane.showMessageDialog (null, "No se pudieron copiar los recursos!");
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

	//-----------------------------------------------------------------		
	// Swing worker functions
	//------------------------------------------------------------------
	// Create command list according to the OS, service, and parameters
	public void createExecutableCommand () {
		String OS = System.getProperty ("os.name").toLowerCase ();
		String separator = OS.contains ("windows") ? "\\" : "/";

		// For testing: python .py, for production: windows .exe
		String exeProgram = "ecuapass_server" + separator + "ecuapass_server.exe";
		String pyProgram = "ecuserver" + separator + "ecuapass_server.py";

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

	@Override
// Called when the server background thread finishes execution
	protected void done () {
		try {
			System.out.println (">>> Servidor finalizado...");
			String statusMsg = (String) get ();
			System.out.println (statusMsg);

		} catch (InterruptedException | ExecutionException ex) {
			Logger.getLogger (ServerWorker.class
				.getName ()).log (Level.SEVERE, null, ex);
		}
	}

	// Start the server process and publish its messages
	@Override
	protected String doInBackground () throws Exception {
		this.createExecutableCommand ();
		if (this.copyResourcesToTempDir () == false)
			return ("ERROR: No se pudo copiar recursos.");

		controller.out ("CLIENTE: comando del servidor: " + commandList);
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

	// Main 
	public static void main (String[] args) {
		try {
			MainController ctr = new MainController ();
			ServerWorker rw = new ServerWorker (new Controller (), new DocModel ());
			rw.execute ();

		} catch (Exception ex) {
			Logger.getLogger (ServerWorker.class
				.getName ()).log (Level.SEVERE, null, ex);
		}
	}
}
