package config;

import javax.swing.JTextField;
import org.json.simple.JSONObject;

public class SettingsPanel extends javax.swing.JPanel {

	SettingsController controller;

	public SettingsPanel () {
		initComponents ();
	}

	public void setController (SettingsController controller) {
		this.controller = controller;
	}

	// Return settings displayed on the panel
	public JSONObject getSttings () {
		// Create a JSON object
		JSONObject settings = new JSONObject ();
		settings.put ("empresa", empresa.getText ());
		settings.put ("codebin_url", codebinUrl.getText ());
		settings.put ("codebin_user", codebinUser.getText ());
		settings.put ("codebin_password", codebinPassword.getText ());
		settings.put ("codebin_user2", codebinUser2.getText ());
		settings.put ("codebin_password2", codebinPassword2.getText ());
		settings.put ("NORMAL_PAUSE", normalPause.getText ());
		settings.put ("SLOW_PAUSE", slowPause.getText ());
		settings.put ("FAST_PAUSE", fastPause.getText ());

		return settings;
	}

	public void setSettings (JSONObject settings) {
			empresa.setText ((String) settings.get ("empresa"));
			codebinUrl.setText ((String) settings.get ("codebin_url"));
			codebinUser.setText ((String) settings.get ("codebin_user"));
			codebinPassword.setText ((String) settings.get ("codebin_password"));
			codebinUser2.setText ((String) settings.get ("codebin_user2"));
			codebinPassword2.setText ((String) settings.get ("codebin_password2"));
			normalPause.setText ((String) settings.get ("NORMAL_PAUSE"));
			slowPause.setText ((String) settings.get ("SLOW_PAUSE"));
			fastPause.setText ((String) settings.get ("FAST_PAUSE"));
		}

		@SuppressWarnings("unchecked")
  // <editor-fold defaultstate="collapsed" desc="Generated Code">//GEN-BEGIN:initComponents
  private void initComponents() {

    ConfigurationPanel = new javax.swing.JPanel();
    companyLabel = new javax.swing.JLabel();
    empresa = new javax.swing.JTextField();
    codebiniLabel = new javax.swing.JLabel();
    codebinUrl = new javax.swing.JTextField();
    ecuapassdocsLabel = new javax.swing.JLabel();
    codebinUser = new javax.swing.JTextField();
    ecuapassLabel = new javax.swing.JLabel();
    codebinPassword = new widgets.PasswordFieldWithToggle();
    codebinUsuario2Label = new javax.swing.JLabel();
    codebinUser2 = new javax.swing.JTextField();
    codebinPassword2Label = new javax.swing.JLabel();
    codebinPassword2 = new widgets.PasswordFieldWithToggle();
    normalPauseLabel = new javax.swing.JLabel();
    normalPause = new javax.swing.JTextField();
    slowPauseLabel = new javax.swing.JLabel();
    slowPause = new javax.swing.JTextField();
    fastPauseLabel = new javax.swing.JLabel();
    fastPause = new javax.swing.JTextField();
    panelOptions = new javax.swing.JPanel();
    saveButton = new javax.swing.JButton();
    cancelButton = new javax.swing.JButton();

    setLayout(new java.awt.BorderLayout());

    ConfigurationPanel.setBorder(javax.swing.BorderFactory.createTitledBorder("Configuración"));
    ConfigurationPanel.setPreferredSize(new java.awt.Dimension(700, 140));
    ConfigurationPanel.setLayout(new java.awt.GridLayout(9, 2));

    companyLabel.setText("Empresa:");
    ConfigurationPanel.add(companyLabel);
    ConfigurationPanel.add(empresa);

    codebiniLabel.setText("Codebin URL:");
    ConfigurationPanel.add(codebiniLabel);
    ConfigurationPanel.add(codebinUrl);

    ecuapassdocsLabel.setText("Codebin Usuario:");
    ConfigurationPanel.add(ecuapassdocsLabel);
    ConfigurationPanel.add(codebinUser);

    ecuapassLabel.setText("Codebin Contraseña:");
    ConfigurationPanel.add(ecuapassLabel);
    ConfigurationPanel.add(codebinPassword);

    codebinUsuario2Label.setText("Codebin Usuario 2:");
    ConfigurationPanel.add(codebinUsuario2Label);
    ConfigurationPanel.add(codebinUser2);

    codebinPassword2Label.setText("Codebin Contraseña 2:");
    ConfigurationPanel.add(codebinPassword2Label);
    ConfigurationPanel.add(codebinPassword2);

    normalPauseLabel.setText("Tiempo Pausa Normal (0.05 Seg):");
    ConfigurationPanel.add(normalPauseLabel);

    normalPause.setText("0.05");
    ConfigurationPanel.add(normalPause);

    slowPauseLabel.setText("Tiempo Pausa Lenta (0.5 Seg):");
    ConfigurationPanel.add(slowPauseLabel);

    slowPause.setText("0.5");
    ConfigurationPanel.add(slowPause);

    fastPauseLabel.setText("Tiempo Pausa Rápida (0.01 Seg):");
    ConfigurationPanel.add(fastPauseLabel);

    fastPause.setText("0.01");
    fastPause.addActionListener(new java.awt.event.ActionListener() {
      public void actionPerformed(java.awt.event.ActionEvent evt) {
        fastPauseActionPerformed(evt);
      }
    });
    ConfigurationPanel.add(fastPause);

    add(ConfigurationPanel, java.awt.BorderLayout.CENTER);

    saveButton.setText("Guardar");
    saveButton.addActionListener(new java.awt.event.ActionListener() {
      public void actionPerformed(java.awt.event.ActionEvent evt) {
        saveButtonActionPerformed(evt);
      }
    });
    panelOptions.add(saveButton);

    cancelButton.setText("Cancelar");
    cancelButton.addActionListener(new java.awt.event.ActionListener() {
      public void actionPerformed(java.awt.event.ActionEvent evt) {
        cancelButtonActionPerformed(evt);
      }
    });
    panelOptions.add(cancelButton);

    add(panelOptions, java.awt.BorderLayout.SOUTH);
  }// </editor-fold>//GEN-END:initComponents

