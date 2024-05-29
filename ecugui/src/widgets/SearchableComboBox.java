package widgets;

import documento.DocModel;
import main.Utils;
import java.awt.Color;
import java.awt.Component;
import java.awt.Font;
import java.awt.KeyboardFocusManager;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.KeyAdapter;
import javax.swing.*;
import java.awt.event.KeyEvent;
import java.awt.event.KeyListener;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;

// Component with search by pressing a key and custom background
public class SearchableComboBox extends JComboBox {

	String[] originalItems;
	Map<String, String[]> subItemsMap;         // For derived combo boxes (e.g. ciudadas, aduanas depending of pais)

	public SearchableComboBox () {
		super ();
	}

	// Default combo box
	public SearchableComboBox (String[] items) {
		super (items);
		this.setFont (new Font ("sansserif", 0, 12));
		originalItems = items;

		addKeyListener (new KeyAdapter () {
			@Override
			public void keyTyped (KeyEvent e) {
				if (e.getKeyChar () != KeyEvent.VK_ENTER) {
					String letter = "" + e.getKeyChar ();
					SwingUtilities.invokeLater (() -> filterItems (letter.toUpperCase ()));
				}
			}
			@Override
			public void keyPressed (KeyEvent e) {
				if (e.getKeyCode () == KeyEvent.VK_ENTER) {
					e.consume (); // Consume the Enter key event
					KeyboardFocusManager manager = KeyboardFocusManager.getCurrentKeyboardFocusManager ();
					manager.focusNextComponent ();
				}
			}
		});
	}

// Constructor for comboBox depending of a parent (e.g. "Ciudades" depends from "Pais")	
	public SearchableComboBox (String[] items, SearchableComboBox parentComboBox, Map subItemsMap) {
		this (items);
		this.subItemsMap = subItemsMap;
		listenForParentEvents (parentComboBox);
	}

	public void listenForParentEvents (SearchableComboBox parentComboBox) {
		// Add an ActionListener to the JComboBox to listen for item selection events
		parentComboBox.addActionListener (new ActionListener () {
			@Override
			public void actionPerformed (ActionEvent e) {
				// Get the selected item from the JComboBox
				String parentItem = (String) parentComboBox.getSelectedItem ();
				if (parentItem != null)
					changeItems (parentItem);
			}
		});
	}

	// Change items according to parentItems (e.g. Ciudades Colombia|Ecuador|Peru)
	public void changeItems (String parentItem) {
		Object[] keys = subItemsMap.keySet ().toArray ();
		for (Object okey : keys) {
			String key = (String) okey;
			if (parentItem.contains (key)) {
				originalItems = (String[]) subItemsMap.get (key);
				break;
			}
		}

		ComboBoxModel<String> newModel = new DefaultComboBoxModel<String> (originalItems);
		this.setModel (newModel); 		// Update comboBox
	}

	private void filterItems (String text) {
		DefaultComboBoxModel<String> model = (DefaultComboBoxModel<String>) getModel ();

		model.removeAllElements ();
		for (String item : originalItems) {
			String name = null;
			if (item.contains ("--Selección--"))
				name = new String ("--Selección--");
			else
				name = item.split ("\\s", 2)[1];          // Ecuapass data stasts with [###]

			if (name.startsWith (text))
				model.addElement (item);
		}
		setPopupVisible (true);
	}

	public void selectItemFromSubstring (String substring) {
		for (int i = 0; i < this.getItemCount (); i++) {
			String itemText = (String) this.getItemAt (i); // Convert to lowercase for case-insensitive matching
			if (itemText.toUpperCase ().contains (substring.toUpperCase ())) {
				this.setSelectedIndex (i);
				break; // Stop searching once a match is foundx
			}
		}
	}

	public static void main (String[] args) {
		SwingUtilities.invokeLater (() -> {
			JFrame frame = new JFrame ("Searchable JComboBox Demo");
			frame.setDefaultCloseOperation (JFrame.EXIT_ON_CLOSE);
			frame.setSize (300, 200);

			String[] items = {"Apple", "Banana", "Cherry", "Date", "Grapes", "Kiwi", "Lemon", "Orange"};
			SearchableComboBox comboBox = new SearchableComboBox (items);
			frame.add (comboBox);

			frame.setVisible (true);
		});

	}
}