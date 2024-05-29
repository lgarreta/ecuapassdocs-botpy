package main;

import documento.DocModel;
import java.awt.Component;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import java.io.File;
import java.util.Arrays;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import javax.swing.JFileChooser;
import javax.swing.JList;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JViewport;
import javax.swing.Timer;
import javax.swing.UIManager;
import javax.swing.filechooser.FileNameExtensionFilter;
import javax.swing.text.AbstractDocument;
import javax.swing.text.AttributeSet;
import javax.swing.text.BadLocationException;
import javax.swing.text.DocumentFilter;
import widgets.ImageViewLens;

public class InputsView extends javax.swing.JPanel {

	@SuppressWarnings("unchecked")
  // <editor-fold defaultstate="collapsed" desc="Generated Code">//GEN-BEGIN:initComponents
  private void initComponents() {

    docNumberGroup = new javax.swing.ButtonGroup();
    filesPanel = new javax.swing.JPanel();
    selectionPanel = new javax.swing.JPanel();
    fileChooser = new javax.swing.JFileChooser();
    controlPanel = new javax.swing.JPanel();
    jLabel1 = new javax.swing.JLabel();
    docNumberPanel = new javax.swing.JPanel();
    docNumberField = new javax.swing.JTextField();
    docNumberCPI = new javax.swing.JRadioButton();
    docNumberMCI = new javax.swing.JRadioButton();
    processDocumentButton = new javax.swing.JButton();
    openEcuapassdocsButton = new javax.swing.JButton();
    imageView = new widgets.ImageViewLens();

    setPreferredSize(new java.awt.Dimension(800, 500));
    setLayout(new java.awt.BorderLayout());

    filesPanel.setPreferredSize(new java.awt.Dimension(600, 800));
    filesPanel.setLayout(new javax.swing.BoxLayout(filesPanel, javax.swing.BoxLayout.Y_AXIS));

    selectionPanel.setPreferredSize(new java.awt.Dimension(580, 700));
    selectionPanel.setLayout(new java.awt.BorderLayout());

    fileChooser.setBackground(new java.awt.Color(204, 255, 204));
    fileChooser.setControlButtonsAreShown(false);
    fileChooser.setAlignmentY(0.1F);
    fileChooser.setAutoscrolls(true);
    fileChooser.setBorder(javax.swing.BorderFactory.createTitledBorder("Selección de facturas:"));
    fileChooser.setMinimumSize(new java.awt.Dimension(442, 200));
    fileChooser.setMultiSelectionEnabled(true);
    selectionPanel.add(fileChooser, java.awt.BorderLayout.CENTER);

    controlPanel.setBackground(new java.awt.Color(204, 255, 204));
    controlPanel.setBorder(javax.swing.BorderFactory.createLineBorder(new java.awt.Color(0, 0, 0)));

    jLabel1.setText("<html>  Seleccione o digite el<br>número de documento:</html>");
    jLabel1.setOpaque(true);
    controlPanel.add(jLabel1);

    docNumberPanel.setBorder(javax.swing.BorderFactory.createLineBorder(new java.awt.Color(0, 0, 0)));
    docNumberPanel.setPreferredSize(new java.awt.Dimension(220, 70));
    docNumberPanel.setRequestFocusEnabled(false);

    docNumberField.setFont(new java.awt.Font("DejaVu Sans Mono", 0, 18)); // NOI18N
    docNumberField.setHorizontalAlignment(javax.swing.JTextField.CENTER);
    docNumberField.setPreferredSize(new java.awt.Dimension(190, 30));
    docNumberPanel.add(docNumberField);

    docNumberGroup.add(docNumberCPI);
    docNumberCPI.setText("CartaPorte");
    docNumberPanel.add(docNumberCPI);

    docNumberGroup.add(docNumberMCI);
    docNumberMCI.setText("Manifiesto");
    docNumberPanel.add(docNumberMCI);

    controlPanel.add(docNumberPanel);

    processDocumentButton.setBackground(new java.awt.Color(255, 255, 0));
    processDocumentButton.setText("<html>Procesar</html>");
    processDocumentButton.addActionListener(new java.awt.event.ActionListener() {
      public void actionPerformed(java.awt.event.ActionEvent evt) {
        processDocumentButtonActionPerformed(evt);
      }
    });
    controlPanel.add(processDocumentButton);

    openEcuapassdocsButton.setBackground(new java.awt.Color(153, 255, 255));
    openEcuapassdocsButton.setText("<html>Abrir<br>EcuapassDocs</html>");
    openEcuapassdocsButton.addActionListener(new java.awt.event.ActionListener() {
      public void actionPerformed(java.awt.event.ActionEvent evt) {
        openEcuapassdocsButtonActionPerformed(evt);
      }
    });
    controlPanel.add(openEcuapassdocsButton);

    selectionPanel.add(controlPanel, java.awt.BorderLayout.PAGE_START);

    filesPanel.add(selectionPanel);

    add(filesPanel, java.awt.BorderLayout.WEST);

    imageView.setBackground(java.awt.Color.orange);
    imageView.setMaximumSize(new java.awt.Dimension(600, 800));
    add(imageView, java.awt.BorderLayout.CENTER);
  }// </editor-fold>//GEN-END:initComponents

  private void openEcuapassdocsButtonActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_openEcuapassdocsButtonActionPerformed
		// TODO add your handling code here
		controller.openCreadorDocumentosEcuapass ();
  }//GEN-LAST:event_openEcuapassdocsButtonActionPerformed

  private void processDocumentButtonActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_processDocumentButtonActionPerformed
		// Reinitialize views
		//controller.onReinitialize ();
		//			controller.onProcessDocument ();
		if (controller.processSelectedDocument ())
			controller.onStartProcessing ();
  }//GEN-LAST:event_processDocumentButtonActionPerformed

  // Variables declaration - do not modify//GEN-BEGIN:variables
  private javax.swing.JPanel controlPanel;
  private javax.swing.JRadioButton docNumberCPI;
  private javax.swing.JTextField docNumberField;
  private javax.swing.ButtonGroup docNumberGroup;
  private javax.swing.JRadioButton docNumberMCI;
  private javax.swing.JPanel docNumberPanel;
  private javax.swing.JFileChooser fileChooser;
  private javax.swing.JPanel filesPanel;
  private widgets.ImageViewLens imageView;
  private javax.swing.JLabel jLabel1;
  private javax.swing.JButton openEcuapassdocsButton;
  private javax.swing.JButton processDocumentButton;
  private javax.swing.JPanel selectionPanel;
  // End of variables declaration//GEN-END:variables

	Controller controller;

	public InputsView () {
		initComponents ();
		modifyFileChooser ();
		initDocNumberField ();

		//if (DocModel.companyName.equals ("BYZA")==false)
		this.openEcuapassdocsButton.setVisible (DocModel.SHOW_DOCS_BUTTONS);
	}

	public void setController (Controller controller) {
		this.controller = controller;
		addFileChooserListeners ();
		fileChooser.setSelectedFile (null);
	}

	public void addFileChooserListeners () {
		// Add listener for file selection (for preview)
		fileChooser.addPropertyChangeListener (new PropertyChangeListener () {
			@Override
			public void propertyChange (PropertyChangeEvent evt) {
				if (JFileChooser.SELECTED_FILE_CHANGED_PROPERTY.equals (evt.getPropertyName ())) {
					File selectedFile = fileChooser.getSelectedFile ();
					if (selectedFile != null && !selectedFile.isDirectory ())
						controller.onFileSelected (fileChooser.getSelectedFile ());
				}
			}
		});

		// Add a timer to refres dir content
		Timer timer = new Timer (5000, new ActionListener () { // Update every 5 seconds
			@Override
			public void actionPerformed (ActionEvent e) {
				fileChooser.rescanCurrentDirectory ();
			}
		});
		timer.start ();
	}

	private static JList getFileList (JFileChooser fileChooser) {
		Component[] components = fileChooser.getComponents ();
		for (Component component : components) {
			if (component instanceof JScrollPane) {
				JScrollPane scrollPane = (JScrollPane) component;
				JViewport viewport = scrollPane.getViewport ();
				Component[] viewportComponents = viewport.getComponents ();
				for (Component c : viewportComponents) {
					if (c instanceof JList)
						return (JList) c;
				}
			}
		}
		return null;
	}

	private void modifyFileChooser () {
		// Changes FileChooser text from english to spanish 
		UIManager.put ("FileChooser.fileNameLabelText", "Archivos");
		UIManager.put ("FileChooser.filesOfTypeLabelText", "Tipos de Archivos");
		UIManager.put ("FileChooser.cancelButtonText", "Deseleccionar ");
		UIManager.put ("FileChooser.openButtonText", "Seleccionar ");
		UIManager.put ("FileChooser.lookInLabelText", "Buscar");

		UIManager.put ("FileChooser.readOnly", Boolean.TRUE);
		fileChooser.updateUI ();

		// Show only images and pdfs  in FileChooser
		fileChooser.setAcceptAllFileFilterUsed (false);
		FileNameExtensionFilter filter = new FileNameExtensionFilter ("Images/pdf files", "jpg", "png", "pdf");
		fileChooser.addChoosableFileFilter (filter);

		// Hide default accept/cancel buttons
		hideFileSelComponents (fileChooser.getComponents ());

	}

	// DocNumber functions
	private void initDocNumberField () {
		((AbstractDocument) docNumberField.getDocument ()).setDocumentFilter (new UppercaseDocumentFilter ());
	}

	public void resetDocNumberType () {
		this.docNumberField.setText ("");
		this.docNumberGroup.clearSelection ();
	}

	public void setDocNumberType (String docNumber, String docType) {
		this.docNumberField.setText (docNumber);
		if (docType.equals ("CARTAPORTE"))
			this.docNumberCPI.setSelected (true);
		else if (docType.equals ("MANIFIESTO"))
			this.docNumberMCI.setSelected (true);
	}

	public boolean checkDocNumberType () {
		String docNumber = this.docNumberField.getText ();
		String docType = this.docNumberCPI.isSelected () ? "CARTAPORTE" : null;
		docType = this.docNumberMCI.isSelected () ? "MANIFIESTO" : docType;
		return this.checkDocNumberType (docNumber, docType);
	}

	public boolean checkDocNumberType (String docNumber, String docType) {
		if (docNumber == null) {
			JOptionPane.showMessageDialog (controller.getMainView (), "Número de documento inválido.");
			this.resetDocNumberType ();
			return false;
		}
		if (docType == null) {
			JOptionPane.showMessageDialog (this, "Seleccione el tipo de documento.");
			return false;
		}
		//this.setDocNumberType (docNumber, docType);
		return true;
	}

	public String getDocNumber () {
		return this.docNumberField.getText ();
	}

	public String getDocType (String shortName) {
		boolean docTypeCPI = this.docNumberCPI.isSelected ();
		boolean docTypeMCI = this.docNumberMCI.isSelected ();
		if (docTypeCPI)
			return shortName.equals ("SHORTNAME") ? "CPI" : "CARTAPORTE";
		else if (docTypeMCI)
			return shortName.equals ("SHORTNAME") ? "MCI" : "MANIFIESTO";
		else
			return null;
	}

	
	public String createFilenameFromDocNumber (String docNumber) throws Exception {
		if (this.checkDocNumberType ()) {
			String filename = "DUMMY-" + getDocType ("SHORTNAME") + "-" + docNumber + ".pdf";
			return filename;
		} else
			throw new Exception ("No se pudo crear nombre de archivo CODEBIN");
	}

