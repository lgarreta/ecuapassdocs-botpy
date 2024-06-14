package widgets;

import documento.DocModel;
import main.Controller;
import main.Utils;
import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.awt.image.BufferedImage;
import java.awt.image.ImageObserver;
import java.io.File;
import java.io.IOException;
import static java.lang.Math.abs;
import java.nio.file.Paths;
import java.util.logging.Level;
import java.util.logging.Logger;
import javax.imageio.ImageIO;

public final class ImageViewLens extends javax.swing.JPanel {

	private Image image;
	String imagePath;
	Dimension imgDim;

	private ImageLabel imageLabel;
	private JScrollPane scrollPane;
	private Point lastMousePoint;
	private double scale = 1.0;
	private double zoomFactor = 0.1; //When zooming or zoomout it's added or substracted

	public ImageViewLens () {
		initComponents ();
	}

	private void initComponents () {
		setLayout (new BorderLayout ());
//		this.imgPath = Utils.getResourcePath (this, "images/image-cartaporte-vacia.png");
		imagePath = DocModel.runningPath + "/resources/images/image-cartaporte-vacia.png";
		ImageIcon imageIcon = new ImageIcon (imagePath);
		imageLabel = new ImageLabel (imageIcon, this);

		image = imageIcon.getImage ();
		scrollPane = new JScrollPane (imageLabel);
		scrollPane.setPreferredSize (new Dimension (850, 600));
		scrollPane.getVerticalScrollBar ().setUnitIncrement (16);
		scrollPane.getHorizontalScrollBar ().setUnitIncrement (16);
		add (scrollPane, BorderLayout.CENTER);
		addListeners ();
	}

	public void addListeners () {;
		// Add a ComponentListener to detect resizing
		ComponentListener componentListener = new ComponentAdapter () {
			@Override
			public void componentResized (ComponentEvent e) {
				int newWidth = getWidth ();
				int newHeight = getHeight ();
				imgDim = drawScaledImage ();
				updateImageSize ();
			}
		};

		MouseAdapter mouseAdapter = new MouseAdapter () {
			@Override
			public void mousePressed (MouseEvent e) {
				lastMousePoint = e.getPoint ();
			}

			@Override
			public void mouseDragged (MouseEvent e) {
				if (lastMousePoint != null) {
					JViewport viewPort = scrollPane.getViewport ();
					Point currentPoint = e.getPoint ();
					Point viewPosition = viewPort.getViewPosition ();
					viewPosition.translate (lastMousePoint.x - currentPoint.x, lastMousePoint.y - currentPoint.y);
					imageLabel.scrollRectToVisible (new Rectangle (viewPosition, viewPort.getSize ()));
					lastMousePoint = currentPoint;
				}
			}

			@Override
			public void mouseWheelMoved (MouseWheelEvent e) {
				int rotation = e.getWheelRotation ();
				double scaleFactor = (rotation > 0) ? 1 - zoomFactor : 1 + zoomFactor;
				Point mousePoint = e.getPoint ();
				zoom (scaleFactor, mousePoint);
			}

			@Override
			public void mouseClicked (MouseEvent e) {
				if (e.getClickCount () == 2)
					if (e.getButton () == MouseEvent.BUTTON1) // Left double-click
						zoomIn (e.getPoint ());
					else if (e.getButton () == MouseEvent.BUTTON3) // Right click
						zoomOut (e.getPoint ());
			}

			private void zoomIn (Point mousePoint) {
				double scaleFactor = 1 + zoomFactor;
				zoom (scaleFactor, mousePoint);
			}

			private void zoomOut (Point mousePoint) {
				double scaleFactor = 1 - zoomFactor;
				zoom (scaleFactor, mousePoint);
			}

			private void zoom (double scaleFactor, Point mousePoint) {
				Point viewPosition = scrollPane.getViewport ().getViewPosition ();

				double dx = mousePoint.x - viewPosition.getX ();
				double dy = mousePoint.y - viewPosition.getY ();

				// Doesn't allow resize in if image out of panel bounds
				double tmpScale = scale * scaleFactor;
				if (imgDim.height * tmpScale > getHeight () || imgDim.width * tmpScale > getWidth ())
					return;
				scale = tmpScale;

				viewPosition.setLocation (mousePoint.getX () - dx * scaleFactor, mousePoint.getY () - dy * scaleFactor);
				scrollPane.getViewport ().setViewPosition (viewPosition);
				updateImageSize ();
			}
		};

		this.addComponentListener (componentListener);
		imageLabel.addMouseWheelListener (mouseAdapter);
		imageLabel.addMouseListener (mouseAdapter);
		imageLabel.addMouseMotionListener (mouseAdapter);
	}

