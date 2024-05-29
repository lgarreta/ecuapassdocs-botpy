package widgets;

import javax.swing.*;
import java.awt.*;
import java.awt.event.*;

public class PasswordFieldWithToggle extends JPanel {
    private JPasswordField passwordField;
    private JButton showHideButton;
		private int columns = 20;

    public PasswordFieldWithToggle() {
        passwordField = new JPasswordField(columns);
        showHideButton = new JButton("Ver");

        showHideButton.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                togglePasswordVisibility();
            }
        });

        setLayout(new BorderLayout());
        add(passwordField, BorderLayout.CENTER);
        add(showHideButton, BorderLayout.EAST);
    }

    private void togglePasswordVisibility() {
        if (showHideButton.getText().equals("Ver")) {
            passwordField.setEchoChar((char) 0); // Show the actual characters
            showHideButton.setText("Ocultar");
        } else {
            passwordField.setEchoChar('*'); // Show '*' characters
            showHideButton.setText("Ver");
        }
    }

    public String getText() {
        return new String(passwordField.getPassword());
    }

    public void setText(String password) {
        passwordField.setText(password);
    }

    public static void main(String[] args) {
        JFrame frame = new JFrame("Password Field Example");
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.getContentPane().add(new PasswordFieldWithToggle());
        frame.pack();
        frame.setVisible(true);
    }
}
