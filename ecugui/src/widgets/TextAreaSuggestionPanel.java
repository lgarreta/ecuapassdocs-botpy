package widgets;

import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Point;
import java.awt.event.KeyAdapter;
import java.awt.event.KeyEvent;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.util.ArrayList;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;

import javax.swing.BorderFactory;
import javax.swing.JFrame;
import javax.swing.JList;
import javax.swing.JPanel;
import javax.swing.JPopupMenu;
import javax.swing.JTextArea;
import javax.swing.ListSelectionModel;
import javax.swing.SwingUtilities;
import javax.swing.text.BadLocationException;

public class TextAreaSuggestionPanel extends JTextArea {

	private SuggestionPanel suggestionPanel;

	public TextAreaSuggestionPanel () {
		super ();
		setBorder (BorderFactory.createLineBorder (Color.DARK_GRAY, 1));
	}

	public TextAreaSuggestionPanel (int x, int y) {
		super (x, y);
		setBorder (BorderFactory.createLineBorder (Color.DARK_GRAY, 1));
	}

	protected void showSuggestionLater (JTextArea textArea) {
		if(getCurrentLineNumber () >0)
			return;
		SwingUtilities.invokeLater (new Runnable () {
			@Override
			public void run () {
				showSuggestion (textArea);
			}
		});
	}
	
	int getCurrentLineNumber () {
		try {
			int caretPosition = this.getCaretPosition();
			int line = this.getLineOfOffset(caretPosition);
			int lineStartOffset = this.getLineStartOffset(line);
			return lineStartOffset;
		} catch (BadLocationException ex) {
			Logger.getLogger (TextAreaSuggestionPanel.class.getName()).log (Level.SEVERE, null, ex);
		}
		return -1;
	}

	protected void showSuggestion (JTextArea textArea) {
		hideSuggestion ();
		final int position = textArea.getCaretPosition ();
		Point location;
		try {
			location = textArea.modelToView (position).getLocation ();
		} catch (BadLocationException e2) {
			e2.printStackTrace ();
			return;
		}
		String text = textArea.getText ();
		int start = Math.max (0, position - 1);
		while (start > 0) {
			if (!Character.isWhitespace (text.charAt (start)))
				start--;
			else {
				start++;
				break;
			}
		}
		if (start > position)
			return;
		final String subWord = text.substring (start, position);
		if (subWord.length () < 2)
			return;
		suggestionPanel = new SuggestionPanel (textArea, position, subWord, location, this);
		SwingUtilities.invokeLater (new Runnable () {
			@Override
			public void run () {
				textArea.requestFocusInWindow ();
			}
		});
	}

	protected void hideSuggestion () {
		if (suggestionPanel != null) {
			suggestionPanel.hide ();
			suggestionPanel = null;
		}
	}

	void setListeners () {
		JTextArea textArea = this;
		textArea.addKeyListener (new KeyAdapter () {
			@Override
			public void keyTyped (KeyEvent e) {
				if (e.getKeyChar () == KeyEvent.VK_ENTER && suggestionPanel != null)
					if (suggestionPanel.insertSelection () == false)
						hideSuggestion ();
					else {
						e.consume ();
						final int position = textArea.getCaretPosition ();
						SwingUtilities.invokeLater (new Runnable () {
							@Override
							public void run () {
								try {
									textArea.getDocument ().remove (position - 1, 1);
								} catch (BadLocationException e) {
									e.printStackTrace ();
								}
							}
						});
					}
			}

			@Override
			public void keyReleased (KeyEvent e) {
				if (e.getKeyCode () == KeyEvent.VK_DOWN && suggestionPanel != null)
					suggestionPanel.moveDown ();
				else if (e.getKeyCode () == KeyEvent.VK_UP && suggestionPanel != null)
					suggestionPanel.moveUp ();
				else if (Character.isLetterOrDigit (e.getKeyChar ()))
					showSuggestionLater (textArea);
				else if (Character.isWhitespace (e.getKeyChar ()))
					hideSuggestion ();
			}
		});
	}

	public static void main (String[] args) {
		SwingUtilities.invokeLater (new Runnable () {
			@Override
			public void run () {
				final JFrame frame = new JFrame ();
				frame.setTitle ("Test frame on two screens");
				frame.setDefaultCloseOperation (JFrame.EXIT_ON_CLOSE);
				JPanel panel = new JPanel (new BorderLayout ());
				TextAreaSuggestionPanel textArea = new TextAreaSuggestionPanel (24, 80);
				textArea.setListeners ();
				panel.add (textArea, BorderLayout.CENTER);
				frame.add (panel);
				frame.pack ();
				frame.setVisible (true);
			}
		});
	}
}

//------------------------------------------------------------------
// Creata a popup menu with options from text in TexArea
//------------------------------------------------------------------
class SuggestionPanel {
	private JList list;
	private JPopupMenu popupMenu;
	private String subWord;
	private final int insertionPosition;
	private JTextArea textArea;
	private TextAreaSuggestionPanel controller;

	public SuggestionPanel (JTextArea textArea, int position, String subWord, Point location, TextAreaSuggestionPanel controller) {
		this.textArea = textArea;
		this.insertionPosition = position;
		this.subWord = subWord;
		this.controller = controller;

		popupMenu = new JPopupMenu ();
		popupMenu.removeAll ();
		popupMenu.setOpaque (false);
		popupMenu.setBorder (null);
		popupMenu.add (list = createSuggestionList (position, subWord), BorderLayout.CENTER);
		popupMenu.show (textArea, location.x, textArea.getBaseline (0, 0) + location.y);
	}

	public void hide () {
		popupMenu.setVisible (false);
		//if (suggestion == this)
		//	suggestion = null;
	}

	private JList createSuggestionList (final int position, final String subWord) {
		Object[] alldata = new Object[]{"apple", "banana", "cherry", "chocolate", "blueberry"};
		List<String> subdata = new ArrayList<> ();
		for (int i = 0; i < alldata.length; i++) {
			String value = (String) alldata[i];
			if (value.startsWith (subWord))
				subdata.add (value);
		}

		JList list = new JList (subdata.toArray ());
		list.setBorder (BorderFactory.createLineBorder (Color.DARK_GRAY, 1));
		list.setSelectionMode (ListSelectionModel.SINGLE_SELECTION);
		list.setSelectedIndex (0);
		list.addMouseListener (new MouseAdapter () {
			@Override
			public void mouseClicked (MouseEvent e) {
				if (e.getClickCount () == 2)
					if (insertSelection () == false)
						controller.hideSuggestion ();
			}
		});
		return list;
	}

	public boolean insertSelection () {
		if (list.getSelectedValue () != null)
				try {
			final String selectedSuggestion = ((String) list.getSelectedValue ()).substring (subWord.length ());
			textArea.getDocument ().insertString (insertionPosition, selectedSuggestion, null);
			return true;
		} catch (BadLocationException e1) {
			e1.printStackTrace ();
		}
		return false;
	}

	public void moveUp () {
		int index = Math.min (list.getSelectedIndex () - 1, 0);
		selectIndex (index);
	}

	public void moveDown () {
		int index = Math.min (list.getSelectedIndex () + 1, list.getModel ().getSize () - 1);
		selectIndex (index);
	}

	private void selectIndex (int index) {
		final int position = textArea.getCaretPosition ();
		list.setSelectedIndex (index);
		SwingUtilities.invokeLater (new Runnable () {
			@Override
			public void run () {
				textArea.setCaretPosition (position);
			}
		}
		);
	}
}
