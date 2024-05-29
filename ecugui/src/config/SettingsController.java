package config;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import documento.DocModel;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.logging.Level;
import java.util.logging.Logger;
import javax.swing.JFrame;
import javax.swing.JOptionPane;
import main.Controller;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;
import widgets.InitialSettingsDialog;

public class SettingsController {

	String runningPath = DocModel.runningPath;
	InitialSettingsDialog initialSettingsDialog;
	public FeedbackView feedbackView;
	Controller controller;

	public SettingsController (Controller controller) {
		this.controller = controller;
		feedbackView = new FeedbackView ();
		feedbackView.setController (this);
	}

	public void onSendFeedback (String feedbackText) {
		controller.onSendFeedback (feedbackText);
	}

	// First time initialization. Set "empresa" name for  cloud document models
	public String initSettings (JFrame parent) {
		String companyName = null;
		JSONObject settings = this.readSettings ();
		if (settings == null) {// Load nombreEmpresa name
			initialSettingsDialog = new InitialSettingsDialog (parent);
			initialSettingsDialog.setController (this);
			initialSettingsDialog.startProcess ();
			settings = this.readSettings ();
		}
		this.feedbackView.setSettings (settings);
		companyName = (String) settings.get ("empresa");
		System.out.println (">>>>>>>>> Empresa: " + companyName + " <<<<<<<<<<");
		return companyName;
	}

	public void onSaveSettings (JSONObject settings) {
		if (this.checkForValidSettings (settings) == false)
			return;

		if (this.initialSettingsDialog != null)
			this.initialSettingsDialog.endProcess ();

		this.writeSettings (settings);
	}

	public JSONObject readSettings () {
		try {
			File settingsFile = new File (runningPath + "/settings.txt");
			System.out.println (">>> Settings file: " + settingsFile);
			if (settingsFile.exists ()) {
				JSONParser parser = new JSONParser ();
				JSONObject settings = (JSONObject) parser.parse (new FileReader (settingsFile));
				settings = this.updateSettings (settings);
				return settings;
			}
		} catch (FileNotFoundException ex) {
			Logger.getLogger (SettingsController.class.getName ()).log (Level.SEVERE, null, ex);
		} catch (IOException | ParseException ex) {
			Logger.getLogger (SettingsController.class.getName ()).log (Level.SEVERE, null, ex);
		}
		return null;
	}

	// Create new 'settings.json' file, if it is old
	public JSONObject updateSettings (JSONObject settings) {
		String empresa = ((String) settings.get ("empresa")).toUpperCase ();
		if (empresa.equals ("BYZA") && !settings.containsKey ("codebin_user")) {
			settings.clear ();
			settings.put ("empresa", "BYZA");
			settings.put ("codebin_url", "https://byza.corebd.net");
			settings.put ("codebin_user", "GRUPO BYZA");
			settings.put ("codebin_password", "GrupoByza2020*");
			settings.put ("NORMAL_PAUSE", "0.05");
			settings.put ("SLOW_PAUSE", "0.5");
			settings.put ("FAST_PAUSE", "0.01");
			this.writeSettings (settings);
		} else if (empresa.equals ("NTA") && !settings.containsKey ("codebin_user2")) {
			settings.clear ();
			settings.put ("empresa", "NTA");
			settings.put ("codebin_url", "https://nta.corebd.net");
			settings.put ("codebin_user", "MARCELA");
			settings.put ("codebin_password", "NTAIPIALES2023");
			settings.put ("codebin_user2", "KARLA");
			settings.put ("codebin_password2", "NTAIPIALES2023");
			settings.put ("NORMAL_PAUSE", "0.05");
			settings.put ("SLOW_PAUSE", "0.5");
			settings.put ("FAST_PAUSE", "0.01");
			this.writeSettings (settings);
		}
		return settings;
	}

	public void writeSettings (JSONObject settings) {
		File settingsFile = new File (runningPath + "/settings.txt");
		Gson gson = new GsonBuilder ().setPrettyPrinting ().create ();
		String jsonString = gson.toJson (settings);

		// Write the JSON string to a file
		try (FileWriter fileWriter = new FileWriter (settingsFile)) {
			System.out.println (">>> Guardando archivo de configuracion: " + settingsFile);
			fileWriter.write (jsonString);
		} catch (Exception e) {
			e.printStackTrace ();
		}
	}

	public void onCancelSettings () {
		if (this.initialSettingsDialog != null)
			System.exit (0);
	}

	public boolean checkForValidSettings (JSONObject settings) {
		if (settings.get ("empresa").equals ("")) {
			JOptionPane.showMessageDialog (null, "Nombre de empresa inválido");
			return false;
		}
		if (settings.get ("codebin_url").equals ("")) {
			JOptionPane.showMessageDialog (null, "URL Codebin inválido");
			return false;
		}
		if (settings.get ("codebin_user").equals ("")) {
			JOptionPane.showMessageDialog (null, "Usuario Codebin inválido");
			return false;
		}
		if (settings.get ("codebin_password").equals ("")) {
			JOptionPane.showMessageDialog (null, "Clave Codebin inválido");
			return false;
		}
		if (settings.containsKey ("codebin_user2") && settings.get ("codebin_user2").equals ("")) {
			JOptionPane.showMessageDialog (null, "Usuario2 Codebin inválido");
			return false;
		}
		if (settings.containsKey ("codebin_password2") && settings.get ("codebin_password2").equals ("")) {
			JOptionPane.showMessageDialog (null, "Clave2 Codebin inválido");
			return false;
		}

		return true;
	}

	// Get value from "settings.json" file located in "runningPath"
	public String getSettingsValue (String key) {
		File settingsFile = new File (this.runningPath + "/settings.txt");

		String value = null;
		try {
			JSONParser parser = new JSONParser ();
			JSONObject jsonObj = (JSONObject) parser.parse (new FileReader (settingsFile));
			value = (String) jsonObj.get (key);

		} catch (IOException | ParseException ex) {
			Logger.getLogger (SettingsController.class
				.getName ()).log (Level.SEVERE, null, ex);
		}
		return value;
	}
}
