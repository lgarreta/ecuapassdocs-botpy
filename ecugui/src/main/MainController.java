package main;

import config.SettingsController;
import config.FeedbackView;
import documento.DocModel;
import documento.DocRecord;
import java.awt.Component;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import widgets.ImageViewLens;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.logging.Level;
import java.util.logging.Logger;
import javax.swing.JFrame;
import javax.swing.JOptionPane;
import javax.swing.JTabbedPane;
import javax.swing.JTextField;
import javax.swing.Timer;
import javax.swing.UIManager;
import javax.swing.WindowConstants;
import org.json.simple.parser.ParseException;
import results.ResultsController;
import widgets.ProgressDialog;
import workers.ServerWorker;

public class MainController extends Controller {

	String appRelease = "0.87";
	DocModel doc;             // Handles invoice data: selected, processed, and no procesed
	MainView mainView;
	InputsView inputsView;
	FeedbackView feedbackView;
	JTabbedPane tabsPanel;
	ImageViewLens imageView;
	//ResultsView resultsView;
	ResultsController resultsController;
	ServerWorker serverWorker;          // Client for sending messages to python server
	ProgressDialog progressDialog;     // Dialog showed when document processing starts

	//SettingsController settingsController; // Initial configuration parameters
	SettingsController configController;
	Timer timer;
	// Current selected file from FileChooser
	File selectedFile = null;

	public MainController () {
		try {
			doc = new DocModel ();
			doc.initGlobalPaths ();
			initializeComponents ();
		} catch (Exception ex) {
			ex.printStackTrace ();
			Logger.getLogger (MainController.class.getName ()).log (Level.SEVERE, null, ex);
		}
		out (">>>>>>>>>>>>>>>> GUI version: " + appRelease + " <<<<<<<<<<<<<<<<<<<<");
	}

	public JFrame getMainView () {
		return mainView;
	}

	// Add the views to this Frame
	private void initializeComponents () {
		// Main views
		mainView = new MainView ();
		mainView.setController (this);
		mainView.setVisible (true);
		mainView.setDefaultCloseOperation (WindowConstants.DO_NOTHING_ON_CLOSE);

		// Inital configuration settings
		configController = new SettingsController (this);
		configController.initSettings (mainView);
		DocModel.companyName = configController.getSettingsValue ("empresa");
		feedbackView = configController.feedbackView;

		// Init InputsView
		inputsView = new InputsView ();
		inputsView.setController (this);
		tabsPanel = mainView.createTabs ();
		tabsPanel.addTab ("Entradas:", inputsView);
		tabsPanel.addTab ("Mensajes", feedbackView);

		// Get components from views
		imageView = inputsView.getImageView ();

		// Initialize dirs
		String location = AppPrefs.FileLocation.get (System.getProperty ("user.home"));
		inputsView.setSelectedDir (location);

		doc.printGlobalPaths (this);

		// Server worker
		serverWorker = new ServerWorker (this, doc);
		if (serverWorker.copyResourcesToTempDir () == false) {
			out ("ERROR: No se pudo copiar recursos.");
			return;
		}
		//serverWorker.getServerUrl ();
		// serverWorker.execute ();	
	}

	// Start document processing after button pressed in InpusView
	@Override
	public void onStartProcessing () {
		// Start resultsController
		if (resultsController != null)
			tabsPanel.remove (resultsController.resultsView);

		resultsController = new ResultsController (this, doc, serverWorker);
		tabsPanel.addTab ("Resultados", resultsController.resultsView);

		// Call to server to start processing documents
		serverWorker.copyDocToProjectsDir (doc.currentRecord);
		DocRecord docRecord = doc.currentRecord;

		String docFilepath = Utils.convertToOSPath (docRecord.docFilepath);
		serverWorker.startProcess ("doc_processing", docFilepath, DocModel.runningPath);
		progressDialog = new ProgressDialog (mainView);
		progressDialog.setController (this);
		progressDialog.startProcess ();
	}

	// Selected docFile in  FileChooser or table from InputsFilesViewProjects
	@Override
	public void onFileSelected (File docFilepath) {
		String docNumber = Utils.extractDocNumber (docFilepath.getName ());
		String docType = Utils.getDocumentTypeFromFilename (docFilepath.getName ());
		if (inputsView.checkDocNumberType (docNumber, docType)) {
			selectedFile = docFilepath;
			inputsView.setDocNumberType (docNumber, docType);
			imageView.showImage (docFilepath);
		}
	}

