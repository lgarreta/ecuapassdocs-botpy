package widgets;

import documento.DocModel;
import main.Controller;
import main.Utils;
import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.io.File;
import java.nio.file.Paths;

public final class OrgImageView extends javax.swing.JPanel {
	private Image image;
	Dimension imgDim;

	private ImageIcon imageIcon;
	private JLabel imageLabel;
	private JScrollPane scrollPane;
	private Point lastMousePoint;
	private double scale = 1.0;
	String imgPath;

	public OrgImageView () {
		initComponents ();
	}
	
	private void initComponents () {
		setLayout (new BorderLayout ());
//		this.imgPath = Utils.getResourcePath (this, "images/image-cartaporte-vacia.png");
		this.imgPath = DocModel.runningPath +"/resources/images/image-cartaporte-vacia.png";
		imageIcon = new ImageIcon (imgPath);
		imageLabel = new JLabel (imageIcon);

		image = imageIcon.getImage ();
		scrollPane = new JScrollPane (imageLabel);
		scrollPane.setPreferredSize (new Dimension (850, 600));
		scrollPane.getVerticalScrollBar ().setUnitIncrement (16);
		scrollPane.getHorizontalScrollBar ().setUnitIncrement (16);
		add (scrollPane, BorderLayout.CENTER);
		addListeners ();
	}

	public void addListeners () {;
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
				double scaleFactor = (rotation > 0) ? 0.5 : 1.5;
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
				double scaleFactor = 1.5;
				zoom (scaleFactor, mousePoint);
			}

			private void zoomOut (Point mousePoint) {
				double scaleFactor = 0.5;
				zoom (scaleFactor, mousePoint);
			}

			private void zoom (double scaleFactor, Point mousePoint) {
				Point viewPosition = scrollPane.getViewport ().getViewPosition ();
				double dx = mousePoint.x - viewPosition.getX ();
				double dy = mousePoint.y - viewPosition.getY ();

				scale *= scaleFactor;
				
				viewPosition.setLocation (mousePoint.getX () - dx * scaleFactor, mousePoint.getY () - dy * scaleFactor);
				scrollPane.getViewport ().setViewPosition (viewPosition);
				updateImageSize ();
			}
		};

		imageLabel.addMouseWheelListener (mouseAdapter);
		imageLabel.addMouseListener (mouseAdapter);
		imageLabel.addMouseMotionListener (mouseAdapter);
	}

	public void showImage (File filePath) {
		if ("pdf".equals (Utils.getFileContentType (filePath)))
			filePath = Utils.convertPDFToImage (filePath);
		
		String imagePath = filePath.getPath ();
		imageIcon = new ImageIcon (imagePath);
		image = imageIcon.getImage ();
		imageLabel.setIcon (imageIcon);
		imageLabel.setHorizontalAlignment (SwingConstants.CENTER);
		scale = 1.0;
		imgDim = drawScaledImage ();
		updateImageSize ();
	}

	public Dimension drawScaledImage () {
		scale = 1.0;

		int imgWidth = image.getWidth (null);
		int imgHeight = image.getHeight (null);

		double imgAspect = (double) imgHeight / imgWidth;

		int canvasWidth = getParent ().getWidth ();
		int canvasHeight = getParent ().getHeight ();
		double canvasAspect = (double) canvasHeight / canvasWidth;

		double x1 = 0, y1 = 0, x2 = 0, y2 = 0; // top left bottom right positions

		if (imgWidth < canvasWidth && imgHeight < canvasHeight) {
			// the image is smaller than the canvas
			x1 = (canvasWidth - imgWidth) / 2;
			y1 = (canvasHeight - imgHeight) / 2;
			x2 = imgWidth + x1;
			y2 = imgHeight + y1;
		} else {
			if (canvasAspect > imgAspect) {
				y1 = canvasHeight;
				// keep image aspect ratio
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
//		imageLabel.setIcon (new ImageIcon (image.getScaledInstance ((int) (x2 - x1), (int) (y2 - y1), Image.SCALE_DEFAULT)));
		return (new Dimension ((int) (x2 - x1), (int) (y2 - y1)));
	}

	private void updateImageSize () {
		int width = (int) (imgDim.width * scale);
		int height = (int) (imgDim.height * scale);
		imageIcon.setImage (image.getScaledInstance (width, height, Image.SCALE_DEFAULT));
		imageLabel.setIcon (imageIcon);
	}

	public static void main (String[] args) {
		OrgImageView imgPanel = new OrgImageView ();
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
