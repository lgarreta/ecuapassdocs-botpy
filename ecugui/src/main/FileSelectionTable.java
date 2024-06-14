package main;

import documento.DocRecord;
import documento.DocRecordCartaporte;
import documento.DocRecordDeclaracion;
import documento.DocRecordManifiesto;
import java.awt.BorderLayout;
import java.awt.Component;
import java.awt.Dimension;
import java.awt.Font;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.io.File;
import java.io.IOException;
import java.util.Map;
import javax.swing.AbstractCellEditor;
import javax.swing.JComboBox;
import javax.swing.JFrame;
import javax.swing.JOptionPane;
import javax.swing.JTable;
import javax.swing.SwingUtilities;
import javax.swing.event.ListSelectionEvent;
import javax.swing.event.ListSelectionListener;
import javax.swing.table.DefaultTableModel;
import javax.swing.table.TableCellEditor;
import org.json.simple.parser.ParseException;

public class FileSelectionTable extends javax.swing.JPanel {

	@SuppressWarnings("unchecked")
  // <editor-fold defaultstate="collapsed" desc="Generated Code">//GEN-BEGIN:initComponents
  private void initComponents() {

    jScrollPane1 = new javax.swing.JScrollPane();
    table = new javax.swing.JTable();

    setLayout(new java.awt.BorderLayout());

    table.setModel(new javax.swing.table.DefaultTableModel(
      new Object [][] {

      },
      new String [] {
        "Tipo", "Nombre", "Ruta"
      }
    ));
    jScrollPane1.setViewportView(table);

    add(jScrollPane1, java.awt.BorderLayout.CENTER);
  }// </editor-fold>//GEN-END:initComponents
  // Variables declaration - do not modify//GEN-BEGIN:variables
  private javax.swing.JScrollPane jScrollPane1;
  private javax.swing.JTable table;
  // End of variables declaration//GEN-END:variables

	Controller controller;
	String id;
	DefaultTableModel tableModel;
	int currentRowSelected;
	Map recordsMap;    // Dictionary with docFilename and its record

	public FileSelectionTable () {
		initComponents ();
		tableModel = (DefaultTableModel) table.getModel ();
		setDoctypeComboBoxToTable ();
		recordsMap = new java.util.LinkedHashMap<String, DocRecord> ();
		addListeners ();
	}

	public void disableEdition () {
		String[] columnNames = {"Tipo", "Documento", "Ruta"};

		// Create the custom table model with all cells set as non-editable        
		tableModel = new DisableTableModel (columnNames, 0);
		table.setModel (tableModel);
	}

	public void setController (Controller controller, String id) {
		this.controller = controller;
		this.id = id;
	}

	// Add record values to table of selected files for processing
	public void addNoProcessedRecord (DocRecord record) {
		File docFile = new File (record.docFilepath);
		String docType = record.docType != null ? record.docType : "Seleccione...";
		Object[] items = new Object[]{docType, docFile.getName (), docFile.getPath ()};
		tableModel.addRow (items);
		recordsMap.put (docFile.getName (), record);
	}

	// Add record values to table of selected files for processing
	// Add record to both table model and map
	public void addProcessedRecord (DocRecord record) {
		try {
			DocRecord docRecord = null;
			if (record.docType.equals ("CARTAPORTE"))
				docRecord = new DocRecordCartaporte (record);
			else if (record.docType.equals ("MANIFIESTO"))
				docRecord = new DocRecordManifiesto (record);
			else if (record.docType.equals ("DECLARACION"))
				docRecord = new DocRecordDeclaracion (record);
			else {
				JOptionPane.showMessageDialog (this, "Adicionando a la tabla un tipo de documento desconocido: " + record.docType);
				return;
			}
			// Add info to table
			File docFile = new File (record.docFilepath);
			Object[] items = new Object[]{record.docType, docFile.getName (), docFile.getPath ()};
			tableModel.addRow (items);

			String filename = new File (docRecord.docFilepath).getName ();
			recordsMap.put (filename, docRecord);
		} catch (IOException | ParseException ex) {
			ex.printStackTrace ();
			this.controller.out ("No se pudo adicionar el documento: " + record.docFilepath);
		}
	}

	// Remove a row from the table given the filename (column 1)
	public void removeRecord (String docFilename) {
		int numRows = tableModel.getRowCount ();
		for (int row = 0; row < numRows; row++) {
			Object cellValue = tableModel.getValueAt (row, 1); // Assuming you want to check the first column
			if (cellValue != null && cellValue.toString ().equals (docFilename)) {
				tableModel.removeRow (row);
				recordsMap.remove (docFilename);
				break; // Once you remove the row, exit the loop
			}
		}
	}

