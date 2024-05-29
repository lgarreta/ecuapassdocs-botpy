package widgets;

import java.awt.BorderLayout;
import java.awt.Dimension;
import java.awt.Point;
import javax.swing.JDialog;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JButton;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.util.Arrays;
import javax.swing.JPanel;
import static javax.swing.WindowConstants.DISPOSE_ON_CLOSE;
import javax.swing.border.EmptyBorder;

public class TopMessageDialog extends JDialog implements ActionListener {

	public TopMessageDialog (JFrame parent, String message) {
		super ((JFrame) parent, "MENSAJE", false);

		// Set AlwaysOnTop property
		setAlwaysOnTop (true);
		setModal (true);

		// Set dialog within parent frame if one exists
		if (parent != null) {
			Dimension parentFrameSize = parent.getSize ();
			Point p = parent.getLocation ();
			setLocation (p.x + parentFrameSize.width / 2, p.y + parentFrameSize.height / 2);
		}
		// Create a description pane
		JPanel descPanel = new JPanel ();
		// message = message.replace ("\n", "<br>");
		String[] lines = message.split ("\\\\");
		String mainMessage = String.format ("<h3><center>%s</center></h3>", lines[0]);

		String infoMessage = "";
		if (lines.length > 1) {
			String[] infoLines = Arrays.copyOfRange (lines, 1, lines.length);
			infoMessage = String.join ("<br>", infoLines);
		}
		message = "".format ("<html>%s<p>%s</p><html/>", mainMessage, infoMessage);
		JLabel textArea = new JLabel (message);
		textArea.setBorder (new EmptyBorder (10, 20, 10, 20));

		descPanel.add (textArea);
		this.add (descPanel);
		// Create a button pane
		JPanel buttonPanel = new JPanel ();
		JButton btn = new JButton ("OK");
		btn.addActionListener (this);
		buttonPanel.add (btn);
		//buttonPanel.setBackground (Color.red);
		this.add (buttonPanel, BorderLayout.SOUTH);
		setDefaultCloseOperation (DISPOSE_ON_CLOSE);
		pack ();
		setVisible (true);
	}

	public static void showAlwaysOnTopMessage (JFrame parent, String message) {
		TopMessageDialog dialog = new TopMessageDialog (parent, message);
		dialog.setVisible (true);
	}

	public static void main (String[] args) {
		// This example does not have a main application window
		showAlwaysOnTopMessage (null, "This is a message dialog always on top.\nThis is a message dialog always on top.\nThis is a message dialog always on top.");
	}

	@Override

	public void actionPerformed (ActionEvent e) {
		setVisible (false);
		dispose ();
	}
}
