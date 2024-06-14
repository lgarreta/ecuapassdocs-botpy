package main;

import documento.DocModel;
import java.awt.Color;
import java.awt.Desktop;
import java.awt.image.BufferedImage;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.net.URL;
import java.net.URLConnection;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.ArrayList;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;
import javax.imageio.ImageIO;
import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.rendering.ImageType;
import org.apache.pdfbox.rendering.PDFRenderer;
import org.apache.pdfbox.text.PDFTextStripper;

public class Utils {

	public static Color HIGH_GREEN = new Color (240, 255, 240);
	public static Color MID_YELLOW = new Color (255, 255, 192);
	public static Color LOW_RED = new Color (255, 229, 229);

	// Copy file from source to destiny checking if file exists 
	public static void copyFile (String sourceFilepath, String destFilepath) {
		//System.out.println  ("Copiando archivos:");
		try {
			File sourcePath = new File (sourceFilepath);
			File destPath = new File (destFilepath);
			//System.out.println  (">>> FUENTE: " + sourcePath);
			//System.out.println  (">>> DESTINO: " + destPath);
			if (sourcePath.getName ().contains ("DUMMY")) {
				destPath.createNewFile ();
				return;
			}
			if (destPath.exists ())
				Files.delete (destPath.toPath ());
			Files.copy (sourcePath.toPath (), destPath.toPath (), StandardCopyOption.REPLACE_EXISTING);
		} catch (IOException ex) {
			System.out.println ("EXCEPCION: No se pudo reemplazar el archivo");
			//Logger.getLogger (Utils.class.getName ()).log (Level.SEVERE, null, ex);
		}

	}

	// Extract the document number from a filename
	public static String extractDocNumber (String filename) {
		Pattern pattern = Pattern.compile ("(CO|COCO|EC|ECEC)(\\d+)");
		Matcher matcher = pattern.matcher (filename);

		if (matcher.find ()) {
			String prefix = matcher.group (1);
			prefix = prefix.replace ("COCO", "CO");
			prefix = prefix.replace ("ECEC", "EC");			
			return prefix + matcher.group (2); // Combine prefix and number
		}else
			return null; // No match found
	}

	// Return document type if document title is found in PDF lines
	public static String getDocumentTypeFromPDF (String pdfFilepath) {
		String textDeclaracion = "Declaración de Tránsito Aduanero Internacional ";
		String textManifiesto = "Manifiesto de Carga Internacional";
		String textCartaporte = "Carta de Porte Internacional por Carretera";

		String[] lines = getLinesFromPDF (pdfFilepath);
		for (String line : lines) {
			if (line.contains (textCartaporte))
				return "CARTAPORTE";
			else if (line.contains (textManifiesto))
				return "MANIFIESTO";
			else if (line.contains (textDeclaracion))
				return "DECLARACION";
		}
		return null;
	}

	public static String getDocumentTypeFromFilename (String filename) {
		filename = filename.toUpperCase ();
		if (filename.contains ("CPI") || filename.contains ("CARTAPORTE"))
			return "CARTAPORTE";
		else if (filename.contains ("MCI") || filename.contains ("MANIFIESTO"))
			return "MANIFIESTO";
		else
			return null;
	}

	public static String[] getLinesFromPDF (String pdfFilepath) {
		String[] lines = null;
		try {
			File pdfFile = new File (pdfFilepath); // Replace with the path to your PDF file
			PDDocument document = PDDocument.load (pdfFile);

			PDFTextStripper pdfTextStripper = new PDFTextStripper ();
			String pdfText = pdfTextStripper.getText (document);

			lines = pdfText.split ("\\r?\\n"); // Split the text into lines
			document.close ();
		} catch (IOException e) {
			e.printStackTrace ();
		}
		return lines;
	}