  private void saveButtonActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_saveButtonActionPerformed
		JSONObject settings = this.getSttings ();
		controller.onSaveSettings (settings);
  }//GEN-LAST:event_saveButtonActionPerformed

  private void cancelButtonActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_cancelButtonActionPerformed
		// TODO add your handling code here:
		controller.onCancelSettings ();
  }//GEN-LAST:event_cancelButtonActionPerformed

  private void fastPauseActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_fastPauseActionPerformed
		// TODO add your handling code here:
  }//GEN-LAST:event_fastPauseActionPerformed

  // Variables declaration - do not modify//GEN-BEGIN:variables
  private javax.swing.JPanel ConfigurationPanel;
  private javax.swing.JButton cancelButton;
  private widgets.PasswordFieldWithToggle codebinPassword;
  private widgets.PasswordFieldWithToggle codebinPassword2;
  private javax.swing.JLabel codebinPassword2Label;
  private javax.swing.JTextField codebinUrl;
  private javax.swing.JTextField codebinUser;
  private javax.swing.JTextField codebinUser2;
  private javax.swing.JLabel codebinUsuario2Label;
  private javax.swing.JLabel codebiniLabel;
  private javax.swing.JLabel companyLabel;
  private javax.swing.JLabel ecuapassLabel;
  private javax.swing.JLabel ecuapassdocsLabel;
  private javax.swing.JTextField empresa;
  private javax.swing.JTextField fastPause;
  private javax.swing.JLabel fastPauseLabel;
  private javax.swing.JTextField normalPause;
  private javax.swing.JLabel normalPauseLabel;
  private javax.swing.JPanel panelOptions;
  private javax.swing.JButton saveButton;
  private javax.swing.JTextField slowPause;
  private javax.swing.JLabel slowPauseLabel;
  // End of variables declaration//GEN-END:variables

}
