package workers;


import java.io.IOException;

public class RunPythonScript {

	public static void run () {
		String pythonScriptPath = "z:\\ecusrv\\gui_activate.py";
		try {
			ProcessBuilder processBuilder = new ProcessBuilder ("cmd", "/c", "python", pythonScriptPath);
			processBuilder.redirectErrorStream (true);
			Process process = processBuilder.start ();
			int exitCode = process.waitFor (); 	// Wait for the process to complete (optional)

			// Print the exit code (0 indicates success)
			System.out.println ("Python script exited with code: " + exitCode);
		} catch (IOException | InterruptedException e) {
			//e.printStackTrace ();
			System.out.println  (">>> ERROR: No se pudo ejecutar script externo 'gui_activate.py'." );
		}
	}
}