	// Convert first page PDF file to image and write to tmpDir
	public static File convertPDFToImage (File pdfFilepath) {
		File tmpDir = new File (System.getProperty ("java.io.tmpdir"));
		File outImgFilepath = new File (tmpDir, pdfFilepath.getName ().replace (".pdf", ".jpg"));
		if (outImgFilepath.exists ())
			return (outImgFilepath);
		//else:
		try {
			PDDocument document = PDDocument.load (pdfFilepath);
			PDFRenderer pdfRenderer = new PDFRenderer (document);

			int numberOfPages = document.getNumberOfPages ();

			int dpi = 200;// use less dpi for to save more space in harddisk. For professional usage you can use more than 300dpi 
			BufferedImage bImage = pdfRenderer.renderImageWithDPI (0, dpi, ImageType.RGB);
			ImageIO.write (bImage, "jpg", outImgFilepath);
			document.close ();
		} catch (IOException ex) {
			Logger.getLogger (Utils.class.getName ()).log (Level.SEVERE, null, ex);
		}
		return (outImgFilepath);
	}

	// Return if a file is a pdf or a image or none
	public static String getFileContentType (File file) {
		String mimeType = URLConnection.guessContentTypeFromName (file.getName ());
		if (mimeType.contains ("pdf"))
			return ("pdf");
		else if (mimeType.contains ("image"))
			return ("image");
		else
			return ("");
	}

	// Get OS name
	public static String getOSName () {
		String OSType = System.getProperty ("os.name").toLowerCase ();
		if (OSType.contains ("windows"))
			return ("windows");
		else
			return ("linux");
	}

	// Return OS tmp dir
	public static File getOSTmpDir () {
		File tmpDir = new File (System.getProperty ("java.io.tmpdir"));
		return (tmpDir);
	}

	// Return save/open projects directory 
	public static String convertToOSPath (String path) {
		if (getOSName ().equals ("windows"))
			path = path.replace ("\\", "\\\\");
		return (path);
	}

	public static String getResultsFile (String docFilepath, String sufixString) {
		String fileName = new File (docFilepath).getPath ();
		String docFilename = fileName.substring (0, fileName.lastIndexOf ('.'));
		String resultsFilename = String.format ("%s-%s", docFilename, sufixString);
		File resultsFilepath = new File (resultsFilename);
		return (resultsFilepath.toString ());
	}

	public static String getResourcePath (Object obj, String resourceName) {
		URL resourceURL = null;
		resourceURL = obj.getClass ().getClassLoader ().getResource ("resources/" + resourceName);
		return (resourceURL.getPath ());
	}
	
	public static String getResourcePathFromTmpDir (String resourceName) {
		String resourcesFile = Paths.get (DocModel.temporalPath, "resources", resourceName).toString ();
		return (resourcesFile);
		
	}

//	public static String getResourcePath (String runningPath, String resourceName) {
//		Path resourcePath = Paths.get (runningPath, resourceName);
//		return (resourcePath.toString ());
//	}
	public static String createTempCompressedFileFromText (String text) {
		File tempFile = null;
		try {
			// Create a temporary file to hold the compressed data
			tempFile = File.createTempFile ("compressed", ".zip");

			// Create a ZipOutputStream to write to the temporary file
			try (FileOutputStream fos = new FileOutputStream (tempFile); ZipOutputStream zipOut = new ZipOutputStream (fos)) {
				// Add a new ZIP entry
				zipOut.putNextEntry (new ZipEntry ("text.txt"));

				// Write the text content to the ZIP entry
				zipOut.write (text.getBytes ());

				// Close the ZIP entry
				zipOut.closeEntry ();
			}
		} catch (IOException ex) {
			Logger.getLogger (Utils.class.getName ()).log (Level.SEVERE, null, ex);
		}

		return Utils.convertToOSPath (tempFile.toString ());
	}

	// Used to read and fill Ecuapass comboBoxes (e.g paises, ciudades, etc.)
	public static String[] readDataFromFile (String filename) {
		List<String> data = new ArrayList<> ();
		String[] arrData = null;
		try (BufferedReader reader = new BufferedReader (new FileReader (filename))) {
			String line;
			while ((line = (String) reader.readLine ()) != null) {
				if (line.contains ("+++"))
					continue;
				data.add (new String (line.getBytes (), "UTF-8"));
			}
			arrData = data.toArray (new String[0]);
		} catch (IOException e) {
			e.printStackTrace ();
		}
		return arrData;
	}

