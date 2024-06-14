#!/usr/bin/env python3

"""
Create one unique file from from two fles from same extracted ECUAPASS box
"""

import sys

args = sys.argv

file1 = args [1]
file2 = args [2]

lines1 = open (file1, encoding="utf-16le").readlines()
lines2 = open (file2, encoding="utf-16le").readlines()

n1 = len (lines1) 
n2 = len (lines2) 
n  = max (n1, n2)

newFile = open ("joined.txt", "w")
for i in range (n):
	l1 = lines1 [i]
	l2 = lines2 [i]

	line = l1 if l1 != "\n" else l2
	newFile.write (line)

newFile.close ()