	public DocRecord getRecordAt (int row) {
		String docFilename = getFileAt (row, 1);
		DocRecord docRecord = (DocRecord) recordsMap.get (docFilename);
		return (docRecord);
	}

	public String getFileAt (int row, int col) {
		String filePath = table.getValueAt (row, col).toString ();
		return (filePath);
	}

	public String getCurrentFileSelected () {
		return (getFileAt (currentRowSelected, 1));
	}
	public String getCurrentFilePathSelected () {
		return (getFileAt (currentRowSelected, 2));
	}
	

	public int getCurrentRowSelected () {
		return (currentRowSelected);
	}

	public void addListeners () {
		table.getSelectionModel ().addListSelectionListener (new ListSelectionListener () {
			public void valueChanged (ListSelectionEvent e) {
				if (!e.getValueIsAdjusting ()) {
					int row = table.getSelectedRow ();
					int col = table.getSelectedColumn ();
					if (row >= 0 && col >= 0) {
						currentRowSelected = row;
						controller.onTableCellSelected (row, col, id);
					}
				}
			}
		});

		table.addMouseListener (new MouseAdapter () {
			@Override
			public void mouseClicked (MouseEvent e) {
				if (e.getClickCount () == 2) {
					int row = table.getSelectedRow ();
					int column = table.getSelectedColumn ();
					String pdfFilePath  = getCurrentFilePathSelected ();
					Utils.openPDF (pdfFilePath);
				}
			}
		});
	}

	public void setDoctypeComboBoxToTable () {
		DefaultTableModel model = new DefaultTableModel (5, 3);
		//for (int row = 0; row < model.getRowCount (); row++) {
		//	for (int col = 0; col < model.getColumnCount (); col++) {
		//		model.setValueAt ("Select an option", row, col);
		//	}
		//}

		table.setModel (tableModel);

		table.getColumnModel ().getColumn (0).setCellEditor (new ComboBoxCellEditor ());

		// Add a listener to detect changes
		table.getModel ().addTableModelListener (e -> {
			int row = e.getFirstRow ();
			int col = e.getColumn ();
			if (col == 0) {
				Object selectedValue = table.getValueAt (row, col);
			}
		});
	}

	public void selectFirstRow () {
		if (tableModel.getRowCount () > 0)
			table.changeSelection (0, 0, false, false);
	}

	public void clear () {
		tableModel.setRowCount (0);
	}

	public JTable getTable () {
		return table;
	}

	public static void main (String[] args) {
		SwingUtilities.invokeLater (() -> {
			JFrame frame = new JFrame ("Test simple input view");
			frame.getContentPane ().setLayout (new BorderLayout ());
			frame.setDefaultCloseOperation (JFrame.EXIT_ON_CLOSE);

			FileSelectionTable fst = new FileSelectionTable ();
			fst.addProcessedRecord (new DocRecord ("/home/lg/AAA/a01/cartaporte-EcoInversiones.png"));
			frame.getContentPane ().add (fst, BorderLayout.CENTER);
			frame.setPreferredSize (new Dimension (600, 700));
			frame.pack ();
			frame.setVisible (true);
		});

	}

}

//----------------------------------------------------------
// Custom Org_ComboBoxCellEditor for selectin document type
//----------------------------------------------------------
class ComboBoxCellEditor extends AbstractCellEditor implements TableCellEditor {

	private JComboBox<String> comboBox;

	public ComboBoxCellEditor () {
		comboBox = new JComboBox<> ();
		comboBox.addItem ("CARTAPORTE");
		comboBox.addItem ("MANIFIESTO");
		comboBox.addItem ("DECLARACION");
		comboBox.setSelectedIndex (0);
		comboBox.setFont (new Font ("Arial", Font.PLAIN, 10));

		comboBox.addActionListener (new ActionListener () {
			@Override
			public void actionPerformed (ActionEvent e) {
				// Notify the cell editor that editing is done when an item is selected
				stopCellEditing ();
			}
		});
	}

	@Override
	public Component getTableCellEditorComponent (JTable table, Object value, boolean isSelected, int row, int column) {
		comboBox.setSelectedItem (value);
		return comboBox;
	}

	@Override
	public Object getCellEditorValue () {
		return comboBox.getSelectedItem ();
	}
}

class DisableTableModel extends DefaultTableModel {

	public DisableTableModel (Object[] columnNames, int rowCount) {
		super (columnNames, rowCount);
	}

	@Override
	public boolean isCellEditable (int row, int column) {
		return false;
	}
}
