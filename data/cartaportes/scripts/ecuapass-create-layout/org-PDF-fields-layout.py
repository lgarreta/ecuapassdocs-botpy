#!/usr/bin/env python3

layout = open ("fields-layout.txt")
lines = layout.readlines ()

xA, xB, xB1, xB2  = 202, 684, 342, 822
yA                = 31
w1, w2, w3, w3CBox, w4, wCBox2, wCal = 280, 264, 762, 742, 254, 122, 82
h1, H, hTA1  = 20, 23, 46
x, y = xA, yA
c = 1
print ("\n\tpublic void addFields () {\n\t\tremove (imageLabel);")
for l in lines:
	hTmp = 0
	if "#" in l:
		continue
	for t in l.split ():
		h = h1      # Default heigh
		if t == "A1":
			x, w = xA, w1
		elif t == "A2":
			x, w = xA, w2
		elif t == "B1":
			x, w = xB, w1
		elif t == "B2":
			x, w = xB, w2
		elif t == "30":
			y = y + 6
			continue
		elif t == "A3":
			x, w = xA, w3
		elif t == "A4":
			x, w = xA, w4
		elif t == "A5":
			x, w = xA, wCBox2
		elif t == "B5":
			x, w = xB1, wCBox2
		elif t == "C5":
			x, w = xB, wCal
		elif t == "D5":
			x, w = xA, wCal
		elif t == "E5":
			x, w = xB, wCBox2
		elif t == "F5":
			x, w = xB2, wCBox2
		elif t == "TA1":
			x, w, h, hTmp = xA, w3, hTA1, (hTA1 - H + 3)
		elif t == "A3CBox":
			x, w = xA, w3CBox 

			
		#print ("##-- ", t)
		name = "txt%.2d" % c
		if t == "TA1":
			#print (f"\t\tJTextArea {name} = new JTextArea (\"{name}\", 20, 5);", end="\n")
			print (f"\t\tJTextArea {name} = new JTextArea (20, 5);", end="\n")
			print (f"\t\tJScrollPane {name}Scroll = new JScrollPane ({name});", end="")
			print (f"imagePanel.add ({name}Scroll);", end="")
			print (f"{name}Scroll.setBounds ({x}, {y}, {w}, {h});")
		else:
			#print (f"\t\tJTextField {name} = new JTextField (\"{name}\");", end="")
			print (f"\t\tJTextField {name} = new JTextField ();", end="")
			print (f"imagePanel.add ({name});", end="")
			print (f"{name}.setBounds ({x}, {y}, {w}, {h});")
		c += 1

	y = y + H + hTmp
print ("\n\t\timagePanel.add(imageLabel);\n\t\timageLabel.setBounds(0, 0,  964, 1223);\n}")


