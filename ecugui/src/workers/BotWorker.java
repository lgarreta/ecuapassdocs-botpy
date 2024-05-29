package workers;

import results.ResultsController;
import java.io.BufferedInputStream;
import java.io.BufferedReader;
import java.io.File;
import java.io.InputStreamReader;
import java.net.URL;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutionException;
import javax.swing.SwingWorker;

/*
 * Execute command line app with parameters. Outputs are sent to controller to
 * show int console and view.
 */
public class BotWorker extends SwingWorker {
	ResultsController controller;
	String docFilepath;
	String workingDir;
	String command;	
	ArrayList<String> cmmList; 

	public BotWorker (ResultsController controller, String docFilepath, String workingDir) {
		this.controller = controller;
		this.docFilepath = docFilepath;
		this.workingDir = workingDir;
		URL commandURL = getClass ().getClassLoader().getResource ("resources/command/cartaporte_Bot.py");
		command = commandURL.getPath ();
		controller.out (">>> BotWorker  Command: " + command);
	}

	protected String doInBackground () throws Exception {
		controller.out ("Running in background: " + cmmList);

		ProcessBuilder processBuilder;
		processBuilder = new ProcessBuilder (cmmList);
		processBuilder.redirectErrorStream (true);
		processBuilder.directory (new File (workingDir));
		Process p = processBuilder.start ();
	
		String lastLine = "";
		BufferedInputStream bis = new BufferedInputStream (p.getInputStream ());
		BufferedReader stdout = new BufferedReader (new InputStreamReader (bis));
		String stdoutLine = "";
		while ((stdoutLine = stdout.readLine ()) != null) {
			lastLine = stdoutLine;
			publish (stdoutLine);
		}
		// Return last line to check if script successfully ended
		return ("robot completed successfully.");
	}

	// Method
	@Override
	protected void process (List chunks) {
		// Handle intermediate results received durint thread execution
		for (Object i : chunks) 
			controller.out ((String) i);
		//String val = (String) chunks.get (chunks.size () - 1);
	}

	// Method
	@Override
	protected void done () {
		// Called when the background thread finishes execution
		try {
			String statusMsg = (String) get ();
			// Check if cloud process ended successfully
			if (statusMsg.contains ("success"))
				controller.onProcessingEnd (docFilepath, "success");
			else
				controller.onProcessingEnd (docFilepath, "failure");
		} catch (InterruptedException | ExecutionException e) {
			e.printStackTrace ();
			controller.onProcessingEnd (docFilepath, "failure");
		}
	}

// Create command list and call thread execution
	public void executeProcess () {
		controller.out (">>> Executing process...");
	
		cmmList = new ArrayList<> ();
		cmmList.addAll (getExecutableShell ());
		cmmList.add (command);
		cmmList.add (docFilepath.toString ());
		this.execute ();
	}

	// Create the shel command  according to the OS
	public ArrayList getExecutableShell () {
		String OSType = System.getProperty ("os.name").toLowerCase ();
		ArrayList<String> shellCmm = new ArrayList ();
		if (OSType.contains ("windows")) {
			controller.out ("Running on a Windows system...");
			shellCmm.add ("cmd.exe");
			shellCmm.add ("/c");
			//cmm.add(0, "py");
		} else {
			shellCmm.add ("python3");
		}
		return (shellCmm);
	}

	public static void main (String[] args) {
		//ResultsController ctr = new ResultsController ();
		//BotWorker rw = new BotWorker (new ResultsController (),
		//	new File ("factura-MariaRosales.jpg"), new File ("/home/lg/AAA/Tests/F3/"));
		//rw.execute ();
	}
}
