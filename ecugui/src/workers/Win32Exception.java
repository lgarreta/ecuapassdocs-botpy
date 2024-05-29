package workers;

public class Win32Exception extends Exception { 
	public Win32Exception () {
		super ("Problemas buscando la ventana del ECUAPASS");
	}
    public Win32Exception (String errorMessage) {
        super(errorMessage);
    }
}