	public void showImage (File docFilepath) {
		try {
			File imagePath = null;
			if (docFilepath.getName().contains ("DUMMY"))
				imagePath = Utils.getDefaultDocImage (docFilepath, this);
			else {
				if ("pdf".equals (Utils.getFileContentType (docFilepath)))
					imagePath = Utils.convertPDFToImage (docFilepath);
				else {
					System.out.println (">>> ERROR: Archivo no es un PDF");
					return;
				}
			}

			ImageIcon imageIcon = new ImageIcon (imagePath.toString ());
			image = imageIcon.getImage ();
			imageLabel.setIcon (imageIcon);

			// Set secondary image
			Image secondaryImage = ImageIO.read (imagePath);
			imageLabel.setSecondaryImage (secondaryImage);

			imageLabel.setHorizontalAlignment (SwingConstants.CENTER);
			scale = 1.0;
			imgDim = drawScaledImage ();
			updateImageSize ();
		} catch (IOException ex) {
			Logger.getLogger (ImageViewLens.class.getName ()).log (Level.SEVERE, null, ex);
		}
	}

	// Calculate dimensions when image is showing for FISRT TIME
	public Dimension drawScaledImage () {
		scale = 1.0;

		int imgWidth = image.getWidth (null);
		int imgHeight = image.getHeight (null);

		double imgAspect = (double) imgHeight / imgWidth;

		int canvasWidth = getWidth ();
		int canvasHeight = getHeight ();
		double canvasAspect = (double) canvasHeight / canvasWidth;

		double x1 = 0, y1 = 0, x2 = 0, y2 = 0; // top left bottom right positions

		if (imgWidth < canvasWidth && imgHeight < canvasHeight) {
			// the image is smaller than the canvas
			x1 = (canvasWidth - imgWidth) / 2;
			y1 = (canvasHeight - imgHeight) / 2;
			x2 = imgWidth + x1;
			y2 = imgHeight + y1;
		} else {
			if (canvasAspect >= imgAspect) {
				y1 = canvasHeight;
				canvasHeight = (int) (canvasWidth * imgAspect);
				y1 = (y1 - canvasHeight) / 2;
			} else {
				x1 = canvasWidth;
				// keep image aspect ratio
				canvasWidth = (int) (canvasHeight / imgAspect);
				x1 = (x1 - canvasWidth) / 2;
			}
			x2 = canvasWidth + x1;
			y2 = canvasHeight + y1;
		}
		// Take account offsets of Panel borders (2, 9)
		return (new Dimension ((int) (x2 - x1) - 2, (int) (y2 - y1) - 9));
	}

	private void updateImageSize () {
		int width = (int) (imgDim.width * scale);
		int height = (int) (imgDim.height * scale);

		Image scaledImage = image.getScaledInstance (width, height, Image.SCALE_DEFAULT);
		ImageIcon imageIcon = new ImageIcon (scaledImage);
		imageLabel.setIcon (imageIcon);
	}

	public static void main (String[] args) {
		ImageViewLens imgPanel = new ImageViewLens ();
		String imgPath = Utils.getResourcePath (imgPanel, "images/image-cartaporte-vacia.png");

		JFrame imgFrame = new JFrame ();
		imgFrame.setDefaultCloseOperation (JFrame.EXIT_ON_CLOSE);
		imgFrame.getContentPane ().add (imgPanel);
		imgFrame.setTitle ("Image Viewer");
		imgFrame.setSize (800, 600);
		imgFrame.setLocationRelativeTo (null);
		imgFrame.setVisible (true);
		imgPanel.showImage (new File (imgPath));
	}

}

//-------------------------------------------------------------------
// Class representing a custom JLabe handling a zooming magic lens
//-------------------------------------------------------------------
class ImageLabel extends JLabel {

	private Image primaryImage;
	private Image secondaryImage;
	private BufferedImage zoomedInImage;
	private Point pri;
	int zoom = 150; // Size of the zoomed-in region	
	double zoomSecondaryImage = 0.70;
	int pW, pH;
	int sW, sH;
	double factor;
	boolean isMouseDragged = false;
	boolean isMouseClicked = false;

	JPanel frame;

	public ImageLabel (ImageIcon imageIcon, JPanel frame) {
		super (imageIcon);
		this.frame = frame;

		primaryImage = imageIcon.getImage ();
		pW = primaryImage.getWidth (null);
		pH = primaryImage.getHeight (null);

		secondaryImage = imageIcon.getImage ();
		pri = new Point (0, 0); // Initialize to an arbitrary point
		sW = secondaryImage.getWidth (null);
		sH = secondaryImage.getHeight (null);

		factor = sW / (double) pW;

		addListeners ();
	}