	@Override
	public boolean processSelectedDocument () {
		try {
			String docNumber = inputsView.getDocNumber ();
			if (Utils.extractDocNumber (docNumber) == null) {
				JOptionPane.showMessageDialog (this.mainView, "Número documento: '" + docNumber + "' inválido.");
				return false;
			}
			String selectedFilename = inputsView.getFileWithDocNumberFromFileChooser (docNumber);
			if (selectedFilename == null) {
				selectedFilename = inputsView.createFilenameFromDocNumber (docNumber);
				String docType = inputsView.getDocType ("LONGNAME");
				selectedFile = new File (selectedFilename);
				doc.currentRecord = new DocRecord (selectedFile.toString (), docType);
			} else {
				selectedFile = new File (selectedFilename);
				doc.currentRecord = new DocRecord (selectedFile.toString ());
			}
			this.onFileSelected (selectedFile);
		} catch (Exception ex) {
			out ("EXCEPCION: No se pudo procesar documento : " + selectedFile.getName ());
			ex.printStackTrace ();
			return false;
		}
		return true;
	}

	// InputsView files selected by FileChooser
	// Send selected file to ready table
	// ServeWorker notification 
	@Override
	public void onEndProcessing (String statusMsg, String text) {
		try {
			if (statusMsg.contains ("EXITO")) {
				String docFilepath = text.split ("'")[1].trim ();
				String jsonFilepath = Utils.getResultsFile (docFilepath, "ECUFIELDS.json");
				String docType = Utils.getDocumentTypeFromFilename (docFilepath);
				DocRecord record = new DocRecord (docType, docFilepath, jsonFilepath);
				doc.currentRecord = record;
				doc.addProcessedRecord (record);
				resultsController.addProcessedRecord (record);
				resultsController.resultsView.selectFirstRecord ();
				tabsPanel.setSelectedIndex (2);
			} else {
				out ("Documento procesado con errores");
				String message = text.split (":", 2)[1].replace ("\\", "\n");
				JOptionPane.showMessageDialog (mainView, message);
			}
		} catch (ParseException | IOException ex) {
			Logger.getLogger (MainController.class.getName ()).log (Level.SEVERE, null, ex);
		} finally {
			progressDialog.endProcess ("document_processed");
		}
	}

	public static void showClosingMessage (String message) {
		Thread thread = new Thread (() -> JOptionPane.showMessageDialog (null, message, "Closing Application", JOptionPane.INFORMATION_MESSAGE));
		thread.start ();
	}

	// Stop cartaporte server if it was opened
	@Override
	public void onWindowClossing () {
		try {
			serverWorker.startProcess ("stop", DocModel.runningPath, null);
			ClosingMessage.showClosingMessage ("Applicación se está cerrando", this.mainView);
			out ("Finalizando Cliente...");
			this.forcedExitWithTimer (5);
		} catch (Exception ex) {
			ex.printStackTrace ();
		}
	}

	//  InputsFileView for "reinitialize" selection
	@Override
	public void onReinitialize () {
		inputsView.clearSelectedFiles ();
		doc.removeAllFiles ();
	}

	// Write message text to both: stdout and FeedbackView
	@Override
	public void out (String s) {
		s = "> " + s;
		System.out.println (s);
		feedbackView.println (s);
	}

	@Override
	public void setWindowState (String state) {
		if (state.equals ("minimize"))
			mainView.setState (JFrame.ICONIFIED);
		else if (state.equals ("restore"))
			mainView.setState (JFrame.NORMAL);
	}

	@Override
	public void onServerRunning (int urlPortNumber) {
		out ("CLIENTE: Escuchando en el puerto: " + urlPortNumber);
		inputsView.enableProcessingButton (true);
	}

	// Send feedback to cloud
	@Override
	public void onSendFeedback (String feedbackText) {

		String zipFilepath = Utils.createTempCompressedFileFromText (feedbackText);
		// Call to server to start processing documents
		System.out.println ("-- " + zipFilepath);
		//serverWorker.startProcess ("send_feedback", zipFilepath, docFilepath);
	}

