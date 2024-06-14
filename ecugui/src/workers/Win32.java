package workers;

import com.sun.jna.Library;
import com.sun.jna.Native;
import com.sun.jna.Pointer;
import com.sun.jna.win32.StdCallLibrary;
import java.util.logging.Level;
import java.util.logging.Logger;
import javax.swing.JOptionPane;

// Class to send events to system windows (e.g. activate, maximize, ...)
public class Win32 {

	public interface User32 extends StdCallLibrary {

		User32 INSTANCE = Native.load ("user32", User32.class);

		// Find a window by its title
		Pointer FindWindowA (String className, String windowName);

		// Set a window to the foreground
		boolean SetForegroundWindow (Pointer hWnd);

		boolean ShowWindow (Pointer hWnd, int nCmdShow);
		int SW_MAXIMIZE = 3;  // Constant to maximize the window
	}

	public static boolean activateMaximizeEcuapassWindow ()  {
		try {
			// Pointer hWnd = findWindow ("ECUAPASS - SENAE browser");
			Pointer hWnd = findWindow ("SENAE");
			if (hWnd == null) {
				JOptionPane.showMessageDialog (null, "No se encontró ventana del ECUAPASS");
				return false;
			} else {
				activateWindow (hWnd);
				//maximizeWindow (hWnd);
				Thread.sleep (3000);
				return true;
			}
		} catch (Win32Exception | InterruptedException ex) {
			ex.printStackTrace ();
		}
		return false;
	}

	public static Pointer findWindow (String windowTitle) throws Win32Exception {
		Pointer hWnd = User32.INSTANCE.FindWindowA (null, windowTitle);
		return hWnd;
	}

	public static void activateWindow (Pointer hWnd) throws Win32Exception {
		boolean result = User32.INSTANCE.SetForegroundWindow (hWnd);
		if (result == false)
			throw new Win32Exception ("No se pudo activar ventana");
		System.out.println (">>> Ventana activada.");
	}

	public static void maximizeWindow (Pointer hWnd) throws Win32Exception {
		boolean result = User32.INSTANCE.ShowWindow (hWnd, User32.SW_MAXIMIZE);
		if (result == false)
			throw new Win32Exception ("No se pudo maximizarventana");
		System.out.println (">>> Ventana maximizada.");
	}
}