// Hide last file panel from JFileChooser component
	private void hideFileSelComponents (Component[] components) {
		// traverse through the components
		for (int i = 0; i < components.length; i++) {
			Component comp = components[i];
			if (comp instanceof JPanel) // traverse recursively
				hideFileSelComponents (((JPanel) comp).getComponents ());
			else if (comp.toString ().contains ("Archivos"))
				comp.getParent ().getParent ().setVisible (false); // hide i
		}
	}

	public ImageViewLens getImageView () {
		return (imageView);
	}

	// Set FileChooser to selectedDir
	public void setSelectedDir (String selectedDir) {
		fileChooser.setCurrentDirectory (new File (selectedDir));
	}

	public File[] getSelectedFiles () {
		File[] selectedFiles = fileChooser.getSelectedFiles ();
		for (File fi : selectedFiles) {
			System.out.println (fi.toString ());
		}
		return (selectedFiles);
	}

	public void selectAllFiles () {
		File[] allFiles = this.getAllFilesFromChooser ();
		//int fileCount = fileChooser.getCurrentDirectory ().listFiles ().length;
		//File[] allFiles = fileChooser.getCurrentDirectory ().listFiles ();
		fileChooser.setSelectedFiles (allFiles);
	}

	public String getFileWithDocNumberFromFileChooser (String substring) {
		File[] files = fileChooser.getCurrentDirectory ().listFiles ();		
		String regex = substring + "\\b";
		Pattern pattern = Pattern.compile (regex);
		for (File file : files) {
			Matcher matcher = pattern.matcher(file.getName ());
			if (matcher.find ()) {
				fileChooser.setSelectedFile (file);
				return file.toString ();
			}
		}
		return null;
	}

	public File[] getAllFilesFromChooser () {
		fileChooser.setAcceptAllFileFilterUsed (false);
		FileNameExtensionFilter filter = new FileNameExtensionFilter ("Images/pdf files", "jpg", "png", "pdf");
		fileChooser.addChoosableFileFilter (filter);
		File wd = fileChooser.getCurrentDirectory ();

		java.io.FileFilter ioFilter = file -> filter.accept (file);
		File[] allFiles = wd.listFiles (ioFilter);

		return (allFiles);
	}

	public void clearSelectedFile () {
		fileChooser.setSelectedFile (null);
		this.resetDocNumberType ();
	}

	public void clearSelectedFiles () {
		File[] selFiles = fileChooser.getSelectedFiles ();
		if (selFiles.length == 1)
			return;

		File[] allFiles = this.getAllFilesFromChooser ();
		File[] noFiles = Arrays.copyOfRange (allFiles, 0, 1);
		File selFile = fileChooser.getSelectedFile ();
		if (noFiles.length > 0)
			fileChooser.setSelectedFiles (noFiles);
	}

	public void enableProcessingButton (boolean value) {
		this.processDocumentButton.setEnabled (value);
	}
}

//---------------------------------------------------------------------------------------
// Class for allow only upercase to DocNumberField
//---------------------------------------------------------------------------------------
class UppercaseDocumentFilter extends DocumentFilter {

	@Override
	public void replace (DocumentFilter.FilterBypass fb, int offset, int length, String str, AttributeSet attr)
		throws BadLocationException {
		super.replace (fb, offset, length, str != null ? str.toUpperCase () : null, attr);
	}
}
