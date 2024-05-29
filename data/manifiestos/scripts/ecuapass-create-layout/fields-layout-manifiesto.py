#!/usr/bin/env python3
import re

def included (labels, text):
	for lb in labels:
		if lb in text:
			return True

layout = open ("fields-layout-manifiesto.txt")
lines = layout.readlines ()

x1   = 202
x2   = 684
w1   = 280
x1b  = 345
x2b  = 826
xr2  = 343
xr3  = 500
wm1  = 95
xm1  = 586
xd2  = 862
ws1  = 137
s1   = 0
s2   = 176
s3   = 302
s4   = 277
h1   = 20
h2   = 66
H    = 23

wr   = 20
wf   = 251
wl1  = 762  # width large
wd1  = 78  # width date

bounds = {}
bounds ["Cb1"] = [x1, w1, h1] 
bounds ["Cb2"] = [x2, w1, h1] 
bounds ["Dt1"] = [x1, wd1, h1] 
bounds ["Tx1"] = [x1, w1, h1] 
bounds ["Tx2"] = [x2, w1, h1] # width find button
bounds ["Rb1"] = [x1, wr, h1] 
bounds ["Rb2"] = [xr2, wr, h1] 
bounds ["Rb3"] = [xr3, wr, h1] 
bounds ["S1"]  = [0, 0, s1]
bounds ["Cbm"] = [xm1, wm1, h1]
bounds ["Dt2"] = [xd2, wd1, h1] 
bounds ["Cbs1"] = [x1, ws1, h1]
bounds ["Cbs2"] = [x1b, ws1, h1]
bounds ["Cbs3"] = [x2, ws1, h1]
bounds ["Cbs4"] = [x2b, ws1, h1]
bounds ["TA1"] = [x1, wl1, h2]
bounds ["S2"] = [0, 0, s2]
bounds ["S3"] = [0, 0, s3]
bounds ["S4"] = [0, 0, s4]
bounds ["Tx2b"] = [x2, wf, h1] # width find button
bounds ["Tx3"] = [x1, wl1, h1] # width find button

count = 1
y = 126
print ("\n\tpublic ArrayList <Component> getInputTextFields () {")
print ("\t\tArrayList <Component> imagePanel = new ArrayList <> ();")
for l in lines:
	offset = 0
	l = l.strip()
	#print (">>> Line: ", l)
	if l == "":
		continue

	if l[0] == "#":
		#print (f"\n\t\t//{l.split('#')[1]}")
		continue

	for element in l.split ():
		name = "txt%.2d" % count
		if "#" in element:
			continue

		if "Cb" in element:
			#print (f">>> Elements: {element}")
			filename  = element.split (":")[1]
			element   = element.split (":")[0]
			if "derivado" in filename:
				print (f"\t\tSearchableComboBox {name} = createComboBox (\"{filename}\", {previousVar});", end="")
			else:
				print (f"\t\tSearchableComboBox {name} = createComboBox (\"{filename}\");", end="")
		elif "Rb" in element:
			print ("\t\tJRadioButton r1 = new JRadioButton ();", end=" ")
			print ("JRadioButton r2 = new JRadioButton ();", end=" ")
			print ("JRadioButton r3 = new JRadioButton ();")
			print (f"\t\tButtonGroup rg = new ButtonGroup ();")
			print (f"\t\trg.add (r1); rg.add (r2); rg.add (r3);")
			name = "txt%.2d" % count
			print (f"\t\timagePanel.add (r1);", end="")
			print (f"\t\tr1.setBounds ({bounds ['Rb1'][0]}, {y}, {bounds['Rb1'][1]}, {bounds['Rb1'][2]});")
			count += 1
			name = "txt%.2d" % count
			print (f"\t\timagePanel.add (r2);", end="")
			print (f"\t\tr2.setBounds ({bounds ['Rb2'][0]}, {y}, {bounds['Rb2'][1]}, {bounds['Rb2'][2]});")
			count += 1
			name = "txt%.2d" % count
			print (f"\t\timagePanel.add (r3);", end="")
			print (f"\t\tr3.setBounds ({bounds ['Rb3'][0]}, {y}, {bounds['Rb3'][1]}, {bounds['Rb3'][2]});")
			count += 1
			break
			
		elif "TA1" in element:
			print (f"\t\tJScrollPane {name} = new JScrollPane (new JTextArea (2,40));", end="")
			offset = 45
		elif "S" in element:
			offset = bounds [element][2]
			break
		else:
			print (f"\t\tJTextField {name} = new JTextField ();", end="")

		x, w, h = bounds [element][0], bounds[element][1], bounds[element][2] 

		print (f"imagePanel.add ({name});", end="")
		print (f"{name}.setBounds ({x}, {y}, {w}, {h});")
		count +=1
		previousVar = name

	y = y + H + offset
print ("\n\t\treturn imagePanel;\n\t}")


#xA, xB, xB1, xB2  = 202, 684, 342, 825
#yA                = 31
#w1, w2, w3, w3CBox, wSb, wCal = 280, 264, 762, 742, 138, 82
#h1, H, hTA1  = 20, 23, 46
#x, y = xA, yA
#count = 1
#print ("\n\tpublic void addFields () {\n\t\tremove (imageLabel);")
#for l in lines:
#	hTmp = 0
#	for t in l.split ():
#		if "#" in t:
#			break           # An end comment
#		h = h1              # Default heigh
#		if "Tx1" in t or "Cb1" in t:
#			x, w = xA, w1
#		elif "Tx2" in t or "Cb2" in t:
#			x, w = xB, w1
#		elif t == "S1":
#			y = y + 0
#			continue
#		elif t == "Tx3":
#			x, w = xA, w3
#		elif "Sb1" in t:
#			x, w = xA, wSb
#		elif "Sb2" in t:
#			x, w = xB1, wSb
#		elif t == "C5":
#			x, w = xB, wCal
#		elif "Sb3" in t:     # Fecha at the end
#			x, w = xB, wCal
#		elif "Sb4" in t:     # Fecha at the beginning
#			x, w = xA, wCal
#		elif "Sb5" in t:     # Pais at the middle
#			x, w = xB, wSb
#		elif "Sb6" in t:     # Ciudad at the end
#			x, w = xB2, wSb
#		elif t == "TA1":
#			x, w, h, hTmp = xA, w3, hTA1, (hTA1 - H + 1)
#		elif t == "Lb1":
#			x, w = xA, w3CBox 
#
#			
#		#print ("##-- ", t)
#		name = "txt%.2d" % count
#		if t == "TA1":
#			print (f"\t\tJScrollPane {name} = new JScrollPane (new JTextArea (2,40));", end="")
#		elif included (["Cb1","Cb2","Sb1","Sb2","Sb5", "Sb6"], t) and ":" in t:   # ComboBox 
#			filename = t.split (":")[1]
#			if filename == "derivado":
#				print (f"\t\tSearchableComboBox {name} = createComboBox (\"{filename}\", {previousVar});", end="")
#			else:
#				print (f"\t\tSearchableComboBox {name} = createComboBox (\"{filename}\");", end="")
#		else:
#			#print (f"\t\tJTextField {name} = new JTextField (\"{name}\");", end="")
#			print (f"\t\tJTextField {name} = new JTextField ();", end="")
#
#		print (f"imagePanel.add ({name});", end="")
#		print (f"{name}.setBounds ({x}, {y}, {w}, {h});")
#
#		count += 1
#		previousVar = name
#
#	y = y + H + hTmp
#print ("\n\t\timagePanel.add(imageLabel);\n\t\timageLabel.setBounds(0, 0,  size.width, size.height);\n\t}")
#
#
