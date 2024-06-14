#!/usr/bin/env python3

def included (labels, text):
	for lb in labels:
		if lb in text:
			return True

layout = open ("fields-layout-cartaporte.txt")
lines = layout.readlines ()

xA, xB, xB1, xB2  = 202, 684, 342, 825
yA                = 31
w1, w2, w3, w3CBox, wSb, wCal = 280, 264, 762, 742, 138, 82
h1, H, hTA1  = 20, 23, 46
x, y = xA, yA
count = 1
print ("\n\tpublic void addFields () {\n\t\tremove (imageLabel);")
for l in lines:
	hTmp = 0
	for t in l.split ():
		if "#" in t:
			break           # An end comment
		h = h1              # Default heigh
		if "Tx1" in t or "Cb1" in t:
			x, w = xA, w1
		elif "Tx2" in t or "Cb2" in t:
			x, w = xB, w1
		elif t == "S1":
			y = y + 0
			continue
		elif t == "Tx3":
			x, w = xA, w3
		elif "Sb1" in t:
			x, w = xA, wSb
		elif "Sb2" in t:
			x, w = xB1, wSb
		elif t == "C5":
			x, w = xB, wCal
		elif "Sb3" in t:     # Fecha at the end
			x, w = xB, wCal
		elif "Sb4" in t:     # Fecha at the beginning
			x, w = xA, wCal
		elif "Sb5" in t:     # Pais at the middle
			x, w = xB, wSb
		elif "Sb6" in t:     # Ciudad at the end
			x, w = xB2, wSb
		elif t == "TA1":
			x, w, h, hTmp = xA, w3, hTA1, (hTA1 - H + 1)
		elif t == "Lb1":
			x, w = xA, w3CBox 

			
		#print ("##-- ", t)
		name = "txt%.2d" % count
		if t == "TA1":
			print (f"\t\tJScrollPane {name} = new JScrollPane (new JTextArea (2,40));", end="")
		elif included (["Cb1","Cb2","Sb1","Sb2","Sb5", "Sb6"], t) and ":" in t:   # ComboBox 
			filename = t.split (":")[1]
			if filename == "derivado":
				print (f"\t\tSearchableComboBox {name} = createComboBox (\"{filename}\", {previousVar});", end="")
			else:
				print (f"\t\tSearchableComboBox {name} = createComboBox (\"{filename}\");", end="")
		else:
			#print (f"\t\tJTextField {name} = new JTextField (\"{name}\");", end="")
			print (f"\t\tJTextField {name} = new JTextField ();", end="")

		print (f"imagePanel.add ({name});", end="")
		print (f"{name}.setBounds ({x}, {y}, {w}, {h});")

		count += 1
		previousVar = name

	y = y + H + hTmp
print ("\n\t\timagePanel.add(imageLabel);\n\t\timageLabel.setBounds(0, 0,  size.width, size.height);\n\t}")