	public String getAppRelease () {
		return this.appRelease;
	}

	public void onWorkingCountrySelected (String workingCountry) {
		System.out.println ("Country Selected: " + workingCountry);
	}

	// First time initialization. Set "empresa" name for  cloud document models
	void initCurrentWorkingCompany () {
		try {
			File settingsFile = new File (doc.runningPath + "/settings.txt");
			if (settingsFile.exists ()) {// Load comany name
				BufferedReader reader = new BufferedReader (new FileReader (settingsFile));
				doc.companyName = reader.readLine ();
			} else { // Request company name
				JTextField textField = new JTextField ();
				Object[] message = {"Nombre de la empresa:", textField};
				Object[] options = {"Aceptar", "Cancelar"};
				while (true) {
					int option = JOptionPane.showOptionDialog (mainView, message, "Configuración Inicial de la Empresa",
						JOptionPane.DEFAULT_OPTION, JOptionPane.INFORMATION_MESSAGE, null, options, null);

					if (option == JOptionPane.OK_OPTION) {
						doc.companyName = textField.getText ().toUpperCase ();
						if (doc.companyName.matches (doc.companiesString)) {
							BufferedWriter writer = new BufferedWriter (new FileWriter (settingsFile, true));
							writer.write (doc.companyName);
							writer.close ();
							break;
						}
					} else
						System.exit (0);
				}
			}
			out (">>>>>>>>> Empresa: " + doc.companyName + " <<<<<<<<<<");
		} catch (Exception ex) {
			ex.printStackTrace ();
		}
	}

	public void openCreadorDocumentosEcuapass () {
		String url = configController.getSettingsValue ("ecuapassdocs_url");
		serverWorker.startProcess ("open_ecuapassdocs_URL", url, null);

//		String url = this.settingsController.getSettingsValue ("url_creador");
//		try {
//			if (Desktop.isDesktopSupported ()) {
//				Desktop desktop = Desktop.getDesktop ();
//				desktop.browse (new URI (url));
//			} else
//				System.out.println ("Desktop API is not supported on this platform.");
//		} catch (Exception e) {
//			e.printStackTrace ();
//		}
	}

	private void forcedExitWithTimer (int timeInSeconds) {
		timer = new Timer (timeInSeconds * 1000, new ActionListener () {  // Timer fires after 5 seconds
			@Override
			public void actionPerformed (ActionEvent e) {
				out ("Tiempo de finalización terminado..!");
				System.exit (1);
			}
		});
		timer.start (); // Start the timer
	}

	public static void main (String args[]) {

		//Set the Nimbus look and feel
		//<editor-fold defaultstate="collapsed" desc=" Look and feel setting code (optional) ">
		/*
		 * If Nimbus (introduced in Java SE 6) is not available, stay with the
		 * default look and feel. For details see
		 * http://download.oracle.com/javase/tutorial/uiswing/lookandfeel/plaf.html
		 */
		try {
			for (javax.swing.UIManager.LookAndFeelInfo info : javax.swing.UIManager.getInstalledLookAndFeels ()) {
				UIManager.setLookAndFeel (UIManager.getCrossPlatformLookAndFeelClassName ());
				//if ("Nimbus".equals (info.getName ())) {
				//	javax.swing.UIManager.setLookAndFeel (info.getClassName ());
				//	break;
				//}

			}
		} catch (ClassNotFoundException | InstantiationException | IllegalAccessException | javax.swing.UnsupportedLookAndFeelException ex) {
			java.util.logging.Logger.getLogger (MainView.class
				.getName ()).log (java.util.logging.Level.SEVERE, null, ex);
		}
		//</editor-fold>

		//</editor-fold>
		//  Create and display the form
		java.awt.EventQueue.invokeLater (new Runnable () {
			public void run () {
				new MainController ();
			}
		});
	}
}

class ClosingMessage {
	public static void showClosingMessage (String message, Component mainWindow) {
		Thread thread = new Thread (() -> JOptionPane.showMessageDialog (mainWindow, message, "Cerrando aplicación", JOptionPane.INFORMATION_MESSAGE));
		thread.start ();
	}
}