	public void setPrimaryImage (Image image) {
		primaryImage = image;
	}

	public void setSecondaryImage (Image image) {
		int width = (int) (zoomSecondaryImage * image.getWidth (null));
		int height = (int) (zoomSecondaryImage * image.getHeight (null));

		secondaryImage = image.getScaledInstance (width, height, Image.SCALE_SMOOTH);
	}

	public void setIcon (ImageIcon imageIcon) {
		super.setIcon (imageIcon);

		primaryImage = imageIcon.getImage ();
		pW = primaryImage.getWidth (null);
		pH = primaryImage.getHeight (null);

		pri = new Point (0, 0); // Initialize to an arbitrary point
		sW = secondaryImage.getWidth (null);
		sH = secondaryImage.getHeight (null);

		factor = sW / (double) pW;
	}

	@Override
	protected void paintComponent (Graphics g) {
		super.paintComponent (g);

		// Calculate offset between panel and image  
		Rectangle fBounds = getParent ().getBounds ();
		int fW = fBounds.width, fH = fBounds.height;
		int iW = primaryImage.getWidth (null), iH = primaryImage.getHeight (null);
		int Xoffset = (fW - iW) / 2, Yoffset = (fH - iH) / 2;

		// Left side out of bounds
		int Xd = pri.x - 2 * zoom;
		int Yd = pri.y - zoom;
		if (pri.x < 2 * zoom)
			Xd = 0;

		// Right side out of bounds
		int Xe = pri.x + 2 * zoom;
		if (Xe > pW)
			Xd = pW - 4 * zoom;

		// Top side out of bounds
		if (pri.y < 1 * zoom)
			Yd = 0;

		// Bottom side out of bounds
		int Ye = pri.y + 1 * zoom;
		if (Ye > pH)
			Yd = pH - 2 * zoom;
		if (isMouseDragged || isMouseClicked)
			g.drawImage (zoomedInImage, Xd + Xoffset, Yd + Yoffset, null);
	}

	public void getMagicArea (Component frame, MouseEvent e) {
		try {
			pri = e.getPoint ();

			// Calculate offset between panel and image  
			Rectangle fBounds = getParent ().getBounds ();
			int fW = fBounds.width, fH = fBounds.height;
			int iW = primaryImage.getWidth (null), iH = primaryImage.getHeight (null);
			int Xoffset = (fW - iW) / 2, Yoffset = (fH - iH) / 2;

			// Update point with panel offset
			pri.x -= Xoffset;
			pri.y -= Yoffset;

			// Set area dimensions
			int w = 4 * zoom;
			int h = 2 * zoom;
			int Xs = (int) (pri.x * factor);
			int Ys = (int) (pri.y * factor);

			int Xi = Xs - 2 * zoom;
			int Yi = Ys - 1 * zoom;

			// Left side out of bounds
			int Xd = pri.x - 2 * zoom;
			if (Xd < 0)
				Xi = Xi + abs (Xd);

			// Righ side out of bounds
			int Xe = pri.x + 2 * zoom;
			int We = Xe - pW;
			if (Xe > pW)
				Xi = Xi - We;

			// Top side out of bounds
			int Yd = pri.y - 1 * zoom;
			if (Yd < 0)
				Yi = Yi + abs (Yd);

			// Bottom side out of bounds
			int Ye = pri.y + 1 * zoom;
			int He = Ye - pH;
			if (Ye > pH)
				Yi = Yi - He;

			// Create a BufferedImage from Image object
			BufferedImage bufferedImage = new BufferedImage (secondaryImage.getWidth (null), secondaryImage.getHeight (null), BufferedImage.TYPE_INT_ARGB);
			Graphics g = bufferedImage.getGraphics ();
			g.drawImage (secondaryImage, 0, 0, (ImageObserver) null);
			g.dispose ();
			zoomedInImage = bufferedImage.getSubimage (Xi, Yi, w, h);
			frame.repaint ();
		} catch (java.awt.image.RasterFormatException ex) {

		}

	}

	public void addListeners () {
		addMouseMotionListener (new MouseAdapter () {
			@Override
			public void mouseDragged (MouseEvent e) {
				isMouseDragged = true;
				getMagicArea (getParent (), e);
			}
		});
		addMouseListener (new MouseAdapter () {
			@Override
			public void mouseReleased (MouseEvent e) {
				isMouseDragged = false;
				isMouseClicked = false;
				frame.repaint ();
			}

			@Override
			public void mousePressed (MouseEvent e) {
				getMagicArea (frame, e);
				isMouseClicked = true;
				frame.repaint ();
			}
		});
	}
}