	// Used to read to fill Ecuapass comboBoxes (e.g paises, ciudades, etc.)
	public static String[] readDataResourceFromFile (Object obj, String filename) {
		String resourcesPath = Utils.getResourcePath (obj, "");
		filename = resourcesPath + filename;
		List<String> data = new ArrayList<> ();
		String[] arrData = null;
		try (BufferedReader reader = new BufferedReader (new FileReader (filename))) {
			String line;
			while ((line = (String) reader.readLine ()) != null) {
				data.add (new String (line.getBytes (), "UTF-8"));
			}
			arrData = data.toArray (new String[0]);
		} catch (IOException e) {
			e.printStackTrace ();
		}
		return arrData;
	}

	public static boolean copyResourcesToTemporalPathFromPath (Object CLASS, String temporalPath) {
		System.out.println ("CLIENTE: Copiando recursos desde un PATH.");
		try {
			String resourceDir = "resources/";// Specify the resource directory path within the JAR			
			ClassLoader classLoader = CLASS.getClass ().getClassLoader ();// Get a reference to the current class loader			
			URL resourceUrl = classLoader.getResource (resourceDir);// Get the URL of the resource directory
			if (resourceUrl == null)
				System.out.println ("SERVER: Carpeta de recursos no encontrada: " + resourceDir);
			else {
				URI uri = resourceUrl.toURI ();
				Path resourcePath = Paths.get (uri);// Convert the URL to a Path		
				Files.walk (resourcePath)// Walk the directory and collect all resource names
					.forEach (filePath -> {
						if (filePath.equals (resourcePath) == false) {
							Path relativePath = resourcePath.relativize (filePath);
							Path destinationPath = Paths.get (temporalPath, relativePath.toString ());
							if (Files.isDirectory (destinationPath))
								destinationPath.toFile ().mkdir ();
							else
							try {
								Files.copy (filePath, destinationPath, StandardCopyOption.REPLACE_EXISTING);
							} catch (IOException ex) {
								Logger.getLogger (CLASS.getClass ().getName ()).log (Level.SEVERE, null, ex);
							}
						}
					}
					);
			}
		} catch (URISyntaxException | IOException ex) {
			ex.printStackTrace ();
			return false;
		}
		return true;
	}

	public static void openPDF (String pdfFilepath) {
		try {
			// Specify the path to the PDF file you want to open
			File pdfFile = new File (pdfFilepath);

			if (Desktop.isDesktopSupported ()) {
				Desktop desktop = Desktop.getDesktop ();

				if (pdfFile.exists () && pdfFile.getName ().toLowerCase ().endsWith (".pdf"))
					desktop.open (pdfFile);
				else
					System.out.println (">>> The specified file is not a valid PDF.");
			} else
				System.out.println (">>> Desktop API is not supported on this platform.");
		} catch (IOException e) {
			e.printStackTrace ();
		}
	}

	public static void main (String[] args) {
		Utils.convertPDFToImage (new File ("/home/lg/AAA/factura-oxxo2.pdf"));
	}

	// A default image is returned according to the document type
	public static File getDefaultDocImage (File docFilepath, Object obj) {
		String docType = Utils.getDocumentTypeFromFilename (docFilepath.getName ());
		String imagePath = null;
		if (docType.equals ("CARTAPORTE"))
			imagePath = Utils.getResourcePathFromTmpDir ("images/cartaporte-DUMMY.png");
		else if (docType.equals ("MANIFIESTO"))
			imagePath = Utils.getResourcePathFromTmpDir ("images/manifiesto-DUMMY.png");
		else
			imagePath = Utils.getResourcePathFromTmpDir ("images/image-DUMMY.png");
		
		return new File (imagePath);
	}
}
