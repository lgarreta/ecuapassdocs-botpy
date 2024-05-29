#!/usr/bin/env python3
import re

def included (labels, text):
	for lb in labels:
		if lb in text:
			return True

layout = open ("fields-layout-declaracion.txt")
lines = layout.readlines ()

x1   = 204
x2   = 687
w1   = 280
w1a   = 260  # Space for find icon
x1b  = 345
x2b  = 826
xr2  = 343
xr3  = 500
wm1  = 95
xm1  = 586
xd2  = 862
ws1  = 137
s1   = 333
s2   = 176
s3   = 302
s4   = 277
h1   = 18
h2   = 66
H    = 23

wr   = 20
wf   = 251
wl1  = 762  # width large
wl1a = 740  # width large with find button
wd1  = 78  # width date

bounds = {}
bounds ["Cb1"]  = [x1, w1, h1] 
bounds ["Cb2"]  = [x2, w1, h1] 
bounds ["Dt1"]  = [x1, wd1, h1] 
bounds ["Dt2"]  = [x2, wd1, h1] 
bounds ["Tx1"]  = [x1, w1, h1] 
bounds ["Tx1a"] = [x1, w1a, h1] 
bounds ["Tx2"]  = [x2, w1, h1] 
bounds ["Tx3a"] = [x1, wl1a, h1] # width find button

bounds ["Tx3"] = [x1, wl1, h1] # width find button
bounds ["Rb1"] = [x1, wr, h1] 
bounds ["Rb2"] = [xr2, wr, h1] 
bounds ["Rb3"] = [xr3, wr, h1] 
bounds ["S1"]  = [0, 0, s1]
bounds ["Cbm"] = [xm1, wm1, h1]
bounds ["Cbs1"] = [x1, ws1, h1]
bounds ["Cbs2"] = [x1b, ws1, h1]
bounds ["Cbs3"] = [x2, ws1, h1]
bounds ["Cbs4"] = [x2b, ws1, h1]
bounds ["TA1"] = [x1, wl1, h2]
bounds ["S2"] = [0, 0, s2]
bounds ["S3"] = [0, 0, s3]
bounds ["S4"] = [0, 0, s4]
bounds ["Tx2b"] = [x2, wf, h1] # width find button

count = 1
y = 103
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

