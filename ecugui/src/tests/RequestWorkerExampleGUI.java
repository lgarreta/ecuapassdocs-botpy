
import javax.swing.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

public class RequestWorkerExampleGUI extends JFrame {
    private JButton requestButton;
    private JTextArea responseArea;

    public RequestWorkerExampleGUI() {
        requestButton = new JButton("Send Request");
        responseArea = new JTextArea(10, 30);
        
        requestButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                // Perform the network request in a background thread
                new RequestWorker().execute();
            }
        });

        add(requestButton, "North");
        add(new JScrollPane(responseArea), "Center");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        pack();
        setVisible(true);
    }

    private class RequestWorker extends SwingWorker<String, Void> {
        @Override
        protected String doInBackground() throws Exception {
            // Simulate sending a request to the server and receiving a response
            Thread.sleep(2000); // Simulate network delay
            return "Server response";
        }

        @Override
        protected void done() {
            try {
                // Update the GUI with the response
                responseArea.setText(get());
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    }

    public static void main(String[] args) {
        new RequestWorkerExampleGUI();
    }
}
